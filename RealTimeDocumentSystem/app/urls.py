from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'documents', views.DocumentViewSet, basename='document')
router.register(r'documents/(?P<document_pk>\d+)/versions', views.DocumentVersionViewSet, basename='document-version')

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Document Management URLs
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_document, name='create_document'),
    path('document/<int:doc_id>/', views.editor_view, name='editor'),
    path('document/<int:doc_id>/versions/', views.document_versions, name='document_versions'),
    
    # API URLs
    path('api/', include(router.urls)),
    path('api/document/<int:doc_id>/add-collaborator/', views.add_collaborator, name='add_collaborator'),
    path('api/document/<int:doc_id>/remove-collaborator/', views.remove_collaborator, name='remove_collaborator'),
    path('api/document/<int:doc_id>/save-version/', views.save_version, name='save_version'),
]
