from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from time import time
from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .controllers.location_controller import router as location_router
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator
from .utils.logging_setup import logger, log_request_middleware
from .models.database import get_db, Request as RequestModel, Metrics as MetricsModel
import uuid

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

# Add logging middleware
app.middleware("http")(log_request_middleware)

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
            "total_connections": self.connection_count,
            "event_type": "websocket_connect"
        })

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        self.connection_count -= 1
        WEBSOCKET_CONNECTIONS.set(self.connection_count)
        logger.info("WebSocket connection closed", extra={
            "total_connections": self.connection_count,
            "event_type": "websocket_disconnect"
        })

    async def broadcast(self, message: str):
        logger.info("Broadcasting message", extra={
            "message": message,
            "recipients": len(self.active_connections),
            "event_type": "websocket_broadcast"
        })
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error("Error broadcasting message", extra={
                    "error": str(e),
                    "event_type": "websocket_error"
                })
                await self.disconnect(connection)

manager = ConnectionManager()

class SubmissionData(BaseModel):
    data: Dict
    metadata: Optional[Dict] = None

@app.get("/service")
@limiter.limit("5/minute")
async def service_status(request: Request):
    logger.info("Service status check", extra={
        "endpoint": "/service",
        "event_type": "status_check"
    })
    return {
        "message": "Service is running",
        "websocket_connections": manager.connection_count,
        "uptime": time() - app.start_time if hasattr(app, 'start_time') else 0
    }

@app.get("/service/request-{id}")
async def get_request_status(id: str, request: Request, db: Session = Depends(get_db)):
    logger.info("Request status check", extra={
        "request_id": id,
        "endpoint": f"/service/request-{id}",
        "event_type": "request_status_check"
    })
    
    db_request = db.query(RequestModel).filter(RequestModel.id == id).first()
    if not db_request:
        logger.warning("Request not found", extra={
            "request_id": id,
            "event_type": "request_not_found"
        })
        raise HTTPException(status_code=404, detail="Request not found")
    
    return {
        "status": db_request.status,
        "request_id": db_request.id,
        "timestamp": db_request.timestamp.isoformat(),
        "last_updated": db_request.last_updated.isoformat()
    }

@app.post("/service/submit")
async def submit_data(request: Request, data: SubmissionData, db: Session = Depends(get_db)):
    request_id = str(uuid.uuid4())
    timestamp = datetime.utcnow()
    
    logger.info("Data submission", extra={
        "request_id": request_id,
        "endpoint": "/service/submit",
        "event_type": "data_submission",
        "data_size": len(str(data.data)),
        "has_metadata": data.metadata is not None
    })
    
    # Create database entry
    db_request = RequestModel(
        id=request_id,
        status="processing",
        timestamp=timestamp,
        last_updated=timestamp,
        data=data.data,
        metadata=data.metadata
    )
    db.add(db_request)
    
    # Initialize metrics
    db_metrics = MetricsModel(
        id=str(uuid.uuid4()),
        request_id=request_id,
        timestamp=timestamp,
        additional_data={"initial_submission": True}
    )
    db.add(db_metrics)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Database error", extra={
            "error": str(e),
            "event_type": "database_error"
        })
        raise HTTPException(status_code=500, detail="Error processing request")
    
    # Update metrics
    REQUEST_COUNT.labels(method="POST", endpoint="/service/submit", status=200).inc()
    
    return {
        "status": "submitted",
        "request_id": request_id,
        "timestamp": timestamp.isoformat()
    }

@app.get("/service/devops/track-{id}")
async def track_request(id: str, request: Request, db: Session = Depends(get_db)):
    logger.info("DevOps tracking request", extra={
        "track_id": id,
        "endpoint": f"/service/devops/track-{id}",
        "event_type": "devops_tracking"
    })
    
    db_request = db.query(RequestModel).filter(RequestModel.id == id).first()
    if not db_request:
        logger.warning("Track ID not found", extra={
            "track_id": id,
            "event_type": "track_not_found"
        })
        raise HTTPException(status_code=404, detail="Track ID not found")
    
    # Get metrics
    db_metrics = db.query(MetricsModel).filter(
        MetricsModel.request_id == id
    ).order_by(MetricsModel.timestamp.desc()).first()
    
    metrics = {
        "process_time": db_metrics.process_time if db_metrics else 0,
        "memory_usage": db_metrics.memory_usage if db_metrics else 0,
        "error_count": db_metrics.error_count if db_metrics else 0,
        "status": db_request.status
    }
    
    return {
        "track_id": id,
        "status": db_request.status,
        "metrics": metrics,
        "request_timestamp": db_request.timestamp.isoformat(),
        "last_updated": db_request.last_updated.isoformat(),
        "tracking_info": {
            "endpoint_health": "healthy",
            "service_uptime": time() - app.start_time if hasattr(app, 'start_time') else 0,
            "active_connections": manager.connection_count
        }
    }

@app.websocket("/service/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info("WebSocket data received", extra={
                "data": data,
                "event_type": "websocket_data"
            })
            await manager.broadcast(f"Received data: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error", extra={
            "error": str(e),
            "event_type": "websocket_error"
        })
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    app.start_time = time()
    logger.info("Application started", extra={
        "event_type": "startup"
    })
