from openai import OpenAI
import requests
import json
from app.core.config import Config

API_KEY = Config.DEEPSEEK_API_KEY 

from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,  
)

def generate_deepseek_report(data): 
    
    # Build the structured prompt
    prompt = f"""
    Act as a music data analyst. Generate a weekly report for a Spotify user based on this data:
    - Top Tracks: {data[0]}
    - Top Artists: {data[1]}
    - Top Genres: {data[2]}
    - Extra Data: {data[3]}

    Follow these rules:
    1. Write a catchy title and 1-paragraph description.
    2. Provide a 5-paragraph report covering:
    - Summary of preferences (mention top genres/artists).
    - Notable patterns (e.g., time/day trends).
    - Key highlight (e.g., "You discovered 10 new artists").
    - 2 personalized recommendations (artists/albums).
    - Fun insight (e.g., "Your playlist is 90% nostalgic!").
    3. Use friendly, enthusiastic tone.
    4. The values of durations are set in milliseconds; convert them in minutes or hours (choose which is the best option in each case) for a better understanding.
    5. Return the response as valid JSON with this structure:
    {{
        "title": "text",
        "description": "text",
        "report": {{
            "summary": "text",
            "patterns": "text",
            "highlight": "text",
            "recommendations": "text",
            "insight": "text"
        }}
    }}
    
    Important: 
    - Act as a music data analyst. Generate a  JSON, without any comments, pre-parsing, or additional text, for a weekly report for a Spotify user based on this data:   
    """
    completion = client.chat.completions.create(
        model="deepseek/deepseek-r1:free",  # Model in OpenRouter
        messages=[ {"role": "user", "content": prompt} ],
        response_format={ "type": "json_object" },  # Force response in JSON
        temperature=0.7  # Control creativity
    )
   
    return completion.choices[0].message.content
    
    