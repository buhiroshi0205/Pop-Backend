from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from exponent_server_sdk import PushClient, PushMessage, DeviceNotRegisteredError
from .models import Group, User, Event
import hashlib, uuid

def getParams(request, tags):
    print(request.POST)
    return [request.POST[i] for i in tags]

def getHash(name, pwd):
    return hashlib.sha256((name+pwd).encode()).digest()

# Create your views here.

@csrf_exempt
def getUid(request):#done, tested
    [name] = getParams(request, ['name'])
    q = User.objects.filter(pk=name)
    if len(q) > 0:
        return JsonResponse({'uid': q[0].uid})
    else:
        raise Http404("you done fked up")

@csrf_exempt
def joinOpenGroup(request):#done, tested
    [uid, gid] = getParams(request, ['uid', 'gid'])
    g = Group.objects.get(pk=gid)
    u = User.objects.get(pk=uid)
    if g.groupType == 'public' or g.groupType == 'private':
        g.members.add(u)
        g.save()
        return JsonResponse({'success': 'true'})
    else:
        raise Http404("Invalid group or invalid user!")

@csrf_exempt
def addEvent(request):#done, tested
    [uid, gid, name, desc, loc] = getParams(request, ['uid', 'gid', 'name', 'desc', 'loc'])
    newEvent = Event(name=name, eid=str(uuid.uuid4()), desc=desc, loc=loc, owner=User.objects.get(pk=uid))
    newEvent.save()
    q = Group.objects.get(pk=gid)
    q.events.add(newEvent)
    q.save()

    if q.groupType == 'private' or q.groupType == 'public':
        responses = PushClient().publish_multiple([PushMessage(to=u.expoPushToken,
                                                               title='{} happening at {}!'.format(name, loc),
                                                               body=newEvent.desc,
                                                               ttl=3,
                                                               priority='high',
                                                               sound='default') for u in q.members.all()])
        for i in range(len(responses)):
            try:
                responses[i].validate_response()
            except DeviceNotRegisteredError:
                u = q.members.all()[i]
                u.expoPushToken = ''
                u.save()

    return JsonResponse({'eid': newEvent.eid})

@csrf_exempt
def deleteEvent(request):#done, BUGGY
    [uid, eid] = getParams(request, ['uid', 'eid'])
    q = Event.objects.get(pk=eid)
    g = q.group_events.all()[0]
    if uid == q.owner.uid or uid == g.owner.uid:
        g.events.remove(q)
        q.delete()
        q.save()
        return JsonResponse({'success': 'true'})
    else:
        raise Http404("Restricted access!")

@csrf_exempt
def getGroupList(request):#done, tested
    [uid] = getParams(request, ['uid'])
    gList = User.objects.get(pk=uid).group_members.all()
    return JsonResponse({'groupList': [g.gid for g in gList]})

@csrf_exempt
def getGroupInfo(request):#done, tested
    [gid] = getParams(request, ['gid'])
    g = Group.objects.get(pk=gid)
    return JsonResponse({'gid': gid,'name': g.name, 'type': g.groupType,
                         'memberList': [u.uid for u in g.members.all()],
                          'owner': g.owner.uid, 'unconfirmed': 0})

@csrf_exempt
def getEventList(request):#done, should be ok
    [gid] = getParams(request, ['gid'])
    eList = Group.objects.get(gid=gid).events.all()
    return JsonResponse({'eventList': [e.eid for e in eList]})

@csrf_exempt
def getEventInfo(request):#done, tested
    [eid, uid] = getParams(request, ['eid', 'uid'])
    q = Event.objects.get(pk=eid)
    return JsonResponse({'eid': eid, 'name': q.name,'desc': q.desc, 'loc': q.loc,
                         'status': q.confirmed, 'initTime': q.initTime.strftime('%b-%d %I:%M %p'),
                         'owner': q.owner.uid, 'isOwner': uid == q.owner.uid or uid == q.group_events.all()[0].owner.uid})

@csrf_exempt
def register(request):#done, tested
    [name, pwd] = getParams(request, ['name', 'pwd'])
    if len(User.objects.filter(name=name)) > 0: 
        raise Http404("Try another name!")
    newUser = User(name=name, uid=str(uuid.uuid4()), pwdHash=getHash(name, pwd))
    newUser.save()
    return JsonResponse({'uid': newUser.uid})

@csrf_exempt
def login(request):#done, tested
    [name, pwd] = getParams(request, ['name', 'pwd'])
    u = User.objects.get(name=name)
    if u.pwdHash == getHash(name, pwd):
        for otheruser in User.objects.all():
            if otheruser.expoPushToken == u.expoPushToken:
                otheruser.expoPushToken = ''
        return JsonResponse({'uid': u.uid})
    else:
        raise Http404("Restricted access!")

@csrf_exempt
def createGroup(request):#done, tested
    [uid, name, gtype] = getParams(request, ['uid', 'name', 'type'])
    newGroup = Group(name=name, gid=str(uuid.uuid4()), owner=User.objects.get(uid=uid), groupType=gtype)
    newGroup.save()
    newGroup.members.add(User.objects.get(uid=uid))
    newGroup.save()
    return JsonResponse({'gid': newGroup.gid})

@csrf_exempt
def removeMember(request):#done, tested
    [m_uid, uid, gid] = getParams(request, ['m_uid', 'uid', 'gid'])
    if m_uid == Group.objects.get(pk=gid).owner.uid or m_uid == uid:
        q = Group.objects.get(pk=gid)
        q.members.remove(User.objects.get(pk=uid))
        q.save()
        return JsonResponse({'status': 'success'})
    else:
        raise Http404("Restricted access!")

@csrf_exempt
def addMember(request):#done, tested
    [m_uid, uid, gid] = getParams(request, ['m_uid', 'uid', 'gid'])
    if m_uid == Group.objects.get(pk=gid).owner.uid:
        q = Group.objects.get(pk=gid)
        q.members.add(User.objects.get(pk=uid))
        q.save()
        return JsonResponse({'status': 'success'})
    else:
        raise Http404("Restricted access!")

@csrf_exempt
def deleteGroup(request):#done, BUGGY
    [gid, uid] = getParams(request, ['gid', 'uid'])
    q = Group.objects.get(pk=gid)
    if uid == q.owner.uid:
        q.delete()
        return JsonResponse({'status': 'success'})
    else:
        raise Http404("Restricted access!")

@csrf_exempt
def getUserInfo(request):#done, tested
    [uid] = getParams(request, ['uid'])
    name = User.objects.get(pk=uid).name
    return JsonResponse({'name': name})

@csrf_exempt
def confirmEvent(request):#done, tested
    [uid, eid] = getParams(request, ['uid', 'eid'])
    e = Event.objects.get(pk=eid)
    if len(e.confirmedMembers.filter(pk=uid)) == 0:
        e.confirmed += 1
        e.confirmedMembers.add(User.objects.get(pk=uid))
        e.save()

        if e.confirmed == 1:
            g = e.group_events.all()[0]
            if g.groupType == 'public':
                responses = PushClient().publish_multiple([PushMessage(to=u.expoPushToken,
                                                                       title="You'll never believe what you're missing out on!",
                                                                       body="This is a test notification",
                                                                       ttl=30,
                                                                       priority='high',
                                                                       sound='default') for u in g.members.all()])
                for i in range(len(responses)):
                    try:
                        responses[i].validate_response()
                    except DeviceNotRegisteredError:
                        u = g.members.all()[i]
                        u.expoPushToken = ''
                        u.save()

        return JsonResponse({'status': 'success'})
    else:
        raise Http404("Multiple confirmation")

@csrf_exempt
def search(request):#done, tested
    [query] = getParams(request, ['q'])
    return JsonResponse({'list': [g.gid for g in Group.objects.all()
                                  if query in g.name and g.groupType == 'public']})

@csrf_exempt
def updateToken(request):
    [token, uid] = getParams(request, ['token', 'uid'])
    u = User.objects.get(uid=uid)
    print("before: "+u.expoPushToken)
    u.expoPushToken = token
    u.save()
    print("after: "+u.expoPushToken)
    return JsonResponse({'status': 'success'})