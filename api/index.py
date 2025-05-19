from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel
import httpx
import decimal

app = FastAPI(
    title="Exsat Verification API",
    description="A API for TaskOn task verification integration",
    version="1.0.0",
)

# Add CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class VerificationResponse(BaseModel):
    result: dict = {"isValid": bool}
    error: Optional[str] = None

@app.get(
    "/api/task/verification",
    response_model=VerificationResponse,
    summary="Verify Task Completion",
    description="Verify if a user has completed the task based on their wallet address or social media ID",
)
async def verify_task(
    address: str,
    authorization: Optional[str] = Header(None)
) -> VerificationResponse:
    # Convert address to lowercase for case-insensitive comparison
    address = address.lower()
    
    # Obtain the token balance from the exsat network API
    try:
        api_url = f"https://scan.exsat.network/api?module=account&action=tokenbalance&contractaddress=0x8266f2fbc720012e5Ac038aD3dbb29d2d613c459&address={address}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            data = response.json()
            
            if data["status"] == "1":
                balance = decimal.Decimal(data["result"]) / decimal.Decimal(10**18)
                is_valid = balance >= 1
                return VerificationResponse(result={"isValid": is_valid}, error=None)
            else:
                return VerificationResponse(
                    result={"isValid": False}, 
                    error=f"API Error: {data.get('message', 'Unknown error')}"
                )
    except Exception as e:
        return VerificationResponse(result={"isValid": False}, error=f"Error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Welcome to Exsat TaskOn Verification API"}