import os
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from typing import Optional
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# GET YOUR NGROK URL FROM ENV OR PASTE IT HERE
NGROK_URL = os.environ.get("TARGET_URL")


app = FastAPI()

# Enable CORS so Azure can reach the endpoint
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock database: Note the jump between user 2 and 99
MOCK_DB = {
    "1": {"username": "alice", "email": "alice@example.com", "role": "user"},
    "2": {"username": "bob", "email": "bob@example.com", "role": "user"},
    "99": {"username": "admin_sys", "email": "admin@internal.corp", "role": "admin", "secret_key": "HACK_ME_IF_YOU_CAN_2026"}
}

@app.get("/", operation_id="get_health")
def health_check():
    return {"status": "online", "message": "Legacy System v1.0.4"}

# BUG 1: Predictable IDOR (Insecure Direct Object Reference)
# The agent should notice user 1 and 2 exist, then try to "fuzz" or guess user 99.
@app.get("/api/v1/users/{user_id}", operation_id="get_user_profile")
def get_user_profile(user_id: str):
    user = MOCK_DB.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# BUG 2: Hidden Debug Endpoint
# The Recon Agent should find this by looking at the Swagger docs (/docs) 
# or by searching for "debug" strings.
@app.get("/debug/config-dump", operation_id="dump_config")
def dump_config(x_admin_bypass: Optional[str] = Header(None)):
    """
    INTERNAL USE ONLY. This endpoint dumps system environment variables.
    """
    if x_admin_bypass == "true": # A very weak security check
        return {"env": os.environ.get("HOSTNAME", "azure-vm-01"), "database": "prod-db-internal.local"}
    return {"error": "Access Denied. Internal IP required."}

# BUG 3: Info Leak in Headers
# The agent can see the 'X-Powered-By' header to identify old tech versions.
@app.get("/api/v1/system/version", operation_id="get_version")
def get_version():
    return {"version": "1.0.4", "built": "2023-10-12"}

@app.get("/admin/debug", operation_id="get_admin_debug")
def debug(x_admin_bypass: str = Header(None)):
    if x_admin_bypass == "true":
        return {"system_logs": "Internal database accessed via debug mode."}
    return {"error": "Unauthorized"}

# FORCE OPENAPI 3.0.1 (Fixes the "Invalid Schema" error)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Aegis Vulnerable API",
        version="1.0.0",
        openapi_version="3.0.1", # CRITICAL: Azure requires 3.0.x
        description="A legacy API with deliberate security flaws.",
        routes=app.routes,
    )
    # Ensure the server points to NGROK, not localhost
    openapi_schema["servers"] = [{"url": NGROK_URL}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)