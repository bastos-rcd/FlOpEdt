from django.db import models
from django.conf import settings

class GameScore(models.Model):
    score = models.PositiveIntegerField()
    user = models.ForeignKey('people.User', on_delete=models.CASCADE)
