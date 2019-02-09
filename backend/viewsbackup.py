from django.http import JsonResponse, HttpResponse, Http404
from .models import Group, User, Event
import hashlib

def getParams(request, tags):
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
def joinOpenGroup(request):#done
  	[uid, gid] = getParams(request, ['uid', 'gid'])
    g = Group.objects.get(pk=gid)
    u = User.objects.get(pk=uid)
    if g.groupType == 'public':
        g.members.add(u)
        g.save()
    else:
        raise Http404("Invalid group or invalid user!")

@csrf_exempt  
def addEvent(request):
  	[uid, gid, name, desc, loc] = getParams(request, ['uid', 'gid', 'name', 'desc', 'loc'])
    newEvent = Event(name=name, desc=desc, loc=loc, owner=User.objects.get(pk=uid))
    newEvent.save()
    q = Group.objects.get(pk=gid)
    q.add(newEvent)
    q.save()
    return JsonResponse({'eid': newEvent.eid})

@csrf_exempt  
def deleteEvent(request):
	[uid, eid] = getParams(request, ['uid', 'eid'])
    q = Event.objects.get(pk=eid)
    if uid == q.owner or uid == q.event_owner:
        q.delete()
        q.save()
    else:
        return Http404("Restricted access!")

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
                         'memberList': [u.uid for u in g.members.all()], 'owner': g.owner.uid, 'unconfirmed': 0})

@csrf_exempt
def getEventList(request):
  	[gid] = getParams(request, ['gid'])
    eList = Group.events.all()
    return JsonResponse({'list': [e.eid for e in eList]})

@csrf_exempt  	
def getEventInfo(request):
  	[eid] = getParams(request, ['eid'])
    q = Event.objects.get(pk=eid)
    return JsonResponse({'eid': eid, 'name': q.name,'desc': q.desc, 'loc': q.loc, 
                            'status': q.confirmed, 'initTime': q.initTime, 'owner': q.owner.uid})

@csrf_exempt  
def register(request):
  	[name, pwd] = getParams(request, ['name', 'pwd'])
    if len(User.objects.filter(pk=name)) > 0: Http404("Try another name!")
    newUser = User(name=name, pwdHash=getHash(name, pwd))
    newUser.save()
    return JsonResponse({'uid': newUser.uid})

@csrf_exempt  
def login(request):
  	[name, pwd] = getParams(request, ['name', 'pwd'])
    if User.objects.get(name=name).pwdHash == getHash(name, pwd):
        return JsonResponse({'uid': newUser.uid})
    else:
        return Http404("Restricted access!")

@csrf_exempt  
def createGroup(request):
  	[uid, name, gtype] = getParams(request, ['uid', 'name', 'type'])
    newGroup = Group(name=name,owner=uid, groupType=gtype)
    newGroup.save()
    return JsonResponse({'gid': newGroup.gid})

@csrf_exempt  
def removeMember(request):
  	[m_uid, uid, gid] = getParams(request, ['m_uid', 'uid', 'gid'])
    if m_uid == Group.get(pk=gid).owner or m_uid == uid:
        q = Group.get(pk=gid).members
        q.remove(User.get(pk=uid))
        q.save()
    else:
        return Http404("Restricted access!")

@csrf_exempt    
def addMember(request):
  	[m_uid, uid, gid] = getParams(request, ['m_uid', 'uid', 'gid'])
    if m_uid == Group.get(pk=gid).owner.uid:
        q = Group.get(pk=gid)
        q.members.add(User.get(pk=uid))
        q.save()
    else:
        return Http404("Restricted access!")

@csrf_exempt    
def deleteGroup(request):
  	[gid, uid] = getParams(request, ['gid', 'uid'])
    q = Group.objects.get(pk=gid)
    if uid == q.owner:
        q.delete()
        q.save()
    else:
        return Http404("Restricted access!")

@csrf_exempt  
def getUserInfo(request):
  	[uid] = getParams(request, ['uid'])
    name = User.objects.get(pk=uid).name
    return JsonResponse({'name': name})
  
@csrf_exempt  
def confirmEvent(request):
    

