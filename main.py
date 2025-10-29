
import json
import os
from typing import List
from datetime import datetime

import dotenv
import httpx
from fastapi import FastAPI, HTTPException
from google.cloud import storage
from google.cloud.storage import Bucket
from pydantic import BaseModel

# Constants
dotenv.load_dotenv()

VERSION = "1.0.0"
SWAPI_URL = "https://www.swapi.tech/api/films"
BUCKET_NAME = "devops_engineer_swapi_test"
CREDENTIALS_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", default="/app/service-account-key.json")

app = FastAPI(title="SWAPI Scraper", version=VERSION)

class FilmData(BaseModel):
    """Model for film data stored in the bucket."""
    filename: str
    upload_date: str
    size: int

def get_bucket() -> Bucket:
    """Get or create the Google Cloud Storage bucket."""
    print(os.listdir('/app'), r'CREDENTIALS_PATH', os.path.exists(CREDENTIALS_PATH))
    if not os.path.exists(r'CREDENTIALS_PATH'):
        raise HTTPException(
            status_code=500,
            detail=f"Credentials file not found at {CREDENTIALS_PATH}"
        )
    
    storage_client = storage.Client.from_service_account_json(CREDENTIALS_PATH)
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    
    if not bucket.exists():
        bucket = storage_client.create_bucket(BUCKET_NAME)
    
    return bucket

@app.get("/version")
async def get_version():
    """Return the service version."""
    return {"version": VERSION}

@app.get("/bucket-contents", response_model=List[FilmData])
async def list_bucket_contents():
    """List all files in the Google Cloud Storage bucket."""
    try:
        bucket = get_bucket()
        blobs = bucket.list_blobs()
        
        contents = []
        for blob in blobs:
            contents.append(FilmData(
                filename=blob.name,
                upload_date=blob.time_created.isoformat() if blob.time_created else "",
                size=blob.size
            ))
        
        return contents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing bucket: {str(e)}")

@app.post("/download-from-api")
async def download_from_api():
    """Download data from SWAPI and store it in the Google Cloud Storage bucket."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(SWAPI_URL)
            response.raise_for_status()
            data = response.json()
            
            # Format the data for storage
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"swapi_films_{timestamp}.json"
            
            # Store in Google Cloud Storage
            bucket = get_bucket()
            blob = bucket.blob(filename)
            blob.upload_from_string(
                json.dumps(data, indent=2),
                content_type='application/json'
            )
            
            return {
                "status": "success",
                "message": f"Data downloaded and stored as {filename}",
                "timestamp": timestamp
            }
            
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching from SWAPI: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
