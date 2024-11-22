from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to specific origin(s) for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Twitter Bearer Token
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# URL to fetch Twitter user data by username
TWITTER_API_URL = "https://api.twitter.com/2/users/by/username/{username}?user.fields=created_at,description,location,profile_image_url,public_metrics,verified,entities,url"

# Response model for Twitter user data
class TwitterUserData(BaseModel):
    name: str
    username: str
    followers: int
    following: int
    description: str
    location: str
    profile_image_url: str
    tweets: int
    listed: int
    created_at: str
    verified: bool
    url: str

# Function to fetch Twitter data by username
async def fetch_twitter_data(username: str) -> dict:
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"
    }
    url = TWITTER_API_URL.format(username=username)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch Twitter data")
        
        return response.json()

# FastAPI route to fetch Twitter user data
@app.get("/api/twitter/{username}", response_model=TwitterUserData)
async def get_twitter_user_data(username: str):
    twitter_data = await fetch_twitter_data(username)
    
    # Extract necessary data from the response
    user_data = twitter_data.get('data', {})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "name": user_data.get("name", ""),
        "username": user_data.get("username", ""),
        "followers": user_data.get("public_metrics", {}).get("followers_count", 0),
        "following": user_data.get("public_metrics", {}).get("following_count", 0),
        "description": user_data.get("description", ""),
        "location": user_data.get("location", ""),
        "profile_image_url": user_data.get("profile_image_url", ""),
        "tweets": user_data.get("public_metrics", {}).get("tweet_count", 0),
        "listed": user_data.get("public_metrics", {}).get("listed_count", 0),
        "created_at": user_data.get("created_at", ""),
        "verified": user_data.get("verified", False),
        "url": user_data.get("url", ""),
    }
