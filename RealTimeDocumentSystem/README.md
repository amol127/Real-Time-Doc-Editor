# Real-Time-Doc-Editor


# Real-Time Collaborative Document Editor

A modern, real-time collaborative document editing platform built with Django, Channels, and WebSockets. Multiple users can edit documents simultaneously with live updates, AI-powered suggestions, and version control.

## Features

### ✅ Core Features
- **Real-Time Collaboration**: Multiple users can edit documents simultaneously with live updates
- **User Authentication**: Secure login/registration system with session management
- **Document Management**: Create, edit, and organize documents with collaboration features
- **AI Suggestions**: Basic grammar and writing suggestions using text analysis
- **Modern UI**: Responsive, intuitive interface built with Bootstrap 5

### ✅ Advanced Features
- **User Presence**: See who's currently editing the document
- **Cursor Tracking**: Visual indicators showing where other users are typing
- **Version History**: Track document changes and revert to previous versions
- **Collaboration Controls**: Add/remove collaborators and set document visibility
- **Conflict Resolution**: Smart handling of concurrent edits

### ✅ Technical Features
- **WebSocket Communication**: Real-time bidirectional communication
- **RESTful API**: Complete API for document management
- **Modular Architecture**: Clean, maintainable code structure
- **Security**: Authentication, authorization, and input validation

## Technology Stack

- **Backend**: Django 4.2.20
- **Real-Time**: Django Channels 4.0.0
- **API**: Django REST Framework 3.14.0
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **WebSockets**: ASGI with Channel Layers

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip
- Redis (for production)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/amol127/Real-Time-Doc-Editor.git
   cd RealTimeDocumentSystem
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
    pip install daphne
   daphne -b 0.0.0.0 -p 8000 RealTimeDocumentSystem.asgi:application
   ```

7. **Access the application**
   - Open http://localhost:8000
   - Register a new account or login
   - Start creating and collaborating on documents!

### Production Setup

1. **Install Redis**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   
   # macOS
   brew install redis
   ```

2. **Update settings.py**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['*']
   
   CHANNEL_LAYERS = {
       "default": {
           "BACKEND": "channels_redis.core.RedisChannelLayer",
           "CONFIG": {
               "hosts": [("127.0.0.1", 6379)],
           },
       },
   }
   ```

3. **Deploy with ASGI server**
   ```bash
   pip install daphne
   daphne -b 0.0.0.0 -p 8000 RealTimeDocumentSystem.asgi:application
   ```

## Usage Guide

### Getting Started

1. **Registration/Login**
   - Visit the application and create an account
   - Login with your credentials

2. **Creating Documents**
   - Click "Create New Document" from the dashboard
   - Enter a title and start editing

3. **Collaboration**
   - Share document links with collaborators
   - Add collaborators via username in document settings
   - Set documents as public for wider access

4. **Real-Time Editing**
   - Multiple users can edit simultaneously
   - See live updates as others type
   - View active users and their cursor positions

### Features in Detail

#### Real-Time Collaboration
- **Live Updates**: Changes appear instantly for all users
- **User Presence**: See who's currently editing
- **Cursor Tracking**: Visual indicators for other users' positions
- **Conflict Resolution**: Smart handling of concurrent edits

#### AI Suggestions
- **Grammar Checks**: Basic spelling and grammar suggestions
- **Writing Tips**: Suggestions for improving text quality
- **Common Mistakes**: Detection of frequently misspelled words

#### Document Management
- **Version Control**: Automatic version creation for significant changes
- **Collaboration Controls**: Add/remove collaborators
- **Access Control**: Public/private document settings
- **Document History**: View and restore previous versions

## API Documentation

### Authentication Endpoints
- `POST /login/` - User login
- `POST /register/` - User registration
- `GET /logout/` - User logout

### Document Endpoints
- `GET /` - Dashboard (list documents)
- `POST /create/` - Create new document
- `GET /document/{id}/` - Edit document
- `GET /document/{id}/versions/` - View version history

### REST API
- `GET /api/documents/` - List documents
- `POST /api/documents/` - Create document
- `GET /api/documents/{id}/` - Get document details
- `PUT /api/documents/{id}/` - Update document
- `DELETE /api/documents/{id}/` - Delete document
- `POST /api/documents/{id}/add_collaborator/` - Add collaborator
- `GET /api/documents/{id}/versions/` - Get version history

### WebSocket Events
- `edit` - Document content changes
- `cursor_move` - Cursor position updates
- `user_joined` - User joined the document
- `user_left` - User left the document
- `ai_suggestion_request` - Request AI suggestions
- `ai_suggestion` - AI suggestion response

## Architecture

### Backend Architecture
```
RealTimeDocumentSystem/
├── app/
│   ├── models.py          # Database models
│   ├── views.py           # HTTP views and API
│   ├── consumers.py       # WebSocket consumers
│   ├── serializers.py     # API serializers
│   ├── routing.py         # WebSocket routing
│   └── templates/         # HTML templates
├── RealTimeDocumentSystem/
│   ├── settings.py        # Django settings
│   ├── urls.py           # URL configuration
│   └── asgi.py           # ASGI application
└── manage.py
```

### Data Models
- **Document**: Core document entity with content and metadata
- **DocumentVersion**: Version history for documents
- **DocumentSession**: Active user sessions for real-time tracking
- **User**: Django's built-in user model

### Real-Time Communication Flow
1. User connects to WebSocket with document ID
2. Server validates user access to document
3. User joins document room and notifies others
4. Real-time edits are broadcast to all users in room
5. AI suggestions are generated and sent to requesting user
6. User disconnection is handled gracefully

## Deployment Options

### Heroku Deployment
1. Create `Procfile`:
   ```
   web: daphne RealTimeDocumentSystem.asgi:application --port $PORT --bind 0.0.0.0
   ```

2. Add Redis addon:
   ```bash
   heroku addons:create heroku-redis:hobby-dev
   ```

3. Deploy:
   ```bash
   git push heroku main
   ```

### Docker Deployment
1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.9
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8000
   CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "RealTimeDocumentSystem.asgi:application"]
   ```

2. Create `docker-compose.yml`:
   ```yaml
   version: '3.8'
   services:
     web:
       build: .
       ports:
         - "8000:8000"
       depends_on:
         - redis
     redis:
       image: redis:alpine
   ```

## Security Considerations

- **Authentication**: Session-based authentication with CSRF protection
- **Authorization**: Document-level access control
- **Input Validation**: Server-side validation for all inputs
- **XSS Protection**: Content sanitization and proper escaping
- **CSRF Protection**: Django's built-in CSRF middleware

## Performance Optimization

- **Channel Layers**: Redis for production scalability
- **Database Indexing**: Optimized queries with proper indexing
- **Caching**: Redis-based caching for frequently accessed data
- **Static Files**: CDN-ready static file serving

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the code comments

## Future Enhancements

- [ ] Advanced AI integration (GPT, etc.)
- [ ] Rich text editor with formatting
- [ ] File attachments
- [ ] Comments and annotations
- [ ] Mobile app
- [ ] Advanced analytics
- [ ] Multi-language support 