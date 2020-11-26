from django.db import models
from uuid import uuid4

class Account(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False, db_index=True)
    email = models.EmailField(unique=True, blank=False)
    password = models.CharField(max_length=60, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accounts'

class Project(models.Model):
    class Status(models.IntegerChoices):
        JUST_CREATED = 0
        IN_PROGRESS = 1
        FINISHED = 2
        DROPPED = 3

    uuid = models.UUIDField(default=uuid4, editable=False, db_index=True)
    name = models.CharField(max_length=50)
    status = models.IntegerField(choices=Status.choices, default=Status.JUST_CREATED)
    author = models.ForeignKey('Account', on_delete=models.CASCADE)
    rules = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projects'

class Sentence(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False, db_index=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    words = models.JSONField()
    categories = models.JSONField()
    derivations = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sentences'
