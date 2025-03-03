from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
from time import time
from .controllers.location_controller import router as location_router
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# Rate limiting configuration
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Production'da spesifik host'lar belirtilmeli
)

# Include routers
app.include_router(location_router, prefix="/service", tags=["location"])

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
        self.connection_count = 0

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_count += 1
        logger.info(f"WebSocket connection established. Total connections: {self.connection_count}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        self.connection_count -= 1
        logger.info(f"WebSocket connection closed. Total connections: {self.connection_count}")

    async def broadcast(self, message: str):
        logger.info(f"Broadcasting message: {message}")
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                await self.disconnect(connection)

manager = ConnectionManager()

@app.get("/service")
@limiter.limit("100/minute")
async def service_status(request: Request):
    logger.info("Service status endpoint accessed")
    return {
        "message": "Service is running",
        "websocket_connections": manager.connection_count,
        "uptime": time() - app.start_time if hasattr(app, 'start_time') else 0
    }

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
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Add startup event to initialize app start time
@app.on_event("startup")
async def startup_event():
    app.start_time = time()
    logger.info("Application startup completed")
