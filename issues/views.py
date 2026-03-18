# issues/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from .models import Issue, Comment
from .serializers import IssueSerializer, CommentSerializer, UserSerializer
from .permissions import IsReporterOrAssigneeOrReadOnly, IsPosterOrReadOnly

User = get_user_model()

class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.select_related('reporter', 'assignee').prefetch_related('tags').all()
    serializer_class = IssueSerializer
    
    permission_classes = [IsAuthenticated, IsReporterOrAssigneeOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority', 'assignee', 'reporter']

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    # GET /api/issues/{id}/comments/
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        issue = self.get_object()
        comments = issue.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # GET /api/users/{id}/issues/
    @action(detail=True, methods=['get'])
    def issues(self, request, pk=None):
        user = self.get_object()
        issues = user.reported_issues.all()
        serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data)

    # GET /api/users/{id}/comments/
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        user = self.get_object()
        comments = user.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('poster', 'issue').all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsPosterOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(poster=self.request.user)