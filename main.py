import os
import asyncio
from pathlib import Path
from typing import List
from datetime import datetime

import dotenv
import httpx
import backoff
from fastapi import FastAPI, HTTPException
from google.cloud import storage
from google.cloud.storage import Bucket
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Constants
dotenv.load_dotenv()

VERSION = "1.0.0"
SWAPI_URL = "https://www.swapi.tech/api/films"
SWAPI_URL_PLANETS = "https://www.swapi.tech/api/planets"
BUCKET_NAME = "devops_engineer_swapi_test"
CREDENTIALS_PATH = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS", default="/app/service-account-key.json"
)

app = FastAPI(title="SWAPI Scraper", version=VERSION)

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class FilmData(BaseModel):
    """Model for film data stored in the bucket."""

    filename: str
    upload_date: str
    size: int


class Planet(Base):
    """SQLAlchemy model for planets."""

    __tablename__ = "planets"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    diameter = Column(String(50))
    rotation_period = Column(String(50))
    orbital_period = Column(String(50))
    gravity = Column(String(50))
    population = Column(String(50))
    climate = Column(String(100))
    terrain = Column(String(100))
    surface_water = Column(String(50))
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PlanetResponse(BaseModel):
    """Pydantic model for API response."""

    id: int
    name: str
    diameter: str
    rotation_period: str
    orbital_period: str
    gravity: str
    population: str
    climate: str
    terrain: str
    surface_water: str


# Create database tables
Base.metadata.create_all(bind=engine)


def get_bucket() -> Bucket:
    """Get or create the Google Cloud Storage bucket."""
    path = Path(CREDENTIALS_PATH)
    if not path.exists():
        raise HTTPException(
            status_code=500, detail=f"Credentials file not found at {CREDENTIALS_PATH}"
        )

    storage_client = storage.Client.from_service_account_json(path)
    bucket = storage_client.bucket(BUCKET_NAME)

    if not bucket.exists():
        bucket = storage_client.create_bucket(BUCKET_NAME)

    return bucket


async def fetch_with_retry(
    client: httpx.AsyncClient, url: str, max_retries: int = 5
) -> dict:
    """Fetch data from URL with retry logic."""

    @backoff.on_exception(
        backoff.expo,
        (httpx.TimeoutException, httpx.HTTPError),
        max_tries=max_retries,
        max_time=30,
    )
    async def _fetch():
        response = await client.get(url, timeout=30.0)
        response.raise_for_status()
        return response.json()

    try:
        return await _fetch()
    except (httpx.TimeoutException, httpx.HTTPError) as e:
        print(f"Error fetching {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data from {url}")


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
        raise HTTPException(
            status_code=500, detail=f"Error fetching from SWAPI: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@app.get("/planets", response_model=List[PlanetResponse])
async def list_planets():
    """List all planets from the database."""
    db = SessionLocal()
    try:
        planets = db.query(Planet).all()
        return planets
    finally:
        db.close()


@app.post("/fetch-planets")
async def fetch_planets():
    """Fetch planets from SWAPI and store them in the database."""
    db = SessionLocal()
    try:
        # Configure client with appropriate timeouts and limits
        timeout = httpx.Timeout(30.0, connect=10.0)
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)

        async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
            # Get total number of planets
            response = await fetch_with_retry(client, SWAPI_URL_PLANETS)
            total_records = response["total_records"]

            # Fetch all planets with rate limiting
            planets_data = []
            for page in range(1, (total_records // 10) + 2):
                await asyncio.sleep(1)  # Rate limiting
                page_data = await fetch_with_retry(
                    client, f"{SWAPI_URL_PLANETS}?page={page}"
                )
                if "results" in page_data:
                    planets_data.extend(page_data["results"])

            # Process and store each planet with rate limiting
            processed_count = 0
            for planet_info in planets_data:
                if processed_count >= 10:
                    break

                try:
                    await asyncio.sleep(1)  # Rate limiting
                    response = await fetch_with_retry(client, planet_info["url"])
                    planet_result = response.get("result", {})

                    if "properties" not in planet_result:
                        print(f"Missing properties for planet: {planet_info}")
                        continue

                    planet_data = planet_result["properties"]

                    # Check if planet already exists
                    existing_planet = (
                        db.query(Planet).filter_by(name=planet_data["name"]).first()
                    )
                    if existing_planet:
                        # Update existing planet
                        for key, value in planet_data.items():
                            if hasattr(existing_planet, key):
                                setattr(existing_planet, key, str(value))
                        existing_planet.updated = datetime.utcnow()
                    else:
                        # Create new planet
                        planet = Planet(
                            name=planet_data["name"],
                            diameter=str(planet_data["diameter"]),
                            rotation_period=str(planet_data["rotation_period"]),
                            orbital_period=str(planet_data["orbital_period"]),
                            gravity=str(planet_data["gravity"]),
                            population=str(planet_data["population"]),
                            climate=str(planet_data["climate"]),
                            terrain=str(planet_data["terrain"]),
                            surface_water=str(planet_data["surface_water"]),
                        )
                        db.add(planet)

                    processed_count += 1
                    # Commit every 10 planets to avoid long transactions
                    if processed_count % 10 == 0:
                        db.commit()

                except Exception as e:
                    print(
                        f"Error processing planet {planet_info.get('name', 'unknown')}: {str(e)}"
                    )
                    continue

            # Final commit for remaining changes
            db.commit()
            return {
                "status": "success",
                "message": f"Successfully processed {processed_count} planets",
                "timestamp": datetime.utcnow().isoformat(),
            }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
