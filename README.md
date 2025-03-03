# FastAPI Location Service

This project is a REST API service that processes and stores location information. It is developed using the Controller-Service-Repository pattern.

## Features

- Location information storage and querying
- Real-time data streaming with WebSocket support
- API Key based security
- PostgreSQL database integration
- Comprehensive test coverage
- Docker container support

## Technologies

- FastAPI
- PostgreSQL
- Docker
- Pytest
- WebSocket
- Python 3.10+

## Installation

### Requirements

- Python 3.10+
- PostgreSQL
- Docker (optional)

### Local Development Environment

1. Clone the repository:
```bash
git clone https://github.com/your-username/fastapi-service.git
cd fastapi-service
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create database:
```bash
createdb fastapi_db
```

5. Start the application:
```bash
uvicorn src.main:app --reload
```

### Running with Docker

1. Build Docker image:
```bash
docker build -t fastapi-service .
```

2. Start the application:
```bash
docker run -p 8000:8000 fastapi-service
```

## API Documentation

You can access the API documentation at the following URLs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints

#### GET /service
Checks service status.

#### POST /service/submit
Adds new location information.

**Request Body:**
```json
{
    "city": "Istanbul",
    "latitude": 41.0082,
    "longitude": 28.9784
}
```

**Headers:**
- X-API-Key: API key

#### GET /service/request-{request_id}
Queries the status of a specific location record.

**Headers:**
- X-API-Key: API key

#### WebSocket /service/stream
WebSocket connection for real-time data streaming.

## Testing

To run tests:

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

## CI/CD

The project uses Jenkins for CI/CD pipeline. The pipeline includes the following steps:

1. Code checkout
2. Python environment setup
3. Test and coverage check
4. Docker image build
5. Deployment

## Project Structure

```
src/
├── controllers/     # API endpoints
├── services/       # Business logic
├── repositories/   # Database operations
├── models/         # Data models
├── database/       # Database connection management
└── main.py         # Main application
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Project Owner - [@your-username](https://github.com/your-username)

Project Link: [https://github.com/your-username/fastapi-service](https://github.com/your-username/fastapi-service) 