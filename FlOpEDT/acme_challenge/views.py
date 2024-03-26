import os

from django.http import Http404
from django.views import View
from django.views.static import serve


class ACMEChallengeView(View):
    def get(self, request, **kwargs):
        if 'acme_challenge' in kwargs:
            filename = kwargs['acme_challenge']
            return serve(request, f'token/{filename}', os.path.join(os.path.abspath('.'), os.path.dirname(__file__)))
        raise Http404
