'''

Copyright (c) 2012, Kris Lamoureux
All rights reserved.

DJ-BaseSite is released under the New BSD Liscense.
Please take a momemt to read the short 3 Clause LICENSE file.

'''


# Built in imports
import random
import hashlib
import datetime

# response imports
from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponseRedirect

# Authentication/Session/Validation imports
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
# Below expected to be in same directory
import validation as v
import captcha

# Time related Django imports
from django.utils.timezone import now

# Email imports
from django.core.mail import EmailMessage
from django.core import mail

# Variables from Settings.py
from settings import EMAIL_HOST_USER, ACTIVATE_EMAIL, RECOVERY_EMAIL
from settings import captcha_publickey, captcha_privatekey
from settings import baseurl, base_title

# User Profile model
from accountprofile.models import UserProfile

# Website base title
base_title = base_title+" - "

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
		profile = UserProfile(
			activated=True,
			recovery_time=now(),
			user=user
			)
			
		profile.save()
	return profile

def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

	
def KeyGen():
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
		
	response = render_to_response('index.html', locals())
	return response
	
def logout_user(request):
	logout(request)
	user_navigation = user_nav(False)
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
						user_navigation = user_nav(user.username)
						response = render_to_response('auth/logged_in.html', locals())
					else:
						# The account is not activated via email
						error = "Please activate your account through email."
						response = render_to_response('error.html', locals())						
				else:
					# The account is disabled. No login.
					message = "Your account has been disabled."
					response = render_to_response('auth/disabled.html', locals())
					
			else:
				# No object so the username and password are invalid.
				login_errors = True
				response = render_to_response(	
					'auth/login.html', 
					locals(), 
					context_instance=RequestContext(request)
					)

		else:
			# User isn't online and hasn't sent any POST data, give them a login form.
			response = render_to_response(
				'auth/login.html',
				locals(),
				context_instance=RequestContext(request)
										)

	else:
		# User is logged on, don't let them login until he's logged out.
		user_navigation = user_nav(request.user.username)
		error = "You're already logged on."
		response = render_to_response('error.html',locals())

	return response

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
					HumanTestResult.error_code
					)
					
			# Connect to SMTP server
			connection = mail.get_connection()
			connection.open()

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
				activation_key = KeyGen()
				
				# Add 2 hours so a recovery key can be made instantly after
				# account creation.
				thetime = new_user.date_joined + datetime.timedelta(hours=2)
				
				profile = UserProfile(
					activate_key=activation_key,
					activated=False,
					recovery_time=thetime,
					user=new_user)

				profile.save()
				
				# User is created and saved. Send an activation link via email
				
				# Activation link
				message_activateurl = baseurl+"/activate/?key="+str(activation_key)
				message_activateurl = message_activateurl+"&user="+str(new_user.username)
				
				# Deactivation link
				message_deactivateurl = baseurl+"/deactivate/?key="+str(activation_key)
				message_deactivateurl = message_deactivateurl+"&user="+str(new_user.username)
				
				# Open email and replace data
				f = open(ACTIVATE_EMAIL, 'r')
				message = f.read()
				
				message = message.replace("<$user>", str(new_user.username))
				message = message.replace("<$activatelink>", message_activateurl)
				message = message.replace("<$disablelink>", message_deactivateurl)
				
				# Send email
				email = EmailMessage(
					"Account Activation", 
					message,
					EMAIL_HOST_USER,
					[new_user.email]
					)

				email.send()
				connection.close()
				
				# Return new account page
				accountname = new_user.username
				response = render_to_response(	
					'auth/newaccount.html', 
					locals(), 
					context_instance=RequestContext(request)
					)

			else:
				# Return registration form with errors in registration_errors
				response = render_to_response(	
					'auth/registration.html', 
					locals(), 
					context_instance=RequestContext(request)
					)

		# If user hasn't sent POST data (not logged on)
		else:
			response = render_to_response(	
				'auth/registration.html', 
				locals(), 
				context_instance=RequestContext(request)
				)

	# User is logged on
	else:
		user_navigation = user_nav(request.user.username)
		error = "You cannot register while logged in."
		response = render_to_response(	
									'error.html', 
									locals()
								)
	return response

def activate_user(request):
	if request.method == 'GET' and not request.user.is_authenticated():
		# Check if data could be valid through regex
		key = v.clean_key(request.GET["key"])
		u_name = v.clean_usernameRE(request.GET["user"])
		
		# If key and username are valid
		if request.GET["key"] == key and u_name:
			try:
				# Check profile for key and compare.
				user = User.objects.get(username=u_name)
				user_profile = get_or_create_profile(user)
				
				# You're already activated
				if user_profile.activated:
					key_correct = False
					
				# You're disabled.
				elif user.is_active == False:
					key_correct = False

				elif user_profile.activate_key == key:
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
			
		user_navigation = user_nav(False)

		if key_correct:
			user_name = user.username
			response = render_to_response(	
				'auth/activated.html', 
				locals()
				)
		else:
			error = "Activation failed."
			response = render_to_response(	
				'error.html', 
				locals()
				)
		
		return response

	# Logged on or didn't give GET data.
	return HttpResponseRedirect('/')
	
def deactivate_user(request):
	if request.method == 'GET' and not request.user.is_authenticated():
		# Check if data could be valid through regex
		key = v.clean_key(request.GET["key"])
		u_name = v.clean_usernameRE(request.GET["user"])
		
		# If key and username are valid
		if request.GET["key"] == key and u_name:
			try:
				# Check profile for key and compare.
				user = User.objects.get(username=u_name)
				user_profile = get_or_create_profile(user)

				# If you wish to have your users deactivate with the same 
				# link sent in activation, remove this if statement
				if user_profile.activated:
					key_correct = False
					

				elif user_profile.activate_key == key:
					# Disable account.
					user_profile.activated = False
					user_profile.save()

					user.is_active = False
					user.save()

					key_correct = True
				else:
					key_correct = False
					
			except ObjectDoesNotExist:
				key_correct = False
		else:
			key_correct = False
			
		if key_correct:
			user_name = user.username
			response = render_to_response(	
				'auth/deactivated.html', 
				locals()
				)
		else:
			error = "Deactivation failed."
			response = render_to_response(	
				'error.html', 
				locals()
				)
			
		return response

	# Logged on or didn't give GET data.
	return HttpResponseRedirect('/')
	
def recover_user(request):
	global base_title
	global global_nav, user_nav
	
	title = base_title + "Recovery"
	global_navigation=global_nav()
	
	# If user is not logged on
	if not request.user.is_authenticated():
	
		# Return user navigation for an anonymous session
		user_navigation = user_nav(False)

		# Set up captcha html.
		captcha_test = captcha.displayhtml(captcha_publickey)
		
		# If user has sent POST data (not logged in)
		if request.method == 'POST':
			# Check info via regex
			u_name = v.clean_usernameRE(request.POST["usern"])
			email = v.clean_emailRE(request.POST["email"])
			

			if email == request.POST["email"] and u_name:
				try:
					user = User.objects.get(username__iexact=u_name)
					user_profile = get_or_create_profile(user)
					
					# Current time
					time_now = now()					
					
					# Recovery time
					recovery_time = user_profile.recovery_time
					
					if time_now > recovery_time:
						# Key has been requested too many times in 2 hours.
						error = "Recovery keys can only be requested once every 2 hours."
						response = render_to_response(
							'error.html', 
							locals()
							)
					else:
						# Connect to SMTP server
						connection = mail.get_connection()
						connection.open()
						
						# Create a recovery key
						user_profile.recovery_key = KeyGen()
						user_profile.save()

						# Create account recovery link
						message_recoveryurl = baseurl+"/recover/?key="+str(user_profile.recovery_key)
						message_recoveryurl = message_recoveryurl+"&user="+str(user.username)
				
				
						# Open email template
						f = open(RECOVERY_EMAIL, 'r')
						message = f.read()
						print message
				
						# Replace information
						message = message.replace("<$user>", str(user.username))
						message = message.replace("<$recoverylink>", message_recoveryurl)
						message = message.replace("<$time>", str(user_profile.recovery_time))
				
						# Send email
						email = EmailMessage(
							"Account Recovery", 
							message,
							EMAIL_HOST_USER,
							[user.email]
							)

						email.send()
						connection.close()
						
						# Tell user to check their email.
						error = "Check your email for a recovery link."
						response = render_to_response(	
							'error.html', 
							locals()
							)

				except User.DoesNotExist:
					error = "No user with that email exists."
					response = render_to_response(	
						'error.html', 
						locals()
						)
			else:
				error = "No user with that email exists."
				response = render_to_response(	
					'error.html', 
					locals()
					)
		else:
		# Didn't submit, give recovery form.
			response = render_to_response(
				'auth/recovery.html',
				locals(),
				context_instance=RequestContext(request)
				)
	# You're signed in, no recovery for you.
	else:
		return HttpResponseRedirect('/')

	return response
	
def recover_attempt(request):
	global base_title
	global global_nav, user_nav
	
	title = base_title + "Recovery"
	global_navigation=global_nav()
	
	# If user is not logged on
	if request.method == 'GET' and not request.user.is_authenticated():
		# Check if data could be valid through regex
		key = v.clean_key(request.GET["key"])
		u_name = v.clean_usernameRE(request.GET["user"])

		
		# If valid data
		if request.GET["key"] == key and u_name:
			# return new password form
			the_user = u_name
 			the_key = key
			response = render_to_response(	
					'auth/recoveryattempt.html', 
					locals(),
					context_instance=RequestContext(request)
					)
		else:
			error = "User does not exist."
			response = render_to_response(	
					'error.html', 
					locals()
					)			
	
	# If user isn't online and is sending post data
	elif request.method == 'POST' and not request.user.is_authenticated():
		# Check if data could be valid through regex
		key = v.clean_key(request.POST["key"])
		u_name = v.clean_usernameRE(request.POST["user"])
		
		# If key/username is validated by regex
		if request.POST["key"] == key and u_name:
			try:
				# Check profile for key and compare.
				user = User.objects.get(username=u_name)
				user_profile = get_or_create_profile(user)
				
				# Get database key and key time limit
				key_db = user_profile.recovery_key
				keylimit_db = user_profile.recovery_time
				
				# Current time
				time_now = now()
				
				# If the key hasn't expired and is correct
				if now() < keylimit_db and key_db == key:

					password = v.clean_password(request.POST["p1"])
					
					recover_error = ""
					if not request.POST["p1"] == request.POST["p2"]:
						recover_error = "Passwords don't match."
					elif password == None:
						recover_error = "No password entered."
					elif password == -1:
						recover_error = "Passwords have to be at least 5 characters."
						
					# If there is an error
					if recover_error != '':
						# Set error variable for template
						error = recover_error
						
						response = render_to_response(
							'error.html',
							locals()
							)
					else:
						# No errors, change password
						user.set_password(password)
						user.save()
						
						# Expire recovery time.
						user_profile.recovery_time = now()
						user_profile.save()

						response = render_to_response(
							'auth/recoverysuccess.html',
							locals()
							)
				else:
					error = "Invalid key and/or username."
					response = render_to_response(
						'error.html',
						locals()
						)
			except User.DoesNotExist:
				error = "User doesn't exist."
				response = render_to_response(
					'error.html',
					locals()
					)
		else:
			error = "Invalid key and/or username."
			response = render_to_response(
				'error.html',
				locals()
				)
	else:
		# logged on, no recovery.
		return HttpResponseRedirect('/')
		
	return response
	