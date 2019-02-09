from django.db import models
import datetime

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=32)
    uid = models.CharField(max_length=36, primary_key=True)
    pwdHash = models.BinaryField(max_length=32)
    expoPushToken = models.CharField(max_length=64)
    
    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=32)
    desc = models.CharField(max_length=256)
    loc = models.CharField(max_length=64)
    eid = models.CharField(max_length=36, primary_key=True)
    confirmed = models.IntegerField(default=0)
    confirmedMembers = models.ManyToManyField(User, related_name='group_confirmed_members')
    initTime = models.DateTimeField(default=datetime.datetime.now)
    owner = models.ForeignKey(User, related_name='event_owner', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=64)
    gid = models.CharField(max_length=36, primary_key=True)
    
    members = models.ManyToManyField(User, related_name='group_members')#, through='Membership', through_fields=('group', 'user'))
    owner = models.ForeignKey(User, related_name='group_owner', on_delete=models.CASCADE)
    GROUP_TYPE_CHOICES = (
        ('private', 'Private Group'),
        ('public', 'Public Group')
    )
    groupType = models.CharField(max_length=7, choices=GROUP_TYPE_CHOICES)
    events = models.ManyToManyField(Event, related_name='group_events')
    
    def __str__(self):
        return self.name

'''
class Membership(models.Model):
    group = models.ForeignKey(Group, related_name='group_membership', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_membership', on_delete=models.CASCADE)
    notify = models.BooleanField()
'''
