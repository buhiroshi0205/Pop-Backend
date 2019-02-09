from django.http import JsonResponse, HttpResponse

# Create your views here.
def test(request):
	return JsonResponse({'Tartanhacks': 'test test'})

def login(request):
	return HttpResponse('success!')