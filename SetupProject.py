'''

Copyright (c) 2012, Kris Lamoureux
All rights reserved.

Released under the New BSD.

'''

from os import mkdir
from shutil import copy
import os.path
import traceback
		
PROJECT_HOME = "myproject"
PROJECT = ""

HERE = os.path.dirname(os.path.realpath(__file__))
HERE = HERE.replace('\\','/')

REPLACEM = []

def add_REPLACE(a):
	global REPLACEM
	REPLACEM.append(a)


def main():
	global PROJECT, PROJECT_HOME, HERE, REPLACEM
	PROJECT = raw_input("New Project Name: ")
	add_REPLACE(['<%myproject%>',PROJECT])
	mkdir(PROJECT)
	mkdir(PROJECT+'/'+PROJECT)
	
	files = []
	move = []
	
	
	'''
		The config system is a little picky, it works
		but it can be written better, and I plan to 
		update it.
	'''
	f_hand = open("./config.txt")
	config_list = f_hand.readlines()

	for config_setting in config_list:
		# take off '\n' at end of string
		config_setting = config_setting[:-1]
		
		# ignore comments.
		if config_setting[0:2] == "//":
			pass
		# ignore empty lines
		elif config_setting == "":
			pass
		# ignore newlines
		elif config_setting == "\n":
			pass
		# add file variable. (format: <%myproject%>)
		elif config_setting[0:1] == "v":
			config_setting = config_setting.split(' ')
			config_setting[1] = "<%"+config_setting[1]+"%>"
			try:
				add_REPLACE([config_setting[1],config_setting[2]])
			except IndexError:
				print "You have an empty variable in the configuration."
			except:
				traceback.print_exc()
				raw_input()
				quit()

		# Create folder for an app.
		elif config_setting[0:3] == "dir":
			config_setting = config_setting.split(' ')
			if not len(config_setting) == 3:
				mkdir(HERE+'/'+PROJECT+'/'+PROJECT+'/'+config_setting[1])
			else:
				mkdir(HERE+'/'+PROJECT+'/'+config_setting[1])
		else:
			old_path = config_setting.split(' ')[0]
			old_path= old_path.replace("%here%",HERE)
			new_path = old_path.replace("myproject", PROJECT)
			
			if config_setting.split(' ')[1] == '1':
				files.append([old_path, new_path])
			elif config_setting.split(' ')[1] == '2':
				move.append([old_path, new_path])
			else:
				print "Something went wrong here.."
				raw_input()
				exit()
	'''
		END OF CONFIG SYSTEM.
	'''
	
	
	# Cycle through files, dynamic then static.
	for dyn_file in files:
		# Open file that has vars to replace (format: <%varname%>)
		
		old_fileh = open(dyn_file[0])
		old_file = old_fileh.read()
		
		# Replace vars with data
		for var in REPLACEM:
			old_file = old_file.replace(var[0],var[1])
		
		# Write new file
		f = open(dyn_file[1], "w+")
		f.write(old_file)
		f.close()
	
	# Static cycle.
	stat_file_dir = ""
	for sta_file in move:
		if sta_file[1].find('.'):
			stat_file_dir = os.path.dirname(sta_file[1])
			copy(sta_file[0], stat_file_dir)
		else:
			copy(sta_file[0], sta_file[1])
		
	print "Project: "+PROJECT+" is ready for development.\n"
try:
	main()
except:
	traceback.print_exc()

print "Press any key to quit."
raw_input()
quit()
	