import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import logging

app = FastAPI()

# PostgreSQL Connection
conn = psycopg2.connect(
    dbname="fastapi_db",
    user="fastapi_user",
    password="securepassword",
    host="postgres-service",
    port="5432"
)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS requests (
    id UUID PRIMARY KEY,
    location TEXT,
    status TEXT
)
""")
conn.commit()

class LocationData(BaseModel):
    city: str
    latitude: float
    longitude: float

@app.post("/service/submit")
def submit_location(data: LocationData):
    request_id = str(uuid4())
    cursor.execute("INSERT INTO requests (id, location, status) VALUES (%s, %s, %s)",
                   (request_id, f"{data.city} ({data.latitude}, {data.longitude})", "received"))
    conn.commit()
    return {"request_id": request_id, "status": "received"}
