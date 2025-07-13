from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import Document, DocumentVersion
from .serializers import DocumentSerializer, DocumentVersionSerializer
import json
from django.db import models

# Authentication Views
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('dashboard')
    
    return render(request, 'register.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# Document Management Views
@login_required
def dashboard(request):
    owned_docs = Document.objects.filter(owner=request.user)
    collaborated_docs = Document.objects.filter(collaborators=request.user)
    public_docs = Document.objects.filter(is_public=True).exclude(owner=request.user)
    
    # Get active users for all documents
    from .models import DocumentSession
    from django.utils import timezone
    from datetime import timedelta
    
    # Consider users active if they joined in the last 5 minutes
    active_threshold = timezone.now() - timedelta(minutes=5)
    
    # Get all active sessions
    active_sessions = DocumentSession.objects.filter(
        joined_at__gte=active_threshold
    ).select_related('user', 'document')
    
    # Group active users by document
    active_users_by_doc = {}
    for session in active_sessions:
        doc_id = session.document.id
        if doc_id not in active_users_by_doc:
            active_users_by_doc[doc_id] = []
        if session.user not in active_users_by_doc[doc_id]:
            active_users_by_doc[doc_id].append(session.user)
    
    context = {
        'owned_docs': owned_docs,
        'collaborated_docs': collaborated_docs,
        'public_docs': public_docs,
        'active_users_by_doc': active_users_by_doc
    }
    return render(request, 'dashboard.html', context)

@login_required
def create_document(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled Document')
        document = Document.objects.create(
            title=title,
            owner=request.user
        )
        return redirect('editor', doc_id=document.id)
    return render(request, 'create_document.html')

@login_required
def editor_view(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    
    # Check if user has access
    if not (request.user == document.owner or 
            request.user in document.collaborators.all() or 
            document.is_public):
        messages.error(request, 'You do not have permission to access this document.')
        return redirect('dashboard')
    
    context = {
        'document': document,
        'user': request.user
    }
    return render(request, 'editor.html', context)

@login_required
def document_versions(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    versions = document.versions.all()
    
    context = {
        'document': document,
        'versions': versions
    }
    return render(request, 'document_versions.html', context)


# API Views
@login_required
@csrf_exempt
def add_collaborator(request, doc_id):
    if request.method == 'POST':
        document = get_object_or_404(Document, id=doc_id, owner=request.user)
        collaborator_username = request.POST.get('username')
        
        try:
            collaborator = User.objects.get(username=collaborator_username)
            document.collaborators.add(collaborator)
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})



@login_required
@csrf_exempt
def remove_collaborator(request, doc_id):
    if request.method == 'POST':
        document = get_object_or_404(Document, id=doc_id, owner=request.user)
        collaborator_username = request.POST.get('username')
        
        try:
            collaborator = User.objects.get(username=collaborator_username)
            document.collaborators.remove(collaborator)
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
@csrf_exempt
def save_version(request, doc_id):
    if request.method == 'POST':
        import json
        from django.utils import timezone
        
        document = get_object_or_404(Document, id=doc_id)
        
        # Check if user has access
        if not (request.user == document.owner or 
                request.user in document.collaborators.all() or 
                document.is_public):
            return JsonResponse({'success': False, 'error': 'Permission denied'})
        
        try:
            data = json.loads(request.body)
            content = data.get('content', '')
            
            # Update document content
            document.content = content
            document.save()
            
            # Create version
            latest_version = document.versions.first()
            version_number = (latest_version.version_number + 1) if latest_version else 1
            
            DocumentVersion.objects.create(
                document=document,
                content=content,
                created_by=request.user,
                version_number=version_number
            )
            
            return JsonResponse({
                'success': True,
                'version_number': version_number,
                'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# REST API Viewsets
class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Document.objects.filter(
            models.Q(owner=user) |
            models.Q(collaborators=user) |
            models.Q(is_public=True)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def add_collaborator(self, request, pk=None):
        document = self.get_object()
        if document.owner != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        username = request.data.get('username')
        try:
            collaborator = User.objects.get(username=username)
            document.collaborators.add(collaborator)
            return Response({'success': True})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        document = self.get_object()
        versions = document.versions.all()
        serializer = DocumentVersionSerializer(versions, many=True)
        return Response(serializer.data)


class DocumentVersionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DocumentVersionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        document_id = self.kwargs.get('document_pk')
        return DocumentVersion.objects.filter(document_id=document_id)
