# issues/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Issue
from .serializers import IssueSerializer

class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)