# issues/tests.py
import pytest
from rest_framework.test import APIClient
from issues.models import Issue
from django.contrib.auth import get_user_model

User = get_user_model()


# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def alice(db):
    return User.objects.create_user(username='alice', password='password123')


@pytest.fixture
def bob(db):
    return User.objects.create_user(username='bob', password='password123')


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(username='admin', password='password123', is_staff=True)


@pytest.fixture
def open_issue(alice, bob):
    """OPEN issue: reporter=alice, assignee=bob"""
    return Issue.objects.create(
        title='Open Issue',
        reporter=alice,
        assignee=bob,
        status=Issue.StatusChoices.OPEN,
    )


@pytest.fixture
def in_progress_issue(alice, bob):
    """IN_PROGRESS issue: reporter=alice, assignee=bob"""
    return Issue.objects.create(
        title='In Progress Issue',
        reporter=alice,
        assignee=bob,
        status=Issue.StatusChoices.IN_PROGRESS,
    )


@pytest.fixture
def resolved_issue(alice, bob):
    """RESOLVED issue: reporter=alice, assignee=bob"""
    return Issue.objects.create(
        title='Resolved Issue',
        reporter=alice,
        assignee=bob,
        status=Issue.StatusChoices.RESOLVED,
    )


@pytest.fixture
def closed_issue(alice, bob):
    """CLOSED issue: reporter=alice, assignee=bob"""
    return Issue.objects.create(
        title='Closed Issue',
        reporter=alice,
        assignee=bob,
        status=Issue.StatusChoices.CLOSED,
    )


def patch_status(client, issue, status):
    return client.patch(f'/api/issues/{issue.id}/', {'status': status}, format='json')


# ─────────────────────────────────────────────
# 1. Authentication
# ─────────────────────────────────────────────

@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_issue(client):
    """未登入使用者嘗試建立 issue 應回 401"""
    response = client.post('/api/issues/', {'title': 'Test'}, format='json')
    assert response.status_code == 401


# ─────────────────────────────────────────────
# 2. Permission
# ─────────────────────────────────────────────

@pytest.mark.django_db
def test_non_reporter_non_assignee_cannot_delete_issue(client, alice, bob, open_issue):
    """第三方使用者不能刪除不屬於自己的 issue，應回 403"""
    third_party = User.objects.create_user(username='charlie', password='password123')
    client.force_authenticate(user=third_party)
    response = client.delete(f'/api/issues/{open_issue.id}/')
    assert response.status_code == 403
    assert Issue.objects.filter(id=open_issue.id).exists()


@pytest.mark.django_db
def test_reporter_can_delete_own_issue(client, alice, open_issue):
    """Reporter 可以刪除自己的 issue"""
    client.force_authenticate(user=alice)
    response = client.delete(f'/api/issues/{open_issue.id}/')
    assert response.status_code == 204
    assert not Issue.objects.filter(id=open_issue.id).exists()


# ─────────────────────────────────────────────
# 3. Create — initial status 驗證
# ─────────────────────────────────────────────

@pytest.mark.django_db
def test_create_issue_with_non_open_status_is_rejected(client, alice):
    """新建 issue 時帶 status=IN_PROGRESS 應被拒絕，回 400"""
    client.force_authenticate(user=alice)
    response = client.post('/api/issues/', {
        'title': 'Bad Issue',
        'status': 'IN_PROGRESS',
    }, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_issue_defaults_to_open(client, alice):
    """新建 issue 不帶 status，預設為 OPEN"""
    client.force_authenticate(user=alice)
    response = client.post('/api/issues/', {'title': 'New Issue'}, format='json')
    assert response.status_code == 201
    assert response.data['status'] == 'OPEN'


# ─────────────────────────────────────────────
# 4. Serializer — Read-only fields 保護
# ─────────────────────────────────────────────

@pytest.mark.django_db
def test_serializer_read_only_fields_protection(client, alice, bob):
    """reporter 和 created_at 不能被 API payload 偽造"""
    client.force_authenticate(user=alice)
    response = client.post('/api/issues/', {
        'title': 'Hacked Issue',
        'reporter': bob.id,
        'created_at': '1999-01-01T00:00:00Z',
    }, format='json')
    assert response.status_code == 201
    issue = Issue.objects.get(title='Hacked Issue')
    assert issue.reporter == alice
    assert issue.created_at.year >= 2024


# ─────────────────────────────────────────────
# 5. Status Machine — OPEN → IN_PROGRESS
# ─────────────────────────────────────────────

@pytest.mark.django_db
def test_assignee_can_move_open_to_in_progress(client, bob, open_issue):
    """Assignee 可以把 OPEN → IN_PROGRESS"""
    client.force_authenticate(user=bob)
    response = patch_status(client, open_issue, 'IN_PROGRESS')
    assert response.status_code == 200
    open_issue.refresh_from_db()
    assert open_issue.status == Issue.StatusChoices.IN_PROGRESS


@pytest.mark.django_db
def test_reporter_cannot_move_open_to_in_progress(client, alice, open_issue):
    """Reporter 不能把 OPEN → IN_PROGRESS，應回 400"""
    client.force_authenticate(user=alice)
    response = patch_status(client, open_issue, 'IN_PROGRESS')
    assert response.status_code == 400


@pytest.mark.django_db
def test_assignee_cannot_move_open_to_resolved(client, bob, open_issue):
    """OPEN 只能轉到 IN_PROGRESS，不能直接跳 RESOLVED，應回 400"""
    client.force_authenticate(user=bob)
    response = patch_status(client, open_issue, 'RESOLVED')
    assert response.status_code == 400


# ─────────────────────────────────────────────
# 6. Status Machine — IN_PROGRESS → RESOLVED
# ─────────────────────────────────────────────

@pytest.mark.django_db
def test_assignee_can_move_in_progress_to_resolved(client, bob, in_progress_issue):
    """Assignee 可以把 IN_PROGRESS → RESOLVED"""
    client.force_authenticate(user=bob)
    response = patch_status(client, in_progress_issue, 'RESOLVED')
    assert response.status_code == 200
    in_progress_issue.refresh_from_db()
    assert in_progress_issue.status == Issue.StatusChoices.RESOLVED


@pytest.mark.django_db
def test_reporter_cannot_move_in_progress_to_resolved(client, alice, in_progress_issue):
    """Reporter 不能把 IN_PROGRESS → RESOLVED，應回 400"""
    client.force_authenticate(user=alice)
    response = patch_status(client, in_progress_issue, 'RESOLVED')
    assert response.status_code == 400


# ─────────────────────────────────────────────
# 7. Status Machine — RESOLVED → CLOSED
# ─────────────────────────────────────────────

@pytest.mark.django_db
def test_reporter_can_close_resolved_issue(client, alice, resolved_issue):
    """Reporter 可以把 RESOLVED → CLOSED"""
    client.force_authenticate(user=alice)
    response = patch_status(client, resolved_issue, 'CLOSED')
    assert response.status_code == 200
    resolved_issue.refresh_from_db()
    assert resolved_issue.status == Issue.StatusChoices.CLOSED


@pytest.mark.django_db
def test_admin_can_close_resolved_issue(client, admin_user, resolved_issue):
    """Admin 可以把 RESOLVED → CLOSED"""
    client.force_authenticate(user=admin_user)
    response = patch_status(client, resolved_issue, 'CLOSED')
    assert response.status_code == 200
    resolved_issue.refresh_from_db()
    assert resolved_issue.status == Issue.StatusChoices.CLOSED


@pytest.mark.django_db
def test_assignee_cannot_close_resolved_issue(client, bob, resolved_issue):
    """Assignee 不能把 RESOLVED → CLOSED，應回 400"""
    client.force_authenticate(user=bob)
    response = patch_status(client, resolved_issue, 'CLOSED')
    assert response.status_code == 400


# ─────────────────────────────────────────────
# 8. Status Machine — RESOLVED → IN_PROGRESS (reopen)
# ─────────────────────────────────────────────

@pytest.mark.django_db
def test_reporter_can_reopen_resolved_issue(client, alice, resolved_issue):
    """Reporter 可以把 RESOLVED → IN_PROGRESS（reopen）"""
    client.force_authenticate(user=alice)
    response = patch_status(client, resolved_issue, 'IN_PROGRESS')
    assert response.status_code == 200
    resolved_issue.refresh_from_db()
    assert resolved_issue.status == Issue.StatusChoices.IN_PROGRESS


@pytest.mark.django_db
def test_assignee_cannot_reopen_resolved_issue(client, bob, resolved_issue):
    """Assignee 不能把 RESOLVED → IN_PROGRESS，應回 400"""
    client.force_authenticate(user=bob)
    response = patch_status(client, resolved_issue, 'IN_PROGRESS')
    assert response.status_code == 400


@pytest.mark.django_db
def test_resolved_cannot_move_to_open(client, alice, resolved_issue):
    """RESOLVED 不能轉到 OPEN，應回 400"""
    client.force_authenticate(user=alice)
    response = patch_status(client, resolved_issue, 'OPEN')
    assert response.status_code == 400


# ─────────────────────────────────────────────
# 9. Status Machine — CLOSED (terminal state)
# ─────────────────────────────────────────────

@pytest.mark.django_db
def test_reporter_cannot_change_closed_issue_status(client, alice, closed_issue):
    """Reporter 不能改變 CLOSED issue 的 status，應回 400"""
    client.force_authenticate(user=alice)
    response = patch_status(client, closed_issue, 'RESOLVED')
    assert response.status_code == 400


@pytest.mark.django_db
def test_admin_cannot_change_closed_issue_status(client, admin_user, closed_issue):
    """Admin 也不能改變 CLOSED issue 的 status，應回 400"""
    client.force_authenticate(user=admin_user)
    response = patch_status(client, closed_issue, 'RESOLVED')
    assert response.status_code == 400