from django.http import HttpRequest, HttpResponse


# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, world. You're at the polls index.")
