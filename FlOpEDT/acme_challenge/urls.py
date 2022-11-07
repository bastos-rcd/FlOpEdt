from django.conf.urls import url

from acme_challenge.views import ACMEChallengeView

urlpatterns = [
    url(r'^(?P<acme_challenge>[\w\-]+)$', ACMEChallengeView.as_view(), name='acme-challenge'),
]
