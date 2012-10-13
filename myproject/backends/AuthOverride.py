from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class CaseInsensitiveModelBackend(ModelBackend):
	def authenticate(self, username=None, password=None):
		try:
			user = User.objects.get(username__iexact=username)
			if user.check_password(password):
				return user
			else:
				return None
		except User.DoesNotExist:
				return None