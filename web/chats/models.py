import uuid

from django.db import models

from auth_app.models import Account


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    online = models.ManyToManyField(to=Account, blank=True)

    def get_online_count(self):
        return self.online.count()

    def join(self, user):
        self.online.add(user)
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()

    def __str__(self):
        return f"{self.name} ({self.get_online_count()})"


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    from_user = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="messages_from_me"
    )
    to_user = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="messages_to_me"
    )
    content = models.CharField(max_length=512, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    statement = models.ForeignKey('main.Statement', on_delete=models.CASCADE, related_name="messages", null=True,
                                  blank=True)

    def __str__(self):
        return f"From {self.from_user.full_name} to {self.to_user.full_name}: {self.content} [{self.timestamp}]"
