from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Document, DocumentVersion, DocumentSession

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class DocumentSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    collaborators = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'content', 'owner', 'collaborators', 'created_at', 'updated_at', 'is_public']
        read_only_fields = ['owner', 'created_at', 'updated_at']

class DocumentVersionSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = DocumentVersion
        fields = ['id', 'content', 'created_by', 'created_at', 'version_number']
        read_only_fields = ['created_by', 'created_at', 'version_number']

class DocumentSessionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = DocumentSession
        fields = ['id', 'user', 'session_id', 'is_active', 'joined_at']
        read_only_fields = ['user', 'joined_at']

class DocumentCollaboratorSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
