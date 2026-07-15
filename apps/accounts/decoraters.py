import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse

User = get_user_model()

def jwt_required(view_func):
    def wrapper(request, *args, **kwargs):
        token = request.COOKIES.get('access_token')
        if not token:
            return HttpResponseRedirect(reverse('accounts:login'))

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            request.user = user
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            response = HttpResponseRedirect(reverse('accounts:login'))
            response.delete_cookie('access_token')
            return response

        return view_func(request, *args, **kwargs)
    return wrapper