from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
from time import time
from .controllers.location_controller import router as location_router
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator
import json
from pythonjsonlogger import jsonlogger

# Configure structured logging
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

WEBSOCKET_CONNECTIONS = Gauge(
    'websocket_connections_active',
    'Number of active WebSocket connections'
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total number of HTTP errors',
    ['type']
)

app = FastAPI()

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app)

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

# Middleware to log all requests with response time and metrics
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time()
    method = request.method
    endpoint = request.url.path
    
    # Log request
    logger.info("Incoming request", extra={
        "method": method,
        "endpoint": endpoint,
        "client_ip": request.client.host
    })
    
    try:
        response = await call_next(request)
        duration = time() - start_time
        
        # Record metrics
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=response.status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
        
        # Log response
        logger.info("Request completed", extra={
            "method": method,
            "endpoint": endpoint,
            "status_code": response.status_code,
            "duration": duration
        })
        
        return response
    except Exception as e:
        ERROR_COUNT.labels(type=type(e).__name__).inc()
        logger.error("Request failed", extra={
            "method": method,
            "endpoint": endpoint,
            "error": str(e)
        })
        raise

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.connection_count = 0

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_count += 1
        WEBSOCKET_CONNECTIONS.set(self.connection_count)
        logger.info("WebSocket connection established", extra={
            "total_connections": self.connection_count
        })

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        self.connection_count -= 1
        WEBSOCKET_CONNECTIONS.set(self.connection_count)
        logger.info("WebSocket connection closed", extra={
            "total_connections": self.connection_count
        })

    async def broadcast(self, message: str):
        logger.info("Broadcasting message", extra={
            "message": message,
            "recipients": len(self.active_connections)
        })
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error("Error broadcasting message", extra={
                    "error": str(e)
                })
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
            logger.info("WebSocket received data", extra={
                "data": data
            })
            await manager.broadcast(f"Received data: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error", extra={
            "error": str(e)
        })
        manager.disconnect(websocket)

# Add startup event to initialize app start time
@app.on_event("startup")
async def startup_event():
    app.start_time = time()
    logger.info("Application startup completed")
