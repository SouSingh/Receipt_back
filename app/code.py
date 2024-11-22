from pydantic import BaseModel
from typing import List
import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio  # For async operations

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_KEY")

# Configure Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

class RestaurantMenu(BaseModel):
    dish_name: str
    dish_price: str
    dish_type: str

async def get_restaurant_menu(image: Image.Image):
    try:
        # Simulated fast processing with reduced overhead
        prompt = "List out the restaurant menu"
        model = genai.GenerativeModel(
            "gemini-1.5-pro",
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": list[RestaurantMenu],
            },
        )
        # Assuming `generate_content` has async support
        response = await asyncio.to_thread(model.generate_content, [prompt, image])
        return response.text
    except Exception as e:
        return {"error": str(e)}

@app.post("/get-menu/")
async def get_menu(image: UploadFile = File(...)):
    try:
        # Limit image processing
        img = Image.open(image.file)
        img.thumbnail((800, 800))  # Resize with thumbnail for faster processing

        # Fetch menu asynchronously
        menu_json = await asyncio.wait_for(get_restaurant_menu(img), timeout=9)  # Adjust timeout for safety
        return JSONResponse(content={"menu": menu_json})
    except asyncio.TimeoutError:
        return JSONResponse(content={"error": "Request timed out. Try again."}, status_code=504)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
