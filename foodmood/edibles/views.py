from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_safe


# Create your views here.
@require_safe
def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, world. You're at the polls index.")
