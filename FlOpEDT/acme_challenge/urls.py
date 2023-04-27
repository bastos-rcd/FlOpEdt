from django.urls import re_path

from acme_challenge.views import ACMEChallengeView

urlpatterns = [
    re_path(r'^(?P<acme_challenge>[\w\-]+)/$',
            ACMEChallengeView.as_view(), name='acme-challenge'),
]
