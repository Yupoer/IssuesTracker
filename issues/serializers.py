# issues/serializers.py
from rest_framework import serializers
from .models import Issue
from django.contrib.auth import get_user_model

User = get_user_model()


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'
        read_only_fields = ['reporter', 'created_at', 'updated_at']

    def validate(self, attrs):
        # create Issue
        if not self.instance:
            #reporter create -> OPEN
            if attrs.get('status') and attrs['status'] != Issue.StatusChoices.OPEN:
                raise serializers.ValidationError({"status": "New issues must be created with status OPEN."})
            return attrs

        # edit Issue
        old_status = self.instance.status
        new_status = attrs.get('status', old_status)
        user = self.context['request'].user 

        # status change
        if old_status != new_status:
            # old_status == CLOSED
            if old_status == Issue.StatusChoices.CLOSED:
                raise serializers.ValidationError({"status": "Cannot change status of a CLOSED issue."})

            # old_status == OPEN
            if old_status == Issue.StatusChoices.OPEN:
                if user != self.instance.assignee:
                    raise serializers.ValidationError({"status": "Only the Assignee can mark this issue as IN_PROGRESS."})
                if new_status != Issue.StatusChoices.IN_PROGRESS:
                    raise serializers.ValidationError({"status": "OPEN issues can only transition to IN_PROGRESS."})

            # old_status == IN_PROGRESS
            if old_status == Issue.StatusChoices.IN_PROGRESS:
                if user != self.instance.assignee:
                    raise serializers.ValidationError({"status": "Only the Assignee can mark this issue as RESOLVED."})
                if new_status != Issue.StatusChoices.RESOLVED:
                    raise serializers.ValidationError({"status": "IN_PROGRESS issues can only transition to RESOLVED."})

            # old_status == RESOLVED
            if old_status == Issue.StatusChoices.RESOLVED:
                if new_status == Issue.StatusChoices.CLOSED:
                    if not (user == self.instance.reporter or user.is_staff):
                        raise serializers.ValidationError({"status": "Only the Reporter or an Admin can CLOSE this issue."})
                elif new_status == Issue.StatusChoices.IN_PROGRESS:
                    if user != self.instance.reporter:
                        raise serializers.ValidationError({"status": "Only the Reporter can reopen this issue."})
                else:
                    raise serializers.ValidationError({"status": "RESOLVED issues can only transition to IN_PROGRESS or CLOSED."})
            
        return attrs
        

class CommentSerializer(serializers.ModelSerializer):
    poster_username = serializers.CharField(source='poster.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'issue', 'poster', 'poster_username', 'content', 'created_at']
        read_only_fields = ['poster', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']