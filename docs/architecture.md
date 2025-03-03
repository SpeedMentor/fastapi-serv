# Architecture Documentation

## Overview

This project is a FastAPI application developed using the Controller-Service-Repository (CSR) pattern. The application is a REST API service that processes and stores location information.

## Architectural Pattern

### Controller-Service-Repository Pattern

1. **Controller Layer**
   - Defines API endpoints
   - Uses request/response models
   - Calls service layer
   - Handles error management

2. **Service Layer**
   - Contains business logic
   - Uses repository layer
   - Performs data transformations
   - Implements business rules

3. **Repository Layer**
   - Manages database operations
   - Contains CRUD operations
   - Handles database connection management

## Database Schema

### Requests Table

```sql
CREATE TABLE requests (
    id UUID PRIMARY KEY,
    location TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    response_time FLOAT
);
```

## Security

### API Key Authentication
- `X-API-Key` header required for each request
- API keys managed through environment variables
- Invalid API keys return 403 Forbidden error

### Rate Limiting
- 100 requests per minute per IP address
- 429 Too Many Requests error on rate limit exceeded

## WebSocket Management

### ConnectionManager Class
- Manages active WebSocket connections
- Handles connection acceptance and closure
- Sends broadcast messages

## Logging

### Log Levels
- INFO: Normal operation logs
- ERROR: Error conditions
- WARNING: Warning conditions

### Log Format
```
%(asctime)s - %(levelname)s - %(message)s
```

## Test Strategy

### Unit Tests
- Separate tests for each layer
- Isolation using mocks
- Coverage target: 80%

### Integration Tests
- API endpoint tests
- Database integration tests
- WebSocket connection tests

## CI/CD Pipeline

### Stages
1. Code checkout
2. Python environment setup
3. Test and coverage check
4. Docker image build
5. Deployment

### Coverage Check
- Minimum coverage: 80%
- Coverage reports in HTML format
- Archived in Jenkins

## Deployment

### Docker
- Python 3.10 slim image
- PostgreSQL client
- Hot reload support

### Environment Variables
```env
API_KEY=secure-api-key
POSTGRES_HOST=postgres-service
POSTGRES_PORT=5432
POSTGRES_DB=fastapi_db
POSTGRES_USER=fastapi_user
POSTGRES_PASSWORD=securepassword
```

## Monitoring

### Metrics
- Response time
- Request count
- Error rate
- WebSocket connection count

### Health Checks
- Service status
- Database connection
- WebSocket connection

## Performance Optimizations

### Database
- Connection pooling
- Indexes
- Prepared statements

### Caching
- Response caching
- Connection caching

## Error Handling

### Exception Handling
- Custom exception classes
- HTTP status code mapping
- Detailed error messages

### Retry Mechanism
- Database connection errors
- Network errors
- Rate limit exceeded

## Development Guidelines

### Code Style
- PEP 8 compliance
- Type hints usage
- Docstring requirement

### Git Workflow
- Feature branches
- Pull request review
- Semantic versioning

## Future Developments

### Planned Features
- Authentication system
- Rate limiting improvements
- Caching mechanism
- Monitoring dashboard
- API versioning 