from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.ForeignKey(User, unique=True)
	activated = models.BooleanField()
	activatekey = models.CharField(max_length=25, blank=True)