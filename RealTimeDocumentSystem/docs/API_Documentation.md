# API Documentation

## Overview

The Real-Time Document Editor API provides RESTful endpoints for document management, user collaboration, and real-time communication. All endpoints return JSON responses and support standard HTTP methods.

## Base URL

- **Development**: `http://127.0.0.1:8000`
- **Production**: `https://yourdomain.com`

## Authentication

### Session Authentication
Most endpoints use Django's session-based authentication. Users must be logged in to access protected endpoints.

### CSRF Protection
All POST/PUT/PATCH/DELETE requests require a valid CSRF token. Include the token in the request header:

```http
X-CSRFToken: your-csrf-token
```

## Endpoints

### User Management

#### Register User
```http
POST /api/register/
```

**Request Body:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password123"
}
```

**Response:**
```json
{
    "success": true,
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
    }
}
```

#### Login User
```http
POST /api/login/
```

**Request Body:**
```json
{
    "username": "john_doe",
    "password": "secure_password123"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
    }
}
```

#### Logout User
```http
POST /api/logout/
```

**Response:**
```json
{
    "success": true,
    "message": "Logout successful"
}
```

### Document Management

#### List User Documents
```http
GET /api/documents/
```

**Response:**
```json
{
    "documents": [
        {
            "id": 1,
            "title": "Project Proposal",
            "content": "This is the document content...",
            "owner": {
                "id": 1,
                "username": "john_doe"
            },
            "collaborators": [
                {
                    "id": 2,
                    "username": "jane_smith"
                }
            ],
            "is_public": false,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T14:45:00Z"
        }
    ]
}
```

#### Create Document
```http
POST /api/documents/
```

**Request Body:**
```json
{
    "title": "New Document",
    "content": "Initial content",
    "is_public": false
}
```

**Response:**
```json
{
    "success": true,
    "document": {
        "id": 2,
        "title": "New Document",
        "content": "Initial content",
        "owner": {
            "id": 1,
            "username": "john_doe"
        },
        "collaborators": [],
        "is_public": false,
        "created_at": "2024-01-15T15:00:00Z",
        "updated_at": "2024-01-15T15:00:00Z"
    }
}
```

#### Get Document Details
```http
GET /api/documents/{id}/
```

**Response:**
```json
{
    "id": 1,
    "title": "Project Proposal",
    "content": "This is the document content...",
    "owner": {
        "id": 1,
        "username": "john_doe"
    },
    "collaborators": [
        {
            "id": 2,
            "username": "jane_smith"
        }
    ],
    "is_public": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T14:45:00Z"
}
```

#### Update Document
```http
PATCH /api/documents/{id}/
```

**Request Body:**
```json
{
    "title": "Updated Title",
    "is_public": true
}
```

**Response:**
```json
{
    "success": true,
    "document": {
        "id": 1,
        "title": "Updated Title",
        "content": "This is the document content...",
        "owner": {
            "id": 1,
            "username": "john_doe"
        },
        "collaborators": [
            {
                "id": 2,
                "username": "jane_smith"
            }
        ],
        "is_public": true,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T16:00:00Z"
    }
}
```

#### Delete Document
```http
DELETE /api/documents/{id}/
```

**Response:**
```json
{
    "success": true,
    "message": "Document deleted successfully"
}
```

### Collaboration

#### Add Collaborator
```http
POST /api/document/{id}/add-collaborator/
```

**Request Body:**
```json
{
    "username": "jane_smith"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Collaborator added successfully",
    "collaborator": {
        "id": 2,
        "username": "jane_smith",
        "email": "jane@example.com"
    }
}
```

#### Remove Collaborator
```http
DELETE /api/document/{id}/remove-collaborator/
```

**Request Body:**
```json
{
    "username": "jane_smith"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Collaborator removed successfully"
}
```

### Version Control

#### Save Document Version
```http
POST /api/document/{id}/save-version/
```

**Request Body:**
```json
{
    "content": "Updated document content",
    "cursor_position": 150
}
```

**Response:**
```json
{
    "success": true,
    "version": {
        "id": 1,
        "document": 1,
        "content": "Updated document content",
        "created_at": "2024-01-15T16:30:00Z"
    },
    "timestamp": "2024-01-15T16:30:00Z"
}
```

#### Get Document Versions
```http
GET /api/document/{id}/versions/
```

**Response:**
```json
{
    "versions": [
        {
            "id": 1,
            "content": "Updated document content",
            "created_at": "2024-01-15T16:30:00Z"
        },
        {
            "id": 2,
            "content": "Previous version content",
            "created_at": "2024-01-15T14:45:00Z"
        }
    ]
}
```

#### Restore Document Version
```http
POST /api/document/{id}/restore-version/{version_id}/
```

**Response:**
```json
{
    "success": true,
    "message": "Version restored successfully",
    "document": {
        "id": 1,
        "title": "Project Proposal",
        "content": "Restored content from version 2",
        "updated_at": "2024-01-15T17:00:00Z"
    }
}
```

### User Management

#### List Available Users
```http
GET /api/users/
```

**Response:**
```json
{
    "users": [
        {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com"
        },
        {
            "id": 2,
            "username": "jane_smith",
            "email": "jane@example.com"
        }
    ]
}
```

#### Get User Profile
```http
GET /api/users/{id}/
```

**Response:**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "date_joined": "2024-01-01T00:00:00Z",
    "documents_owned": 5,
    "documents_collaborating": 3
}
```

## WebSocket API

### Connection
```javascript
const wsUrl = `ws://localhost:8000/ws/document/${documentId}/`;
const socket = new WebSocket(wsUrl);
```

### Message Types

#### Edit Document
```javascript
socket.send(JSON.stringify({
    type: 'edit',
    content: 'Updated document content',
    cursor_position: 150
}));
```

#### Cursor Movement
```javascript
socket.send(JSON.stringify({
    type: 'cursor_move',
    cursor_position: 150
}));
```

#### Typing Indicator
```javascript
// Start typing
socket.send(JSON.stringify({
    type: 'typing_start',
    user_id: 1,
    username: 'john_doe'
}));

// Stop typing
socket.send(JSON.stringify({
    type: 'typing_stop',
    user_id: 1
}));
```

#### AI Suggestion Request
```javascript
socket.send(JSON.stringify({
    type: 'ai_suggestion_request',
    text: 'Current document text'
}));
```

### Incoming Messages

#### Document Edit
```javascript
{
    type: 'edit',
    content: 'Updated content from another user',
    user_id: 2,
    username: 'jane_smith'
}
```

#### User Joined
```javascript
{
    type: 'user_joined',
    user_id: 2,
    username: 'jane_smith'
}
```

#### User Left
```javascript
{
    type: 'user_left',
    user_id: 2,
    username: 'jane_smith'
}
```

#### Cursor Movement
```javascript
{
    type: 'cursor_move',
    user_id: 2,
    username: 'jane_smith',
    cursor_position: 150
}
```

#### AI Suggestion
```javascript
{
    type: 'ai_suggestion',
    suggestion: ['Suggestion 1', 'Suggestion 2'],
    original_text: 'Original text that triggered suggestion'
}
```

#### Version Saved
```javascript
{
    type: 'version_saved',
    timestamp: '2024-01-15T16:30:00Z'
}
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "Invalid request data",
    "details": {
        "field_name": ["This field is required."]
    }
}
```

### 401 Unauthorized
```json
{
    "error": "Authentication required",
    "message": "Please log in to access this resource"
}
```

### 403 Forbidden
```json
{
    "error": "Permission denied",
    "message": "You don't have permission to access this document"
}
```

### 404 Not Found
```json
{
    "error": "Resource not found",
    "message": "Document with id 999 does not exist"
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal server error",
    "message": "An unexpected error occurred"
}
```

## Rate Limiting

- **API Endpoints**: 100 requests per minute per user
- **WebSocket Messages**: 1000 messages per minute per connection
- **Document Saves**: 10 saves per minute per document

## Pagination

For endpoints that return lists, pagination is supported:

```http
GET /api/documents/?page=1&page_size=10
```

**Response:**
```json
{
    "documents": [...],
    "pagination": {
        "page": 1,
        "page_size": 10,
        "total_pages": 5,
        "total_count": 50,
        "has_next": true,
        "has_previous": false
    }
}
```

## Search and Filtering

### Search Documents
```http
GET /api/documents/?search=project
```

### Filter by Owner
```http
GET /api/documents/?owner=john_doe
```

### Filter by Date Range
```http
GET /api/documents/?created_after=2024-01-01&created_before=2024-01-31
```

## Webhooks (Future Feature)

Webhooks will be available for:
- Document updates
- User joins/leaves
- Version saves
- Collaboration changes

## SDKs and Libraries

### JavaScript Client
```javascript
import { DocumentEditor } from 'realtime-doc-editor-sdk';

const editor = new DocumentEditor({
    documentId: 1,
    apiKey: 'your-api-key',
    onUpdate: (content) => console.log('Document updated:', content)
});
```

### Python Client
```python
from realtime_doc_editor import DocumentClient

client = DocumentClient(api_key='your-api-key')
document = client.get_document(document_id=1)
```

## Testing

### API Testing with curl
```bash
# Get documents
curl -X GET http://localhost:8000/api/documents/ \
  -H "Cookie: sessionid=your-session-id"

# Create document
curl -X POST http://localhost:8000/api/documents/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your-csrf-token" \
  -d '{"title": "Test Document", "content": "Test content"}'
```

### WebSocket Testing with wscat
```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket
wscat -c ws://localhost:8000/ws/document/1/

# Send message
{"type": "edit", "content": "Hello World"}
```

## Support

For API support:
- Email: api-support@example.com
- Documentation: https://docs.example.com/api
- GitHub Issues: https://github.com/example/realtime-doc-editor/issues 