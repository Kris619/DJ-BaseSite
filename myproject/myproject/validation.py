from re import match
from django.contrib.auth.models import User

'''
	Return Meanings
		None (no data to check)
		-1 (data too long/short)
		-2 (user exists)
		False (no match)
		data (matched, data is valid)
'''

def clean_username(data,length=30):
	if data == "":
		return None
	if len(data) <= length:
		if match("^[\w\d_]+$", data):
			try:
				user = User.objects.get(username__iexact=data)
				return -2
			except User.DoesNotExist:
				return data
		else:
			return False
	else:
		return -1
		
def clean_email(data,length=254):
	if data == "":
		return None
	if len(data) <= length:
		if match("^[\w\d._%-+]+@[\w\d._%-]+.[\w]{2,6}$", data):
			try:
				user = User.objects.get(email=data)
				return -2
			except User.DoesNotExist:
				return data
		else:
			return False
	else:
		return -1


def clean_password(data,length_min=5):
	if data == "":
		return None
	if len(data) >= length_min:
		return data
	else:
		return -1
		
		
def clean_key(data, length=25):
	if data == "":
		return None
	if len(data) == 25:
		if match("^[a-zABCDEFG0-9]+$", data):
			return data
		else:
			return False
	else:
		return -1

		
def clean_usernameRE(data):
	if match("^[\w\d_]+$", data):
		return data
	else:
		return False
	
def clean_emailRE(data):
	if match("^[\w\d._%-+]+@[\w\d._%-]+.[\w]{2,6}$", data):
		return data
	else:
		return False
	
	