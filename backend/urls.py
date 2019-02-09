from django.urls import path
from . import views

app_name = 'backend'

urlpatterns = [
	path('getUid/', views.getUid),
	path('joinOpenGroup/', views.joinOpenGroup),
	path('addEvent/', views.addEvent),
	path('deleteEvent/', views.deleteEvent),
	path('getGroupList/', views.getGroupList),
	path('getGroupInfo/', views.getGroupInfo),
	path('getEventList/', views.getEventList),
	path('getEventInfo/', views.getEventInfo),
	path('register/', views.register),
	path('login/', views.login),
	path('createGroup/', views.createGroup),
	path('removeMember/', views.removeMember),
	path('addMember/', views.addMember),
	path('deleteGroup/', views.deleteGroup),
	path('getUserInfo/', views.getUserInfo),
	path('confirmEvent/', views.confirmEvent),
	path('search/', views.search),
	path('updateToken/', views.updateToken),
]