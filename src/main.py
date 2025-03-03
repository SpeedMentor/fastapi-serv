from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from uuid import uuid4
import logging
import psycopg2
import json
import os
from time import time

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API Key Security
API_KEY = os.getenv("API_KEY", "secure-api-key")  # Use environment variable for security
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")

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
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    response_time FLOAT
)
""")
conn.commit()

class LocationData(BaseModel):
    city: str
    latitude: float
    longitude: float

# Middleware to log all requests with response time
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time()
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    duration = time() - start_time
    logger.info(f"Response status: {response.status_code}, Response time: {duration:.4f} sec")
    return response

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket connection established")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info("WebSocket connection closed")

    async def broadcast(self, message: str):
        logger.info(f"Broadcasting message: {message}")
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/service", dependencies=[Depends(verify_api_key)])
def service_status():
    logger.info("Service status endpoint accessed")
    return {"message": "Service is running"}

@app.websocket("/service/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"WebSocket received data: {data}")
            await manager.broadcast(f"Received data: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/service/submit", dependencies=[Depends(verify_api_key)])
def submit_location(data: LocationData):
    start_time = time()
    request_id = str(uuid4())
    cursor.execute("INSERT INTO requests (id, location, status) VALUES (%s, %s, %s)",
                   (request_id, f"{data.city} ({data.latitude}, {data.longitude})", "received"))
    conn.commit()
    duration = time() - start_time
    cursor.execute("UPDATE requests SET response_time = %s WHERE id = %s", (duration, request_id))
    conn.commit()
    logger.info(f"Location data received: {data.city} at {data.latitude}, {data.longitude} (ID: {request_id}), Response time: {duration:.4f} sec")
    return {"request_id": request_id, "status": "received", "response_time": f"{duration:.4f} sec"}

@app.get("/service/request-{request_id}", dependencies=[Depends(verify_api_key)])
def get_request_status(request_id: str):
    cursor.execute("SELECT id, location, status, created_at, updated_at, response_time FROM requests WHERE id = %s", (request_id,))
    result = cursor.fetchone()
    if result:
        return {"request_id": result[0], "location": result[1], "status": result[2], "created_at": result[3], "updated_at": result[4], "response_time": result[5]}
    raise HTTPException(status_code=404, detail="Request not found")

@app.get("/service/devops/track-{track_id}", dependencies=[Depends(verify_api_key)])
def track_devops_request(track_id: str):
    cursor.execute("SELECT id, location, status, created_at, updated_at, response_time FROM requests WHERE id = %s", (track_id,))
    result = cursor.fetchone()
    if result:
        log_entry = {"request_id": result[0], "location": result[1], "status": result[2], "created_at": result[3], "updated_at": result[4], "response_time": result[5]}
        logger.info(f"DevOps tracking request: {json.dumps(log_entry)}")
        return log_entry
    raise HTTPException(status_code=404, detail="Request not found")
