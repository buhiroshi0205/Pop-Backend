from django.db import models
import uuid

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=32)
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    saltedPwdHash = models.BinaryField(max_length=64)
    
    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=64)
    gid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    members = models.ManyToManyField(User, through='Membership', through_fields=('group', 'person'))
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    GROUP_TYPE_CHOICES = (
        ('private', 'Private Group'),
        ('public', 'Public Group')
    )
    groupType = models.CharField(max_length=7, choices=GROUP_TYPE_CHOICES)
    
    def __str__(self):
        return self.name

class Membership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
      
class Event(models.Model):
    name = models.CharField(max_length=32)
    desc = models.CharField(max_length=64)
    location = models.CharField(max_length=64)
    eid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    confirmed = models.BoolField()
    initTime = models.DateTimeField()
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    
    def __str__(self):
        return self.name
