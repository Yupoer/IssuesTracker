from django.db import models
from django.contrib.auth.models import AbstractUser

#User
class User(AbstractUser):
    pass

#Tag
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#000000") # 存 Hex color

    def __str__(self):
        return self.name

#Issue
class Issue(models.Model):
    class StatusChoices(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'

    class PriorityChoices(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.OPEN)
    priority = models.CharField(max_length=20, choices=PriorityChoices.choices, default=PriorityChoices.MEDIUM)
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_issues')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_issues')
    
    tags = models.ManyToManyField(Tag, related_name='issues', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.id}] {self.title}"

#Comment
class Comment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.poster.username} on Issue #{self.issue.id}"