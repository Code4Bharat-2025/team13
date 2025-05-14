from fastapi import FastAPI, HTTPException
import httpx
from fastapi.responses import Response
import logging
import os
from dotenv import load_dotenv
import random
from typing import Dict, List
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fun with Flags API")

# Constants
FLAG_BASE_URL = "https://flagcdn.com/16x12/"
SWIFTCHAT_API_URL = "https://v1-api.swiftchat.ai/api/bots/"

# Game state storage (in-memory for demonstration)
# In production, use a proper database
user_states: Dict[str, dict] = {}

# Country lists for different difficulty levels
BEGINNER_COUNTRIES = ['us', 'gb', 'fr', 'de', 'it', 'es', 'jp', 'cn', 'in', 'br']
HARD_COUNTRIES = ['kz', 'uz', 'mm', 'la', 'np', 'bt', 'mv', 'bn', 'tl', 'kh']

# Pydantic model for webhook request
class WebhookRequest(BaseModel):
    from_: str = None
    text: str = None
    
    class Config:
        allow_population_by_field_name = True
        fields = {
            'from_': 'from'
        }

async def send_message_with_flag(recipient_mobile: str, country_code: str, options: List[str]):
    """
    Send a flag image with multiple choice options
    """
    bot_id = os.getenv('BOT_ID')
    api_key = os.getenv('API_KEY')
    
    if not bot_id or not api_key:
        logger.error(f"Missing credentials - BOT_ID exists: {bool(bot_id)}, API_KEY exists: {bool(api_key)}")
        raise HTTPException(status_code=500, detail="Missing API credentials")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": recipient_mobile,
        "type": "button",
        "button": {
            "body": {
                "type": "image",
                "image": {
                    "url": f"https://flagcdn.com/96x72/{country_code}.png",
                    "body": "🌎 Which country does this flag belong to?"
                }
            },
            "buttons": [
                {"type": "solid", "body": option, "reply": option}
                for option in options
            ],
            "allow_custom_response": False
        }
    }

    try:
        logger.debug(f"Sending flag message to {recipient_mobile} with payload: {payload}")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SWIFTCHAT_API_URL}{bot_id}/messages",
                headers=headers,
                json=payload
            )
            logger.debug(f"Flag message API response: {response.status_code} - {response.text}")
            if response.status_code not in [200, 201]:
                logger.error(f"SwiftChat API error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to send flag question: {response.text}"
                )
    except Exception as e:
        logger.error(f"Error sending flag question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def send_difficulty_buttons(recipient_mobile: str):
    """
    Send difficulty level buttons to the user
    """
    bot_id = os.getenv('BOT_ID')
    api_key = os.getenv('API_KEY')
    
    if not bot_id or not api_key:
        logger.error(f"Missing credentials - BOT_ID exists: {bool(bot_id)}, API_KEY exists: {bool(api_key)}")
        raise HTTPException(status_code=500, detail="Missing API credentials")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": recipient_mobile,
        "type": "button",
        "button": {
            "body": {
                "type": "text",
                "text": {
                    "body": "Choose your difficulty level for the flag quiz!"
                }
            },
            "buttons": [
                {
                    "type": "solid",
                    "body": "Beginner",
                    "reply": "beginner"
                },
                {
                    "type": "solid",
                    "body": "Hard",
                    "reply": "hard"
                }
            ],
            "allow_custom_response": False
        }
    }

    try:
        logger.debug(f"Sending difficulty buttons to {recipient_mobile} with payload: {payload}")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SWIFTCHAT_API_URL}{bot_id}/messages",
                headers=headers,
                json=payload
            )
            logger.debug(f"Difficulty API response: {response.status_code} - {response.text}")
            if response.status_code in [200, 201]:
                # Initialize user state
                user_states[recipient_mobile] = {
                    "state": "awaiting_difficulty",
                    "score": 0,
                    "questions_asked": 0
                }
                return {"status": "success", "message": "Difficulty options sent"}
            else:
                logger.error(f"SwiftChat API error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to send difficulty options: {response.text}"
                )
    except Exception as e:
        logger.error(f"Error sending difficulty options: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def send_game_over(recipient_mobile: str, score: int, total: int):
    """
    Send game over message with final score
    """
    bot_id = os.getenv('BOT_ID')
    api_key = os.getenv('API_KEY')
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": recipient_mobile,
        "type": "button",
        "button": {
            "body": {
                "type": "text",
                "text": {
                    "body": f"🎮 Game Over!\n\nYour score: {score}/{total}\n\nWould you like to play again?"
                }
            },
            "buttons": [
                {
                    "type": "solid",
                    "body": "Play Again",
                    "reply": "play_again"
                }
            ],
            "allow_custom_response": False
        }
    }

    try:
        logger.debug(f"Sending game over message to {recipient_mobile} with payload: {payload}")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SWIFTCHAT_API_URL}{bot_id}/messages",
                headers=headers,
                json=payload
            )
            logger.debug(f"Game over API response: {response.status_code} - {response.text}")
            if response.status_code not in [200, 201]:
                logger.error(f"SwiftChat API error: {response.text}")
    except Exception as e:
        logger.error(f"Error sending game over message: {str(e)}")

@app.post("/start-quiz/{recipient_mobile}")
async def start_quiz(recipient_mobile: str):
    """
    Start the quiz by sending difficulty options
    """
    logger.info(f"Starting quiz for mobile: {recipient_mobile}")
    return await send_difficulty_buttons(recipient_mobile)

@app.get("/flag/{country_code}")
async def get_flag(country_code: str):
    """
    Endpoint to fetch a flag by country code
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FLAG_BASE_URL}{country_code}.png")
            if response.status_code == 200:
                return Response(content=response.content, media_type="image/png")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch flag"
                )
    except Exception as e:
        logger.error(f"Error fetching flag: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/webhook")
async def webhook(request: dict):
    """
    Webhook endpoint to handle user responses
    """
    try:
        logger.debug(f"Received webhook data: {request}")
        
        # Extract mobile number and response
        mobile = request.get("from")
        
        # Handle both button responses and text messages
        if request['type'] == 'button_response':
            # This is a button response
            response = request["button_response"]['body']
        elif "text" in request and isinstance(request["text"], dict):
            # This is a text message with body
            response = request["text"].get("body", "").lower()
        elif "text" in request:
            # This is a plain text message
            response = request["text"].lower()
        else:
            logger.error("No valid response found in webhook data")
            raise HTTPException(status_code=400, detail="Invalid webhook format")
        
        logger.info(f"Processing webhook for mobile: {mobile}, response: {response}")
        
        if not mobile:
            logger.error("No mobile number in webhook request")
            raise HTTPException(status_code=400, detail="Missing mobile number")
            
        if not response:
            logger.error("No response text in webhook request")
            raise HTTPException(status_code=400, detail="Missing response text")

        if mobile not in user_states:
            logger.info(f"New user {mobile}, starting fresh game")
            return await send_difficulty_buttons(mobile)

        user_state = user_states[mobile]
        logger.debug(f"Current user state: {user_state}")
        
        if user_state["state"] == "awaiting_difficulty":
            # Handle difficulty selection
            if response == "beginner":
                countries = BEGINNER_COUNTRIES
            elif response == "hard":
                countries = HARD_COUNTRIES
            else:
                logger.error(f"Invalid difficulty: {response}")
                return {"status": "error", "message": "Invalid difficulty"}

            # Set up the game
            user_state.update({
                "state": "playing",
                "difficulty": response,
                "countries": countries.copy(),
                "current_country": None,
                "score": 0,
                "questions_asked": 0
            })

            # Send first question
            country = random.choice(user_state["countries"])
            user_state["current_country"] = country
            user_state["countries"].remove(country)
            
            # Generate options (1 correct + 3 random from the same difficulty)
            options = random.sample([c for c in countries if c != country], 3)
            options.append(country)
            random.shuffle(options)
            
            await send_message_with_flag(mobile, country, options)
            
        elif user_state["state"] == "playing":
            # Handle answer
            if response == user_state["current_country"]:
                user_state["score"] += 1
            
            user_state["questions_asked"] += 1
            
            # Check if game should continue
            if user_state["questions_asked"] >= 5 or not user_state["countries"]:
                # Game over
                await send_game_over(mobile, user_state["score"], user_state["questions_asked"])
                user_states[mobile]["state"] = "game_over"
            else:
                # Send next question
                country = random.choice(user_state["countries"])
                user_state["current_country"] = country
                user_state["countries"].remove(country)
                
                # Generate options
                all_countries = BEGINNER_COUNTRIES if user_state["difficulty"] == "beginner" else HARD_COUNTRIES
                options = random.sample([c for c in all_countries if c != country], 3)
                options.append(country)
                random.shuffle(options)
                
                await send_message_with_flag(mobile, country, options)
        
        elif user_state["state"] == "game_over":
            if response == "play_again":
                # Start new game
                return await send_difficulty_buttons(mobile)

        return {"status": "success", "message": "Response processed"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 
