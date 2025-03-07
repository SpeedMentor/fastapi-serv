# API Documentation

## General Information

- Base URL: `http://localhost:8000`
- API Version: v1
- Format: JSON
- Encoding: UTF-8

## Authentication

The API uses API Key based authentication. All requests require the `X-API-Key` header.

```http
X-API-Key: your-api-key
```

## Endpoints

### Service Status

```http
GET /service
```

Checks service status.

#### Response

```json
{
    "message": "Service is running"
}
```

### Submit Location

```http
POST /service/submit
```

Adds new location information.

#### Headers

```http
X-API-Key: your-api-key
Content-Type: application/json
```

#### Request Body

```json
{
    "city": "Istanbul",
    "latitude": 41.0082,
    "longitude": 28.9784
}
```

#### Response

```json
{
    "request_id": "uuid-string",
    "status": "received",
    "response_time": "0.1234 sec"
}
```

### Query Location Status

```http
GET /service/request-{request_id}
```

Queries the status of a specific location record.

#### Headers

```http
X-API-Key: your-api-key
```

#### Response

```json
{
    "request_id": "uuid-string",
    "location": "Istanbul (41.0082, 28.9784)",
    "status": "received",
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00",
    "response_time": 0.1234
}
```

### WebSocket Connection

```http
WebSocket /service/stream
```

WebSocket connection for real-time data streaming.

#### Example Usage

```javascript
const ws = new WebSocket('ws://localhost:8000/service/stream');

ws.onmessage = function(event) {
    console.log('Received:', event.data);
};

ws.send('test message');
```

## Error Codes

- 200: Success
- 400: Bad Request
- 403: Unauthorized Access
- 404: Resource Not Found
- 500: Server Error

## Error Responses

```json
{
    "detail": "Error message"
}
```

## Rate Limiting

The API is limited to 100 requests per minute per IP address.

## Example Usage

### Submit Location with cURL

```bash
curl -X POST http://localhost:8000/service/submit \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Istanbul",
    "latitude": 41.0082,
    "longitude": 28.9784
  }'
```

### Query Location with Python

```python
import requests

response = requests.get(
    'http://localhost:8000/service/request-uuid-string',
    headers={'X-API-Key': 'your-api-key'}
)
print(response.json())
```

### WebSocket Connection with JavaScript

```javascript
const ws = new WebSocket('ws://localhost:8000/service/stream');

ws.onopen = function() {
    console.log('Connected to WebSocket');
    ws.send('Hello Server!');
};

ws.onmessage = function(event) {
    console.log('Received:', event.data);
};

ws.onerror = function(error) {
    console.error('WebSocket error:', error);
};

ws.onclose = function() {
    console.log('Disconnected from WebSocket');
};
``` 