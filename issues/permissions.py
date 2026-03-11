# issues/permissions.py
from rest_framework import permissions

class IsReporterOrReadOnly(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return obj.reporter == request.user