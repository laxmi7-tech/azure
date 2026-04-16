"""
AzureScope — Full Stack Cost Monitor
FastAPI Backend: Login · Azure Connect · Cost & Amortized Cost
"""
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx
import os
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# ─── App Setup ────────────────────────────────────────────────────────────────
app = FastAPI(title="AzureScope Cost Monitor")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")
from jinja2 import Environment, FileSystemLoader

_jinja_env = Environment(loader=FileSystemLoader("templates"), auto_reload=True)
_jinja_env.cache = {}  # simple dict cache, avoids LRUCache unhashable issue

class _Templates:
    def TemplateResponse(self, name, context):
        from fastapi.responses import HTMLResponse
        t = _jinja_env.get_template(name)
        return HTMLResponse(t.render(**context))

templates = _Templates()

# ─── Single User Credentials ──────────────────────────────────────────────────
APP_USERNAME = "azureadmin"
APP_PASSWORD = "AzureScope@2024"

# ─── In-Memory Session Store ──────────────────────────────────────────────────
sessions: dict = {}          # token → username
azure_creds: dict = {}       # token → {tenant_id, client_id, client_secret, subscription_id}
access_tokens: dict = {}     # token → azure_access_token

# ─── Pydantic Models ──────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class AzureConnectRequest(BaseModel):
    tenant_id: str
    client_id: str
    client_secret: str
    subscription_id: str
    session_token: str

class CostRequest(BaseModel):
    session_token: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

# ─── Helper: get session token from request ───────────────────────────────────
def get_session(request: Request) -> Optional[str]:
    return request.cookies.get("session_token")

# ─── PAGE ROUTES ──────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    token = request.cookies.get("session_token")
    if token and token in sessions:
        return RedirectResponse("/connect", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/connect", response_class=HTMLResponse)
def connect_page(request: Request):
    token = request.cookies.get("session_token")
    if not token or token not in sessions:
        return RedirectResponse("/", status_code=302)
    connected = token in azure_creds
    return templates.TemplateResponse("connect.html", {
        "request": request,
        "connected": connected,
        "creds": azure_creds.get(token, {})
    })

@app.get("/costs", response_class=HTMLResponse)
def costs_page(request: Request):
    token = request.cookies.get("session_token")
    if not token or token not in sessions:
        return RedirectResponse("/", status_code=302)
    if token not in azure_creds:
        return RedirectResponse("/connect", status_code=302)
    return templates.TemplateResponse("costs.html", {"request": request})

@app.get("/logout")
def logout(request: Request):
    token = request.cookies.get("session_token")
    if token:
        sessions.pop(token, None)
        azure_creds.pop(token, None)
        access_tokens.pop(token, None)
    resp = RedirectResponse("/", status_code=302)
    resp.delete_cookie("session_token")
    return resp

# ─── API ROUTES ───────────────────────────────────────────────────────────────

@app.post("/api/login")
async def api_login(req: LoginRequest):
    if req.username.strip() == APP_USERNAME and req.password == APP_PASSWORD:
        import secrets
        token = secrets.token_hex(32)
        sessions[token] = req.username
        resp = JSONResponse({"success": True, "message": "Login successful"})
        resp.set_cookie(
            key="session_token", value=token,
            httponly=True, max_age=86400, samesite="lax"
        )
        return resp
    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.post("/api/azure/connect")
async def azure_connect(req: AzureConnectRequest):
    """Validate Azure credentials by fetching an OAuth2 access token."""
    token = req.session_token
    if token not in sessions:
        raise HTTPException(status_code=401, detail="Session expired")

    # Validate fields
    for field in [req.tenant_id, req.client_id, req.client_secret, req.subscription_id]:
        if not field or not field.strip():
            raise HTTPException(status_code=400, detail="All Azure credential fields are required")

    # Attempt to get Azure access token
    url = f"https://login.microsoftonline.com/{req.tenant_id.strip()}/oauth2/v2.0/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": req.client_id.strip(),
        "client_secret": req.client_secret.strip(),
        "scope": "https://management.azure.com/.default"
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(url, data=payload)
        data = r.json()
        if "access_token" not in data:
            err = data.get("error_description", data.get("error", "Authentication failed"))
            raise HTTPException(status_code=400, detail=f"Azure auth failed: {err}")

        # Store credentials and access token
        azure_creds[token] = {
            "tenant_id": req.tenant_id.strip(),
            "client_id": req.client_id.strip(),
            "client_secret": req.client_secret.strip(),
            "subscription_id": req.subscription_id.strip(),
        }
        access_tokens[token] = data["access_token"]
        return {"success": True, "message": "Connected to Azure successfully"}

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Network error connecting to Azure: {str(e)}")


async def _get_azure_token(session_token: str) -> str:
    """Return cached Azure access token or refresh it."""
    creds = azure_creds.get(session_token)
    if not creds:
        raise HTTPException(status_code=401, detail="Azure not connected")

    # Re-fetch token (tokens expire in 1 hour; for simplicity, always refresh)
    url = f"https://login.microsoftonline.com/{creds['tenant_id']}/oauth2/v2.0/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "scope": "https://management.azure.com/.default"
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(url, data=payload)
    data = r.json()
    if "access_token" not in data:
        raise HTTPException(status_code=401, detail="Azure token refresh failed")
    return data["access_token"]


@app.get("/api/costs/actual")
async def get_actual_costs(request: Request, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Pull ACTUAL cost from Azure Cost Management API."""
    token = request.cookies.get("session_token")
    if not token or token not in sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if token not in azure_creds:
        raise HTTPException(status_code=400, detail="Azure not connected")

    creds = azure_creds[token]
    az_token = await _get_azure_token(token)
    sub_id = creds["subscription_id"]

    # Default: current month
    if not start_date:
        start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    url = (
        f"https://management.azure.com/subscriptions/{sub_id}"
        f"/providers/Microsoft.CostManagement/query?api-version=2023-11-01"
    )
    body = {
        "type": "ActualCost",
        "dataSet": {
            "granularity": "Daily",
            "aggregation": {
                "totalCost": {"name": "Cost", "function": "Sum"},
                "totalCostUSD": {"name": "CostUSD", "function": "Sum"}
            },
            "grouping": [{"type": "Dimension", "name": "ServiceName"}],
            "sorting": [{"direction": "Descending", "name": "Cost"}]
        },
        "timeframe": "Custom",
        "timePeriod": {"from": f"{start_date}T00:00:00+00:00", "to": f"{end_date}T23:59:59+00:00"}
    }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            url,
            json=body,
            headers={"Authorization": f"Bearer {az_token}", "Content-Type": "application/json"}
        )

    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=f"Azure API error: {r.text[:300]}")

    data = r.json()
    return _transform_cost_response(data, "ActualCost", start_date, end_date)


@app.get("/api/costs/amortized")
async def get_amortized_costs(request: Request, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Pull AMORTIZED cost from Azure Cost Management API."""
    token = request.cookies.get("session_token")
    if not token or token not in sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if token not in azure_creds:
        raise HTTPException(status_code=400, detail="Azure not connected")

    creds = azure_creds[token]
    az_token = await _get_azure_token(token)
    sub_id = creds["subscription_id"]

    if not start_date:
        start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    url = (
        f"https://management.azure.com/subscriptions/{sub_id}"
        f"/providers/Microsoft.CostManagement/query?api-version=2023-11-01"
    )
    body = {
        "type": "AmortizedCost",
        "dataSet": {
            "granularity": "Daily",
            "aggregation": {
                "totalCost": {"name": "Cost", "function": "Sum"},
                "totalCostUSD": {"name": "CostUSD", "function": "Sum"}
            },
            "grouping": [{"type": "Dimension", "name": "ServiceName"}],
            "sorting": [{"direction": "Descending", "name": "Cost"}]
        },
        "timeframe": "Custom",
        "timePeriod": {"from": f"{start_date}T00:00:00+00:00", "to": f"{end_date}T23:59:59+00:00"}
    }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            url,
            json=body,
            headers={"Authorization": f"Bearer {az_token}", "Content-Type": "application/json"}
        )

    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=f"Azure API error: {r.text[:300]}")

    data = r.json()
    return _transform_cost_response(data, "AmortizedCost", start_date, end_date)


@app.get("/api/costs/summary")
async def get_cost_summary(request: Request):
    """Return both actual + amortized summary side-by-side."""
    token = request.cookies.get("session_token")
    if not token or token not in sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if token not in azure_creds:
        raise HTTPException(status_code=400, detail="Azure not connected")

    start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")

    # Last month for comparison
    last_month_end = datetime.now().replace(day=1) - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    creds = azure_creds[token]
    az_token = await _get_azure_token(token)
    sub_id = creds["subscription_id"]

    async def fetch_total(cost_type: str, start: str, end: str) -> float:
        url = (
            f"https://management.azure.com/subscriptions/{sub_id}"
            f"/providers/Microsoft.CostManagement/query?api-version=2023-11-01"
        )
        body = {
            "type": cost_type,
            "dataSet": {
                "granularity": "None",
                "aggregation": {"totalCost": {"name": "Cost", "function": "Sum"}}
            },
            "timeframe": "Custom",
            "timePeriod": {"from": f"{start}T00:00:00+00:00", "to": f"{end}T23:59:59+00:00"}
        }
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                url, json=body,
                headers={"Authorization": f"Bearer {az_token}", "Content-Type": "application/json"}
            )
        if r.status_code != 200:
            return 0.0
        d = r.json()
        rows = d.get("properties", {}).get("rows", [])
        return round(rows[0][0], 2) if rows else 0.0

    actual_curr = await fetch_total("ActualCost", start_date, end_date)
    amort_curr = await fetch_total("AmortizedCost", start_date, end_date)
    actual_last = await fetch_total("ActualCost", last_month_start.strftime("%Y-%m-%d"), last_month_end.strftime("%Y-%m-%d"))
    amort_last = await fetch_total("AmortizedCost", last_month_start.strftime("%Y-%m-%d"), last_month_end.strftime("%Y-%m-%d"))

    def pct_change(curr, prev):
        if prev == 0: return 0
        return round((curr - prev) / prev * 100, 1)

    return {
        "actual": {
            "current_month": actual_curr,
            "last_month": actual_last,
            "change_pct": pct_change(actual_curr, actual_last)
        },
        "amortized": {
            "current_month": amort_curr,
            "last_month": amort_last,
            "change_pct": pct_change(amort_curr, amort_last)
        },
        "period": {"start": start_date, "end": end_date},
        "subscription_id": sub_id
    }


@app.get("/api/session/token")
def session_token_endpoint(request: Request):
    """Return the session token for frontend use in API calls that need it in body."""
    token = request.cookies.get("session_token")
    if not token or token not in sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"token": token}


@app.get("/api/session/status")
def session_status(request: Request):
    token = request.cookies.get("session_token")
    if not token or token not in sessions:
        return {"authenticated": False}
    return {
        "authenticated": True,
        "username": sessions[token],
        "azure_connected": token in azure_creds,
        "subscription_id": azure_creds.get(token, {}).get("subscription_id", "")
    }


def _transform_cost_response(data: dict, cost_type: str, start_date: str, end_date: str) -> dict:
    """Transform Azure Cost Management API response into clean structure."""
    props = data.get("properties", {})
    columns = [c["name"] for c in props.get("columns", [])]
    rows = props.get("rows", [])

    # Build per-service totals
    service_totals: dict = {}
    daily_totals: dict = {}

    for row in rows:
        row_dict = dict(zip(columns, row))
        cost = float(row_dict.get("Cost", row_dict.get("cost", 0)))
        date_val = str(row_dict.get("UsageDate", row_dict.get("BillingMonth", "")))
        service = str(row_dict.get("ServiceName", row_dict.get("serviceName", "Unknown")))
        currency = row_dict.get("Currency", "USD")

        if service not in service_totals:
            service_totals[service] = 0.0
        service_totals[service] += cost

        if date_val not in daily_totals:
            daily_totals[date_val] = 0.0
        daily_totals[date_val] += cost

    total = sum(service_totals.values())

    # Top services
    top_services = sorted(
        [{"service": k, "cost": round(v, 2), "pct": round(v / total * 100, 1) if total > 0 else 0}
         for k, v in service_totals.items()],
        key=lambda x: x["cost"], reverse=True
    )[:15]

    # Daily trend sorted
    daily_sorted = sorted(
        [{"date": k, "cost": round(v, 2)} for k, v in daily_totals.items()],
        key=lambda x: x["date"]
    )

    return {
        "cost_type": cost_type,
        "total": round(total, 2),
        "currency": "USD",
        "period": {"start": start_date, "end": end_date},
        "top_services": top_services,
        "daily_trend": daily_sorted,
        "service_count": len(service_totals)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
