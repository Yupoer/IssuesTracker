# issues/tests.py
import pytest
from rest_framework.test import APIClient
from issues.models import Issue
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_bob_cannot_delete_alice_issue():
    client = APIClient() 
    
    alice = User.objects.create_user(username='alice', password='password123')
    bob = User.objects.create_user(username='bob', password='password123')
    
    issue = Issue.objects.create(
        title="Alice's Secret Issue",
        description="Only Alice can delete this.",
        reporter=alice
    )
    
    
    client.force_authenticate(user=bob)
    
    response = client.delete(f'/api/issues/{issue.id}/')
    
    assert response.status_code == 403
    assert Issue.objects.filter(id=issue.id).exists() is True
    
@pytest.mark.django_db
def test_serializer_read_only_fields_protection():
    client = APIClient()
    hacker = User.objects.create_user(username='hacker', password='password123')
    victim = User.objects.create_user(username='victim', password='password123')
    
    client.force_authenticate(user=hacker)
    
    malicious_payload = {
        "title": "Hacked Issue",
        "description": "I am forging the reporter!",
        "reporter": victim.id,  
        "created_at": "1999-01-01T00:00:00Z" 
    }
    
    response = client.post('/api/issues/', malicious_payload, format='json')
    
    assert response.status_code == 201 
    created_issue = Issue.objects.get(title="Hacked Issue")
    assert created_issue.reporter == hacker
    assert created_issue.created_at.year >= 2024