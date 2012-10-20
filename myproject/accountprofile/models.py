from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.ForeignKey(User, unique=True)
	activated = models.BooleanField()
	activate_key = models.CharField(max_length=25, blank=True)
	recovery_key = models.CharField(max_length=25, blank=True)
	recovery_time = models.DateTimeField(blank=True)
