import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Document, DocumentSession, DocumentVersion

import re

logger = logging.getLogger(__name__)

class DocumentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.doc_id = self.scope['url_route']['kwargs']['doc_id']
            self.user = self.scope['user']
            self.room_group_name = f'document_{self.doc_id}'
            
            logger.info(f"User {self.user.username} attempting to connect to document {self.doc_id}")
            
            # Check if user can access this document
            if not await self.can_access_document():
                logger.warning(f"User {self.user.username} denied access to document {self.doc_id}")
                await self.close()
                return
                
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            
            logger.info(f"User {self.user.username} successfully connected to document {self.doc_id}")
            
            # Add user to active sessions
            await self.add_user_session()
            
            # Notify others that user joined
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'username': self.user.username,
                    'user_id': self.user.id
                }
            )
            
        except Exception as e:
            logger.error(f"Error in connect: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            if hasattr(self, 'room_group_name'):
                await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
                await self.remove_user_session()
                
                logger.info(f"User {self.user.username} disconnected from document {self.doc_id}")
                
                # Notify others that user left
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_left',
                        'username': self.user.username,
                        'user_id': self.user.id
                    }
                )
        except Exception as e:
            logger.error(f"Error in disconnect: {str(e)}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'edit')
            
            logger.debug(f"Received message type '{message_type}' from user {self.user.username}")
            
            if message_type == 'edit':
                await self.handle_edit(data)
            elif message_type == 'cursor_move':
                await self.handle_cursor_move(data)
            elif message_type == 'ai_suggestion_request':
                await self.handle_ai_suggestion_request(data)
            elif message_type == 'save_version':
                await self.handle_save_version(data)
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")

    async def handle_edit(self, data):
        try:
            content = data.get('content', '')
            cursor_position = data.get('cursor_position', 0)
            
            logger.debug(f"Handling edit from user {self.user.username}, content length: {len(content)}")
            
            # Save to database
            await self.save_document_content(content)
            
            # Broadcast to all users in the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_edit',
                    'content': content,
                    'cursor_position': cursor_position,
                    'user_id': self.user.id,
                    'username': self.user.username
                }
            )
        except Exception as e:
            logger.error(f"Error in handle_edit: {str(e)}")

    async def handle_cursor_move(self, data):
        try:
            cursor_position = data.get('cursor_position', 0)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_cursor',
                    'cursor_position': cursor_position,
                    'user_id': self.user.id,
                    'username': self.user.username
                }
            )
        except Exception as e:
            logger.error(f"Error in handle_cursor_move: {str(e)}")

    async def handle_ai_suggestion_request(self, data):
        try:
            text = data.get('text', '')
            suggestion = await self.get_ai_suggestion(text)
            
            await self.send(text_data=json.dumps({
                'type': 'ai_suggestion',
                'suggestion': suggestion,
                'original_text': text
            }))
        except Exception as e:
            logger.error(f"Error in handle_ai_suggestion_request: {str(e)}")

    async def handle_save_version(self, data):
        try:
            content = data.get('content', '')
            
            # Save version
            version_info = await self.save_document_version(content)
            
            if version_info:
                # Notify all users in the room about the saved version
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'version_saved',
                        'version_number': version_info['version_number'],
                        'user_id': self.user.id,
                        'username': self.user.username,
                        'timestamp': version_info['timestamp']
                    }
                )
                
                # Send confirmation to the user who saved
                await self.send(text_data=json.dumps({
                    'type': 'version_saved',
                    'version_number': version_info['version_number'],
                    'timestamp': version_info['timestamp']
                }))
        except Exception as e:
            logger.error(f"Error in handle_save_version: {str(e)}")

    async def broadcast_edit(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'edit',
                'content': event['content'],
                'cursor_position': event['cursor_position'],
                'user_id': event['user_id'],
                'username': event['username']
            }))
        except Exception as e:
            logger.error(f"Error in broadcast_edit: {str(e)}")

    async def broadcast_cursor(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'cursor_move',
                'cursor_position': event['cursor_position'],
                'user_id': event['user_id'],
                'username': event['username']
            }))
        except Exception as e:
            logger.error(f"Error in broadcast_cursor: {str(e)}")

    async def user_joined(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'username': event['username'],
                'user_id': event['user_id']
            }))
        except Exception as e:
            logger.error(f"Error in user_joined: {str(e)}")

    async def user_left(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'user_left',
                'username': event['username'],
                'user_id': event['user_id']
            }))
        except Exception as e:
            logger.error(f"Error in user_left: {str(e)}")

    async def version_saved(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'version_saved',
                'version_number': event['version_number'],
                'username': event['username'],
                'timestamp': event['timestamp']
            }))
        except Exception as e:
            logger.error(f"Error in version_saved: {str(e)}")

    @database_sync_to_async
    def can_access_document(self):
        try:
            document = Document.objects.get(id=self.doc_id)
            can_access = (self.user == document.owner or 
                         self.user in document.collaborators.all() or 
                         document.is_public)
            logger.info(f"Access check for user {self.user.username} to document {self.doc_id}: {can_access}")
            return can_access
        except Document.DoesNotExist:
            logger.warning(f"Document {self.doc_id} does not exist")
            return False
        except Exception as e:
            logger.error(f"Error in can_access_document: {str(e)}")
            return False

    @database_sync_to_async
    def save_document_content(self, content):
        try:
            document = Document.objects.get(id=self.doc_id)
            
            # Check if content actually changed
            if document.content != content:
                document.content = content
                document.save()
                
                # Create version for any significant change
                # Create version if:
                # 1. Content is substantial (more than 50 characters)
                # 2. Or if it's been more than 5 minutes since last version
                # 3. Or if this is the first version
                
                latest_version = document.versions.first()
                should_create_version = False
                
                if len(content) > 50:  # Substantial content
                    should_create_version = True
                elif not latest_version:  # First version
                    should_create_version = True
                else:
                    # Check if it's been more than 5 minutes since last version
                    from django.utils import timezone
                    from datetime import timedelta
                    time_diff = timezone.now() - latest_version.created_at
                    if time_diff > timedelta(minutes=5):
                        should_create_version = True
                
                if should_create_version:
                    version_number = (latest_version.version_number + 1) if latest_version else 1
                    
                    DocumentVersion.objects.create(
                        document=document,
                        content=content,
                        created_by=self.user,
                        version_number=version_number
                    )
                    
                    logger.info(f"Created version {version_number} for document {self.doc_id} by {self.user.username}")
                
        except Document.DoesNotExist:
            logger.error(f"Document {self.doc_id} not found when saving content")
        except Exception as e:
            logger.error(f"Error in save_document_content: {str(e)}")

    @database_sync_to_async
    def save_document_version(self, content):
        """Save a manual version of the document"""
        try:
            from django.utils import timezone
            
            document = Document.objects.get(id=self.doc_id)
            
            # Update document content
            document.content = content
            document.save()
            
            # Create version
            latest_version = document.versions.first()
            version_number = (latest_version.version_number + 1) if latest_version else 1
            
            DocumentVersion.objects.create(
                document=document,
                content=content,
                created_by=self.user,
                version_number=version_number
            )
            
            logger.info(f"Manually created version {version_number} for document {self.doc_id} by {self.user.username}")
            
            return {
                'version_number': version_number,
                'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Document.DoesNotExist:
            logger.error(f"Document {self.doc_id} not found when saving version")
            return None
        except Exception as e:
            logger.error(f"Error in save_document_version: {str(e)}")
            return None

    @database_sync_to_async
    def add_user_session(self):
        try:
            DocumentSession.objects.create(
                document_id=self.doc_id,
                user=self.user,
                session_id=self.channel_name
            )
            logger.info(f"Added user session for {self.user.username} in document {self.doc_id}")
        except Exception as e:
            logger.error(f"Error in add_user_session: {str(e)}")

    @database_sync_to_async
    def remove_user_session(self):
        try:
            DocumentSession.objects.filter(
                document_id=self.doc_id,
                user=self.user,
                session_id=self.channel_name
            ).delete()
            logger.info(f"Removed user session for {self.user.username} in document {self.doc_id}")
        except Exception as e:
            logger.error(f"Error in remove_user_session: {str(e)}")

    async def get_ai_suggestion(self, text):
        """Simple AI suggestions using basic text analysis"""
        try:
            suggestions = []
            
            # Basic grammar suggestions
            if len(text.split()) < 3:
                suggestions.append("Consider adding more detail to your sentence.")
            
            # Check for common mistakes
            common_mistakes = {
                'teh': 'the',
                'recieve': 'receive',
                'seperate': 'separate',
                'occured': 'occurred',
                'definately': 'definitely'
            }
            
            for mistake, correction in common_mistakes.items():
                if mistake in text.lower():
                    suggestions.append(f"Did you mean '{correction}' instead of '{mistake}'?")
            
            # Check sentence structure
            sentences = text.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and not sentence[0].isupper():
                    suggestions.append("Consider capitalizing the first letter of your sentence.")
            
            logger.debug(f"Generated {len(suggestions)} AI suggestions for text length {len(text)}")
            return suggestions[:3]  # Return max 3 suggestions
        except Exception as e:
            logger.error(f"Error in get_ai_suggestion: {str(e)}")
            return []
