# issues/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Issue
from .serializers import IssueSerializer
from .permissions import IsReporterOrReadOnly


class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.select_related('reporter', 'assignee').prefetch_related('tags').all()
    serializer_class = IssueSerializer
    
    permission_classes = [IsAuthenticated, IsReporterOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority', 'assignee', 'reporter']

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)