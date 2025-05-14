from fastapi import FastAPI, HTTPException
import httpx
from fastapi.responses import Response
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fun with Flags API")

# Constants
FLAG_URL = "https://flagcdn.com/16x12/ua.png"

@app.get("/flag1")
async def get_flag1():
    """
    Endpoint to fetch the flag from the first URL
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(FLAG_URL)
            if response.status_code == 200:
                return Response(content=response.content, media_type="image/png")
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch flag")
    except Exception as e:
        logger.error(f"Error fetching flag1: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/flag2")
async def get_flag2():
    """
    Endpoint to fetch the flag from the second URL
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(FLAG_URL)
            if response.status_code == 200:
                return Response(content=response.content, media_type="image/png")
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch flag")
    except Exception as e:
        logger.error(f"Error fetching flag2: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/webhook")
async def webhook(request: dict):
    """
    Webhook endpoint that can be exposed via ngrok
    """
    try:
        logger.info(f"Received webhook data")
        if request['type'] == 'text':
            logger.info(f"Received text response")
        
        if request['type'] == 'button_response':
            logger.info(f"Received button response")
        
        return {"status": "success", "message": "Webhook received", "data": request}
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 