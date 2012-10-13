'''

Copyright (c) 2012, Kris Lamoureux
All rights reserved.

DJ-BaseSite is released under the New BSD Liscense.
Please take a momemt to read the short 3 Clause LICENSE file.

'''


# Built in imports
import random
import hashlib

# Responce imports
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext

# Authentication/Session/Validation imports
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
# Below expected to be in same directory
import validation as v
import captcha

# Email imports
from django.core.mail import EmailMessage
from django.core import mail

# Variables from Settings.py
from settings import EMAIL_HOST_USER, baseurl, EMAIL_MESSAGE

# User Profile model
from accountprofile.models import UserProfile

# Website base title
base_title = "Base Site - "

# Global Site Navigation 
def global_nav():
	return '<a href="/">Home</a>'

# User Site Navigation 
def user_nav(user):
	if not user:
		return '<a href="/login/">Login</a> | <a href="/register/">Register</a>'	
	else:
		return '<a href="/account/">'+user+'</a> | <a href="/logout/">Logout</a>'
		
def get_or_create_profile(user):
	try:
		profile = user.get_profile()
	except ObjectDoesNotExist:
		profile = UserProfile(activated=True, user=user)
		profile.save()
	return profile

def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
	
def UserActivationKey():
	random.seed()
	choices = "abcdefghijklmnopqrstuvwxyzABCDEFG0123456789"

	word = ""
	for i in range(25):
		x = random.randrange(0,len(choices))
		word = word + choices[x]
	return word
		
		
''' PAGE REQUESTS '''
def index(request):
	global base_title
	global global_nav, user_nav
	
	# Load Global Navigation and title.
	title = base_title + "Home"
	global_navigation=global_nav()
	
	# Load user navigation based on the session
	if request.user.is_authenticated():
		user_navigation = user_nav(request.user.username)
	else:
		user_navigation = user_nav(False)
		
	responce = render_to_response('index.html', locals())
	return responce
	
def logout_user(request):
	logout(request)
	return render_to_response('auth/logged_out.html', locals())

def login_user(request):
	global base_title
	global global_nav, user_nav

	title = base_title + "Login"
	global_navigation=global_nav()
	
	# If user is not logged on
	if not request.user.is_authenticated():
	
		# Return user navigation for an anonymous session
		user_navigation = user_nav(False)
		
		# If user has sent POST data
		if request.method == 'POST':
		
			# Collect user data and return user object
			usern = request.POST['username']
			passw = request.POST['password']
			
			''' CLEAN '''
			
			user = authenticate(username=usern, password=passw)

			if user is not None:
			# If user object exists it means the user is authenticated
			# but you still need to check if the user.is_active

				if user.is_active:
					# Account is active and not disabled.
					# ... but is it activated?
					user_profile = get_or_create_profile(user)
					if user_profile.activated:
						# User account is activated (via email)
						login(request, user)
						user_name = user.username
						responce = render_to_response('auth/logged_in.html', locals())
					else:
						# The account is not activated via email
						error = "Please activate your account through email."
						responce = render_to_response('error.html', locals())						
				else:
					# The account is disabled. No login.
					message = "Your account has been disabled."
					responce = render_to_response('auth/disabled.html', locals())
					
			else:
				# No object so the username and password are invalid.
				login_errors = True
				responce = render_to_response(	
											'auth/login.html', 
											locals(), 
											context_instance=RequestContext(request)
											)

		else:
			# User isn't online and hasn't sent any POST data, give them a login form.
			responce = render_to_response(
										'auth/login.html',
										locals(),
										context_instance=RequestContext(request)
										)

	else:
		# User is logged on, don't let them login until he's logged out.
		user_navigation = user_nav(request.user.username)
		error = "You're already logged on."
		responce = render_to_response(	
									'error.html', 
									locals()
									)
	return responce

def register_user(request):
	global base_title
	global global_nav, user_nav
	
	title = base_title + "Register"
	global_navigation=global_nav()
	
	
	# If user is not logged on
	if not request.user.is_authenticated():
	
		# Return user navigation for an anonymous session
		user_navigation = user_nav(False)

		# Set up captcha html.
		from settings import captcha_publickey, captcha_privatekey
		captcha_test = captcha.displayhtml(captcha_publickey)
		
		# If user has sent POST data (not logged in)
		if request.method == 'POST':
			registration_errors = [] # Error list
			
			''' Check and validate data '''
			
			# Is human?
			HumanTestResult = captcha.submit(
											request.POST["recaptcha_challenge_field"],
											request.POST["recaptcha_response_field"],
											captcha_privatekey,
											get_ip(request)
											)

			# If not human: display errors
			if HumanTestResult.is_valid:				
				# Matching passwords?
				password = v.clean_password(request.POST["passw"])
				if not request.POST["passw"] == request.POST["repassw"]:
					registration_errors.append("Passwords don't match.")
				if password == None:
					registration_errors.append("No password entered.")
				elif password == -1:
					registration_errors.append("Passwords have to be at least 5 characters.")
				
				# Username related errors
				username = v.clean_username(request.POST["usern"])
				if username == None:
					registration_errors.append("No username entered.")
				elif username == -2:
					registration_errors.append("This username isn't available.")
				elif username == -1:
					registration_errors.append("Username's can only be 30 characters.")
				elif username == False:
					registration_errors.append("Username wasn't just characters numbers ")
					
				# Email related errors
				email = v.clean_email(request.POST["email"])
				if email == None:
					registration_errors.append("No email entered.")
				elif email == -2:
					registration_errors.append("This email already has an account.")
				elif email == -1:
					registration_errors.append("Emails can only be 245 characters.")
				elif email == False:
					registration_errors.append("Invalid email.")

			# Invalid CAPTCHA, display only that error giving no more information to the bot
			else:
				registration_errors.append("Invalid human verification code.")
				captcha_test = captcha.displayhtml(
													captcha_publickey, 
													False, 
													HumanTestResult.error_code)

			# If no errors: create user.
			if len(registration_errors) == 0:
				new_user = User.objects.create_user(
									username,
									email,
									request.POST["repassw"]
									)				
				new_user.is_active = True
				new_user.save()
				
				# Create activation key and user profile
				activation_key = UserActivationKey()
				profile = UserProfile(
									activatekey=activation_key, 
									activated=False,
									user=new_user)
				profile.save()
				
				# User is created and saved. Send an activation link via email
				connection = mail.get_connection()
				connection.open()
				
				message_activateurl = baseurl+"/activate/?key="+str(activation_key)+"&user="+str(new_user.username)
				message_deactivateurl = baseurl+"/deactivate/?key="+str(activation_key)+"&user="+str(new_user.username)
				
				f = open(EMAIL_MESSAGE, 'r')
				message = f.read()
				
				message = message.replace("<$user>", str(new_user.username))
				message = message.replace("<$activatelink>", message_activateurl)
				message = message.replace("<$disablelink>", message_deactivateurl)
				
				email = EmailMessage(
									"Account Activation", 
									message,
									EMAIL_HOST_USER,
									[new_user.email])
				email.send()
				connection.close()
				
				# Return new account page
				accountname = new_user.username
				responce = render_to_response(	
										'auth/newaccount.html', 
										locals(), 
										context_instance=RequestContext(request)
									)
			else:
				# Return registration form with errors in registration_errors
				responce = render_to_response(	
										'auth/registration.html', 
										locals(), 
										context_instance=RequestContext(request)
									)

		# If user hasn't sent POST data (not logged on)
		else:
			responce = render_to_response(	
									'auth/registration.html', 
									locals(), 
									context_instance=RequestContext(request)
								)
	# User is logged on
	else:
		user_navigation = user_nav(request.user.username)
		error = "You cannot register while logged in."
		responce = render_to_response(	
									'error.html', 
									locals()
								)
	return responce

def activate_user(request):
	if request.method == 'GET':
		# Check if data could be valid through regex
		key = v.clean_key(request.GET["key"])
		u_name = v.clean_usernameRE(request.GET["user"])
		
		# If key and username are valid
		if request.GET["key"] == key and u_name:
			try:
				# Check profile for key and compare.
				user = User.objects.get(username=u_name)
				user_profile = get_or_create_profile(user)

				if user_profile.activatekey == key:
					# Activate user
					user_profile.activated = True
					user_profile.save()
					key_correct = True
				else:
					key_correct = False
					
			except ObjectDoesNotExist:
				key_correct = False
		else:
			key_correct = False
			
	if key_correct:
		user_name = user.username
		responce = render_to_response(	
									'auth/activated.html', 
									locals()
									)
	else:
		error = "Activation failed."
		responce = render_to_response(	
									'error.html', 
									locals()
									)
		
	return responce
