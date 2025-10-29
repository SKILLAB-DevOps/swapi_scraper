# SWAPI Scraper

A FastAPI application that scrapes the Star Wars API (SWAPI) and stores the data in Google Cloud Storage.

## Features

- FastAPI interface with endpoints for:
  - Service version information
  - Bucket contents listing
  - Download data from SWAPI
- Google Cloud Storage integration
- Async HTTP client for API requests

## Prerequisites

1. Python 3.13 or higher
2. Google Cloud SDK installed and configured
3. Google Cloud Storage credentials configured

## Setup

1. Install dependencies:
```bash
pip install -e .
```

2. Set up Google Cloud Storage:
   - Install and configure the Google Cloud SDK
   - Create a service account with Storage Admin permissions
   - Download the service account key JSON file
   - Set the environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

## Running the Application

Start the FastAPI server:

```bash
python main.py
```

The server will start on http://0.0.0.0:8000

## API Endpoints

- GET `/version` - Get the service version
- GET `/bucket-contents` - List all files in the Google Cloud Storage bucket
- POST `/download-from-api` - Download data from SWAPI and store it in the bucket

## Documentation

Once the server is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc