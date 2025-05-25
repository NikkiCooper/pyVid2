#  PlayVideo.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Class that plays the video and updates all information dialog boxes ETC.
#
import os
import datetime
import cachetools
import subprocess

# This must be called BEFORE importing pygame
# else set it in ~/.bashrc
# Or run it from the command line:
# PYGAME_HIDE_SUPPORT_PROMPT=1 pyvid [options] (more trouble than what its worth)
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import sys
import time
import random
import pygame
from pygame.locals import *
from fractions import Fraction
from pyvidplayer2.video_pygame import VideoPygame
from pyvidplayer2 import Video
import pyvidplayer2
from DrawVideoInfo import DrawVideoInfo

class PlayVideo:
	def __init__(self, opts: object, videoList: list, bcolors: object) -> None:
		"""
		A class which plays videos
		:param opts: Contains all of our command line argument flags
		:type opts:
		:param videoList: A list which has all the path/filenames of the vids to be played
		:type videoList:
		:param bcolors:   Class object to give colors in the python console
		:type bcolors:
		"""
		self.opts = opts
		self.bcolors = bcolors
		self.vid = None
		self.reader = None
		# A list containing the path/filenames of each video to be played
		self.videoList = videoList
		self.USER_HOME = None

		self.drawVidInfo = None
		#  flag to decide if we display the  video info box or not
		self.video_info_box = False
		# Flag to render the video info box tooltip
		self.video_info_box_tooltip = False
		self.video_info_box_tooltip_mouse_x = 0
		self.video_info_box_tooltip_mouse_y = 0

		'''
		There are no entries in self.videoList,
		so no point in continuing.
		Just exit the program instead.
		'''

		if len(self.videoList) == 0:
			print("No playable media files were found.  Exiting.")
			exit(128)
		# index to access the video elements in self.vidoeList
		self.currVidIndx = -1
		# Flag that denotes we are wanting to play a previously played video.
		self.backwardsFlag = False
		# Flag that denotes we are wanting to play the next video
		self.forwardsFlag = False
		# Default volume
		self.vol: float = 0.20
		self.volume = self.vol
		self.vol_rect = None
		self.play_speed_rect = None
		self.fileNum = 0
		self.pause = None
		self.muted = False
		self.key_mute_flag = self.opts.key_mute_flag
		self.mute_flag = self.opts.mute
		self.savePlayListFlag = False
		self.savePlayListPath = ""
		self.smoothscaleBackend = ""
		# Flag for seek forward/backwards progress meter
		self.progress_active = False
		self.progress_percentage = 0
		self.last_update_time = 0
		self.progress_timeout = 60
		self.progress_value = 0
		self.current_position = 0
		self.total_duration = 0

		# displayVideoInfo
		self.status_bar_visible = False
		self.seek_flag2 = False
		self.lastflag2 = False
		self.last_vid_info_pos = 0.0

		#
		self.disableSplash = False

		# The Width and Height of the Video Splash
		self.Splash_Width = 800
		self.Splash_Height = 400
		self.image_surface = None
		self.shuffleSplashFlag = False

		# screenshot splash
		self.saveScreenShotFlag = False
		self.save_sshot_error = None
		#self.SCREEN_SHOT_DIR = self.USER_HOME + '/pyVidScreenShots'
		self.SCREEN_SHOT_DIR = None
		#
		# Set some environment variables BEFORE initializing pygame
		self.__environmentSetup()

		#pygame.mixer.init(frequency=44100, channels=2 )
		# Initialize pygame
		pygame.init()
		pygame.display.init()
		#self.bcolors.clear()
		self.dFlags =  pygame.FULLSCREEN | pygame.NOFRAME
		self.win = pygame.display.set_mode((0, 0), self.dFlags)
		self.displayWidth = self.win.get_width()
		self.displayHeight = self.win.get_height()
		# Might use this in the future
		pygame.transform.set_smoothscale_backend(self.smoothscaleBackend)
		self.clock = pygame.time.Clock()

		# OSD Icons.
		# The width and height of self.OSD_ICON_X & self.OSD_ICON_Y will be taken off the play icon.
		# Therefore, ALL icons must have the same width and height and their backgrounds must be transparent.
		self.RESOURCES_DIR = self.USER_HOME + "/.local/share/pyVid/Resources/"
		self.playIcon = pygame.image.load(self.RESOURCES_DIR + "play.png").convert_alpha()
		self.pauseIcon = pygame.image.load(self.RESOURCES_DIR + "pause.png").convert_alpha()
		self.forwardIcon = pygame.image.load(self.RESOURCES_DIR + "forward10s.png").convert_alpha()
		self.rewindIcon = pygame.image.load(self.RESOURCES_DIR + "rewind10s.png").convert_alpha()
		# x,y coordinates of the OSD play/pause icons
		self.OSD_ICON_X = 50
		self.OSD_ICON_Y = 28
		self.OSD_ICON_WIDTH = self.playIcon.get_width()
		self.OSD_ICON_HEIGHT = self.playIcon.get_height()
		# x, y coordinates of the OSD text
		self.OSD_TEXT_X = 100
		self.OSD_TEXT_Y = 0
		# y coordinate of the OSD filename
		# Note that the x coordinate is centered onto the width of the screen so only the y coordinate needs to be specified.
		self.OSD_FILENAME_Y = self.displayHeight - 100
		# Other OSD vars and flags
		self.osd_text_width = 0
		self.osd_text_height = 0
		self.draw_OSD_active = False
		self.OSD_curPos_flag = False
		self.seek_flag = False
		self.last_osd_position = 0.0
		self.seekFwd_flag = False
		self.seekRewind_flag = False

		''' 
		Setup some fonts to be used by the status bar.
		ToDo:  Setup some default backup fonts incase my choice of fonts are not installed.
		'''
		self.FONT_DIR = self.USER_HOME + "/.local/share/pyVid/fonts/"
		self.font_italic = pygame.font.Font(self.FONT_DIR + 'RobotoCondensed-Italic.ttf', 18)
		self.font_bold_italic = pygame.font.Font(self.FONT_DIR + 'Roboto-BoldItalic.ttf', 18)
		self.font_regular = pygame.font.Font(self.FONT_DIR + 'RobotoCondensed-Regular.ttf', 18)
		self.font_bold_regular = pygame.font.Font( self.FONT_DIR + 'Roboto-Bold.ttf', 18)
		self.font_regular_28 = pygame.font.Font(self.FONT_DIR + 'RobotoCondensed-Regular.ttf', 28)
		self.font_regular_32 = pygame.font.Font( self.FONT_DIR + 'RobotoCondensed-Regular.ttf', 32)
		self.font_regular_36 = pygame.font.Font( self.FONT_DIR + 'RobotoCondensed-Regular.ttf', 36)
		self.font_regular_50 = pygame.font.Font(self.FONT_DIR + 'RobotoCondensed-Regular.ttf',  50)
		self.font_bold_regular_75 = pygame.font.Font(self.FONT_DIR + 'Roboto-Bold.ttf',75)

		# Referenced in addShadowEffect()
		self.font = None

		# Location of the thumbnail cache directory
		self.CACHE_DIR = self.USER_HOME + '/.local/share/pyVid/thumbs'
		# Create a thumbnail cache with a maximum of 25 entries that reside in memory.
		self.thumbnail_cache = cachetools.LRUCache(maxsize=25)

	def addShadowEffect(self, screen, font, video_name, org_dur, cur_dur, play_speed, curPos):
		#self.font = font
		shadow_color = pygame.color.THECOLORS['red']
		text_color = pygame.color.THECOLORS['white']
		position = (self.displayWidth // 2, self.displayHeight - 12)

		if play_speed % 1 == 0:                         # Check if play_speed is a whole number
			formatted_value = f"{int(play_speed)}"      # Drop the decimal part
		else:
			formatted_value = f"{play_speed:.1f}"
		play_speed_str = ('[' + formatted_value + 'X]').rjust(3)
		info_text = f"{video_name} | {org_dur}-->{cur_dur} {play_speed_str} | {curPos}"
		# Draw shadow
		shadow_surface = self.font.render(info_text, True, shadow_color)
		shadow_rect = shadow_surface.get_rect(center=(position[0] + 2, position[1] + 2))  # Offset shadow
		screen.blit(shadow_surface, shadow_rect)

		# Draw main text
		text_surface = self.font.render(info_text, True, text_color)
		text_rect = text_surface.get_rect(center=position)
		screen.blit(text_surface, text_rect)

	@staticmethod
	def format_playback_speed(playback_speed):
		# If playback_speed is a whole number, display it as an integer (e.g., 2X)
		if playback_speed.is_integer():
			return f"[ {int(playback_speed)}X ]"  # Remove th e decimal part
		# Otherwise, display with one decimal place (e.g., 2.5X)
		return f"[ {playback_speed:.1f}X ]"

	def displayVideoInfo(self, screen, video_name, org_dur, cur_dur, play_speed, vol,  curPos):

		"""
		This function is a video info status bar. This is unecessarily complex due to
		each text segment having its own unique color. C'est vie!  Below is the layout:

		+-----------------------------------------------------------------------------------+
		| Playing  15 of 300:   Princess-Video-125     10:00-->04:00[2.5x]   [100%]   03:30 |
		+-----------------------------------------------------------------------------------+

			Text in bar            Text variable                  Description
		+---------------------------------------------------------------------------------------------------------------+
			"Playing"             play_status_text      Otherwise prints PAUSED if the video is paused.
			"15 of 300"           file_number_text      Currently playing video "15 out of 300"
			"Princess-Video-125   video_name_text       Name of the currently playing Video
			"10:00"               org_dur_text          The duration of the video in MM:SS at normal speed.
			 -->                  arrow_text            Delimiter between the "org_dur" time and the "cur_dur" time.
			"04:00"               cur_dur_text          The duration of the video in MM:SS based on its playback speed
			"[2.5X]"              play_speed_text       The speed the video is currently playing at.
			"[100%]               vol_text              The volume meter text. Ranges from 0% - 100% in 10% increments.
			"03:30"		          curPos_text           The current playback position in MM:SS
		+----------------------------------------------------------------------------------------------------------------+
		NOTES:
		The "video_name_text" is enclosed in []'s if the video has been flagged via the 'l' key in the keyboard eventhandler.
		'l' means 'loop', play the file repeatedly. Once flagged, the color of the video name will also change to denote
		It has been flagged to be repeatedly played.

		10:00-->04:00[2.5X]  sequence deserves  explination.  If the play_speed is set to 1X, it will look like this: 10:00[1X].
		Otherwise, the right hand timing will reflect the playtime in MM:SS based on the play_speed the video is being played at.

		The Volume Control meter indicates the volume in 10% increments ranging from [ 0% ] - [ 100% ].  If the mute key 'm'
		is proessed, it will change to: "[ Muted ]"

		The entire bar prints on a semi-transparent background rectangle, large enough to contain all the necesary information.
		This is done to help make it more legible.

		Every variable  has  text, color the text will be rendered in,  a pygame surface the text is rendered onto,
		Every surface object has an associated rectangle that represents the size and dimensions of each text segment.
		These surface segments are then blitted (copied) onto a semi-transparent  background that has already been copied
		to the main  screen where the video is showing.  Refer to vid.draw() in self.play()
		"""
		pct = str(int(round(100 * vol)))
		arrow_surface   =   None
		arrow_rect      =   None
		cur_dur_surface =   None
		cur_dur_rect    =   None
		position = (self.displayWidth //2 - 285, self.displayHeight - 28)

		# Define the colors for each text segment
		play_status_color   =   (pygame.color.THECOLORS['white']
									if self.vid.paused is False else pygame.color.THECOLORS['yellow'])
		video_name_color    =   (pygame.color.THECOLORS['aqua']
									if self.opts.loop_flag is True else pygame.color.THECOLORS['green'])
		file_number_color   =   pygame.color.THECOLORS['magenta']
		org_dur_color       =   pygame.color.THECOLORS['magenta']
		cur_dur_color       =   pygame.color.THECOLORS['sienna1']
		curPos_color        =   pygame.color.THECOLORS['green']
		arrow_color         =   pygame.color.THECOLORS['cyan']
		play_speed_color    =   (pygame.color.THECOLORS['red1']  if int(round(play_speed)) != 1 else pygame.color.THECOLORS['yellow'])
		vol_color           =   (pygame.color.THECOLORS['white'] if self.vid.muted is False else pygame.color.THECOLORS['red'])

		# Break down the info text into parts
		play_status_text    =   f"Paused  " if self.vid.get_paused() is True else f"Playing "
		file_number_text    =   f"{self.currVidIndx + 1} of {len(self.videoList)}:  "
		video_name_text     =   f"[ {video_name} ] " if self.opts.loop_flag is True else f"{video_name} "
		play_speed_text     =   self.format_playback_speed(play_speed)

		raw_position        =   curPos
		corrected_position  =   round(raw_position / play_speed, 1)

		if not hasattr(self, "last_vid_info_pos"):
			self.last_vid_info_pos = corrected_position

		if hasattr(self, "seek_flag2") and self.seek_flag2:
			self.last_vid_info_pos = corrected_position
			self.seek_flag2 = False

		if corrected_position < self.last_vid_info_pos:
			corrected_position = self.last_vid_info_pos

		self.last_vid_info_pos = corrected_position

		#curPos_text        =   f"   {curPos}"
		curPos_text         =   f"   {self.format_duration(corrected_position)}"
		org_dur_text        =   f"   {org_dur}"
		vol_text            =   f"   [ {pct}% ]   " if self.vid.muted is False else f"   [ Muted ]   "

		# Render each part separately with its color
		play_status_surface =   self.font_regular.render(play_status_text, True, play_status_color)
		file_number_surface =   self.font_regular.render(file_number_text, True, file_number_color)
		video_name_surface  =   (self.font_bold_italic.render(video_name_text, True, video_name_color)
								 if self.opts.loop_flag is True else self.font_regular.render(video_name_text, True, video_name_color))
		org_dur_surface     =   self.font_regular.render(org_dur_text, True, org_dur_color)
		play_speed_surface  =   self.font_regular.render(play_speed_text, True, play_speed_color)
		vol_surface         =   self.font_regular.render(vol_text, True, vol_color)
		curPos_surface      =   self.font_bold_regular.render(curPos_text, True, curPos_color)

		base_x, base_y      =   position
		play_status_rect    =   play_status_surface.get_rect(topleft=(base_x, base_y))
		file_number_rect    =   file_number_surface.get_rect(topleft=(play_status_rect.right + 8, base_y))
		video_name_rect     =   video_name_surface.get_rect(topleft=(file_number_rect.right + 12, base_y))
		org_dur_rect        =   org_dur_surface.get_rect(topleft=(video_name_rect.right + 5, base_y))

		'''
		do the following block of code
		if play_speed is not equal to 1
		'''
		if play_speed != 1.0:
			arrow = '-->'
			arrow_text      =   f"{arrow}"
			arrow_surface   =   self.font_regular.render(arrow_text, True, arrow_color)
			arrow_rect      =   arrow_surface.get_rect(topleft=(org_dur_rect.right + 3, base_y))
			cur_dur_text    =   f"{cur_dur}"
			cur_dur_surface =   self.font_regular.render(cur_dur_text, True, cur_dur_color)
			cur_dur_rect    =   cur_dur_surface.get_rect(topleft=(arrow_rect.right + 5, base_y))
			self.play_speed_rect =   play_speed_surface.get_rect(topleft=(cur_dur_rect.right + 6, base_y))
		else:
			self.play_speed_rect =   play_speed_surface.get_rect(topleft=(org_dur_rect.right + 6, base_y))

		self.vol_rect        =   vol_surface.get_rect(topleft=(self.play_speed_rect.right + 20, base_y ))
		curPos_rect          =   curPos_surface.get_rect(topleft=(self.vol_rect.right + 6, base_y))

		# Calculate a background rectangle large enough for all text
		background_rect = pygame.Rect(
			play_status_rect.left - 10,                         # Add padding to the left
			play_status_rect.top - 5,                           # Add padding to the top
			curPos_rect.right - play_status_rect.left + 20,     # Width spans all text
			play_status_rect.height + 10                        # Add padding to the height
		)

		# Draw the semi-transparent background
		background_surface = pygame.Surface((background_rect.width, background_rect.height), pygame.SRCALPHA)
		background_surface.fill((0, 0, 0, 200))                 # Black with 150 alpha (semi-transparent)
		screen.blit(background_surface, background_rect.topleft)

		# Draw each part of the text onto the screen
		screen.blit(play_status_surface, play_status_rect)      # Left-most part of the status bar
		screen.blit(file_number_surface, file_number_rect)      # File xxx of yyy
		screen.blit(video_name_surface, video_name_rect)        # Name of the video
		screen.blit(org_dur_surface, org_dur_rect)              # original duration in MM:SS (1X speed)

		'''
		if play_speed is NOT equal to 1,
		go ahead and blit the arrow_surface &  arrow_rect
		to the screen.
		Do the same thing for cur_dur_surface & cur_dur_rect
		'''
		if play_speed != 1.0:                                   # If the "play_speed" is not running at 1X:
			screen.blit(arrow_surface, arrow_rect)              # blit the "arrow" and "cur_dur":  Thus:  -->cur_dur
			screen.blit(cur_dur_surface, cur_dur_rect)          # The "cur_dur" is the length of the video in MM:SS based on the "play_speed"
																# For example: if the video is running at 1X speed and "org_dur" is 10:00,
																# then if "play_speed" is [2X], then "cur_dur" will be half of "org_dur" or 05:00

		screen.blit(play_speed_surface, self.play_speed_rect)        # Show "play_Speed" in brackets: I.E.  [2X]
		screen.blit(vol_surface, self.vol_rect)                      # Next show the volume indicator:  I.E.  [100%] or [ 50% ] or [ Muted ] even.
		screen.blit(curPos_surface, curPos_rect)                # Last, show the current play position in MM:SS. This is on the far extreme Right of the bar.

	@staticmethod
	def quit():
		"""
		Method to quit pygame and then exit the application.
		:return:
		:rtype:
		"""
		pygame.quit()
		# The following is needed to fix the terminal not echoing to the terminal when program ends. 
		output = os.popen("stty -a").read()
		if "-echo" in output:
			os.system("stty echo")
			time.sleep(0.1)
		exit()

	def __environmentSetup(self):
		"""
		Method to set or get necessary environment variables
		:return:
		:rtype:
		"""

		# Get users home directory
		if "HOME" in os.environ:
			self.USER_HOME = os.environ["HOME"]
			# This should never happen.  But may as well be redundant ...
			if not os.path.isdir(os.path.expanduser(self.USER_HOME)):
				print(f"{self.bcolors.FAIL}Cannot determine user $HOME directory.")
				exit(99)

			# Check for the env var 'SMOOTHSCALE_BACKEND'
		if "SMOOTHSCALE_BACKEND" in os.environ:
			self.smoothscaleBackend = os.environ["SMOOTHSCALE_BACKEND"]
		elif self.smoothscaleBackend not in ['SSE', 'MMX', 'GENERIC']:
			self.smoothscaleBackend = 'SSE'

		if "PYGAME_DISPLAY" not in os.environ:
			os.environ["PYGAME_DISPLAY"] = self.opts.display
		else:
			self.opts.display = os.environ["PYGAME_DISPLAY"]

		# For multi-monitor setups, this is absolutely necessary to avoid the video minimizing when it loses focus.
		if "SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS" not in os.environ:
			os.environ["SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS"] = "0"

		# The path the playlist saves to can be set in an environment variable
		if "SAVE_PLAYLIST_PATH" in os.environ:
			self.savePlayListPath = os.environ["SAVE_PLAYLIST_PATH"]
			if not os.path.isdir(os.path.expanduser(self.savePlayListPath)):
				self.savePlayListPath = os.path.expanduser("~")
		else:
			# No environment variable, so set the path to ~
			self.savePlayListPath = os.path.expanduser("~")

		# Screenshot directory.  Note that self.check_SSHOT_dir() will create the directory if it doesn't exit.
		if "SCREEN_SHOT_DIR" in os.environ:
			self.SCREEN_SHOT_DIR = os.environ["SCREEN_SHOT_DIR"]
		else:
			# Default if no environment exists
			self.SCREEN_SHOT_DIR = self.USER_HOME + '/pyVidScreenShots'
			
	def shuffleVideoList(self):
		"""
		Method to shuffle self.videoList
		:return:
		:rtype:
		"""
		random.shuffle(self.videoList)
		random.shuffle(self.videoList)

	@staticmethod
	def update():
		"""
		Helper method to update the pygame screen
		:return:
		:rtype:
		"""
		pygame.display.update()

	def savePlayList(self, filename):
		_File = self.savePlayListPath + '/' + filename
		with open(_File, "w") as file:
			for line in self.videoList:
				file.write(str(line) + "\n")

	def getResolutions(self):
		"""
		Method to help center the video onto the screen
		:return: Tuple containing the x and y positions.
		:rtype: tuple
		"""
		vid_width = self.vid.current_size[0]
		vid_height = self.vid.current_size[1]
		return (self.displayWidth - vid_width) // 2, (self.displayHeight - vid_height) // 2

	def saveSplash(self, path, filename):
		text_color = pygame.color.THECOLORS['white']
		# Define box dimensions
		box_width, box_height = 300, 125
		box_x = (self.displayWidth - box_width) // 2
		box_y = (self.displayHeight - box_width) // 2

		# Create a semi-transparent surface for the box
		box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)  # Allows transparency
		box_surface.fill((16, 78, 139, 200))  # RGBA: (R, G, B, Alpha), 150 = semi-transparent

		message_lines = [f"Saving {filename} to: ", os.path.expanduser(path)]

		# Blit semi-transparent box
		self.win.blit(box_surface, (box_x, box_y))

		# Render and position text
		line_spacing = 25
		for i, line in enumerate(message_lines):
			text_surface = self.font_regular.render(line, True, text_color)
			text_rect = text_surface.get_rect(center=(self.displayWidth // 2, box_y + 50 + i * line_spacing))
			self.win.blit(text_surface, text_rect)
		pygame.display.flip()

	def shuffleSplash(self):
		text_color = pygame.color.THECOLORS['white']

		# Define box dimensions
		box_width, box_height = 300, 125
		box_x = (self.displayWidth - box_width) // 2
		box_y = (self.displayHeight - box_width) // 2

		# Create a semi-transparent surface for the box
		box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)  # Allows transparency
		box_surface.fill((16, 78, 139, 200))  # RGBA: (R, G, B, Alpha), 150 = semi-transparent

		message_line = "Randomizing master playlist..."

		# Blit semi-transparent box
		self.win.blit(box_surface, (box_x, box_y))

		# Render and position text
		line_spacing = 25
		text_surface = self.font_regular.render(message_line, True, text_color)
		text_rect = text_surface.get_rect(center=(self.displayWidth // 2, box_y + 35 + line_spacing))
		self.win.blit(text_surface, text_rect)
		pygame.display.flip()

	def volume_bar(self, volume, _muted):
		"""
		Helper method for format_output() that creates the volume bar
		:param volume: The volume to represent in the bar
		:type volume: float
		:param _muted: Prints 'Muted' instead of the volume bar if True
		:type _muted: bool
		:return: String representing the actual volume bar
		:rtype: str
		"""
		bar_length = int(round(volume * 10))  # Scale to 10 levels
		return "[" + "=" * bar_length + " " * (10 - bar_length) + "]" + (
				str(int(round(100 * volume))) + "%") if not _muted else self.bcolors.FAIL + " Muted ".rjust(9)

	@staticmethod
	def float_to_fraction_aspect_ratio(aspect_ratio):
		"""
		Method to convert an aspect ratio represented in data type of float to a fraction.
		:param aspect_ratio:
		:type aspect_ratio: float
		:return: Fractional aspect ratio such as 16:9
		:rtype: str
		"""
		# Convert the float aspect ratio to a Fraction
		fraction = Fraction(aspect_ratio).limit_denominator()
		return f"{fraction.numerator}:{fraction.denominator}"

	@staticmethod
	def format_seconds(seconds):
		"""
		Helper method to format seconds to HH:MM:SS format.
		:param seconds: Total duration in seconds
		:type seconds: int
		:return: Formatted duration string (HH:MM:SS)
		:rtype: str
		"""
		hours, remainder = divmod(seconds, 3600)  # Separate hours
		minutes, seconds = divmod(remainder, 60)  # Separate minutes and seconds

		return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

	@staticmethod
	def format_duration(seconds):
		"""
		Helper method to format seconds to MM:SS format
		:param seconds:
		:type seconds:
		:return:
		:rtype:
		"""
		minutes, seconds = divmod(seconds, 60)
		return f"{int(minutes):02}:{int(seconds):02}"

	def format_output(self, vid_paused, index, num_vids, video_name, volume: float, muted: bool, vid_aspect_ratio,
					  resolution, new_resolution, org_duration, current_duration, playback_speed, curPos):
		"""
		Method to print a single line status bar about the currently playing video on a single line in the console.
		This function is really for debug purposes, but eventually will be used as a status line in pygame to control
		the video via a mouse or keyboard.
		:param vid_paused:
		:type vid_paused: bool
		:param index:
		:type index: int
		:param num_vids:
		:type num_vids: int
		:param video_name:
		:type video_name: str
		:param volume:
		:type volume: float
		:param muted:
		:type muted: bool
		:param vid_aspect_ratio:
		:type vid_aspect_ratio: float
		:param resolution: WidthxHeight of video
		:type resolution: tuple
		:param new_resolution: Resized WidthxHeight of scaled video.
		:type new_resolution: tuple
		:param org_duration: Original duration of video at 1X playback speed
		:type org_duration: str
		:param current_duration: New duration of video based on the playback speed of video.
		:type current_duration: str
		:param playback_speed: The desginated playback speed of the video.
		:type playback_speed: float
		:param curPos: Current position of video playback in MM:SS
		:type curPos: str
		:return:
		:rtype:
		"""
		# Define column widths
		index_width = 13
		name_width = 20
		volume_meter_width = 16
		aspect_ratio_width = 8
		res_width = 11
		new_res_width = 11
		arrow_width = 3
		org_duration_width = 4
		current_duration_width = 5
		playback_speed_width = 3

		# Special strings
		arrow = '-->'

		# Format each column
		play_string = f"PAUSED:" if vid_paused else f"Playing:"
		# index
		index_str = (str(index) + ' of ' + str(num_vids)).ljust(index_width)
		# Video Name
		name_str = video_name.ljust(name_width)[:name_width]  # Truncate if too long
		# Loop indicator
		loop_str = (self.bcolors.WARNING + "R".ljust(2)) if self.opts.loop_flag is True else self.bcolors.White_f + "".ljust(0)
		# Volume meter
		volume_meter_str = self.volume_bar(volume, muted).ljust(volume_meter_width)
		# Aspect Ratio
		fractional_aspect_ratio_str = self.float_to_fraction_aspect_ratio(vid_aspect_ratio).rjust(aspect_ratio_width)
		# Original Resolution
		res_str = ('[' + str(resolution[0]) + 'x' + str(resolution[1]) + ']').rjust(res_width)
		# compare resolution tuples
		if resolution == new_resolution:
			# disable arrow
			arrow_strL = "".ljust(0)
			# disable new_res_string
			new_res_str = "".rjust(0)
		else:
			# Place arrow
			arrow_strL = arrow.ljust(arrow_width)
			# Resized Resolution
			new_res_str = ('[' + str(new_resolution[0]) + 'x' + str(new_resolution[1]) + ']').rjust(new_res_width)
		# Normal speed duration of video
		org_duration_str = org_duration.ljust(org_duration_width)
		# Arrow
		arrow_str = arrow.rjust(arrow_width)
		# Duration based on playback speed
		current_duration_str = current_duration.ljust(current_duration_width)
		# The playback speed
		if playback_speed % 1 == 0:
			formatted_value = f"{int(playback_speed)}"
		else:
			formatted_value = f"{playback_speed:.1f}"
		playback_speed_str = ('[' + formatted_value + 'X]').rjust(playback_speed_width)

		# Combine formatted columns
		print(
			f"\r"
			f"{self.bcolors.BOLD}"
			f"{self.bcolors.White_f}"
			f"{play_string}"
			f" {self.bcolors.Magenta_f}"
			f"{index_str}"
			f"{self.bcolors.OKGREEN}"
			f"{name_str}  "
			f"{self.bcolors.White_f}"
			f"| "
			f"{loop_str}"
			f"{self.bcolors.White_f}"
			f"| "
			f"{self.bcolors.Cyan_f}"
			f"{volume_meter_str}"
			f"{self.bcolors.White_f}"
			f" |"
			f"{self.bcolors.HEADER}"
			f"{fractional_aspect_ratio_str}  "
			f"{self.bcolors.White_f}"
			f"| "
			f"{self.bcolors.Blue_f}"
			f"{res_str}"
			f"{self.bcolors.White_f}"
			f"{arrow_strL}"
			f"{self.bcolors.Blue_f}"
			f"{new_res_str} "
			f"{self.bcolors.White_f}"
			f"| "
			f"{self.bcolors.WARNING}"
			f"{org_duration_str}"
			f"{self.bcolors.White_f}"
			f"{arrow_str}"
			f"{self.bcolors.WARNING}"
			f"{current_duration_str} "
			f"{self.bcolors.Cyan_f}"
			f"{playback_speed_str} "
			f"{self.bcolors.White_f}"
			f"|"
			f"{self.bcolors.OKGREEN}"
			f" {curPos}  "
			, end=""
		)

	def next_video(self):
		# Function to advance video
		self.forwardsFlag = True
		# Disable video loop for current video before advancing to the next one.
		if self.opts.loop_flag:
			self.opts.loop_flag = False
		self.vid.stop()
		self.vid.close()

	def previous_video(self):
		# Fucntion to go back
		# Disable video loop for current video before going back to the previous one.
		if self.opts.loop_flag:
			self.opts.loop_flag = False
		if self.currVidIndx != 0:
			self.backwardsFlag = True
			self.vid.stop()
			self.vid.close()

	def quit_video(self):
		self.vid.stop()
		self.vid.close()
		self.quit()

	def generate_screenshot_name(self):
		timestamp = time.strftime("%m%d%y_%H_%M_%S")  # 24-hour format
		return f"pyVidSShot_{timestamp}.png"

	def check_SSHOT_dir(self):
		if not os.path.isdir(self.SCREEN_SHOT_DIR):
			try:
				os.makedirs(self.SCREEN_SHOT_DIR, exist_ok=True)
				self.save_sshot_error = None
			except PermissionError:
				self.save_sshot_error = f"No permission to create '{self.SCREEN_SHOT_DIR}'"
			except OSError as e:
				self.save_sshot_error =  f"Unexpected OS error: {e}"

	def save_screenshot(self, file):
		pygame.image.save(self.win, file)

	def sshot_splash(self):
		text_color = pygame.color.THECOLORS['white']

		# Define box width
		box_width = 600

		message_lines =["PyVid2 Screenshot:", self.save_sshot_error]

		# Calculate box height dynamically based on number of lines
		font_height = self.font_bold_regular.get_height()
		padding = 20  # Extra space around the text
		box_height = (len(message_lines) * (font_height + 10)) + padding

		# Center box position
		box_x = (self.displayWidth - box_width) // 2
		box_y = (self.displayHeight - box_height) // 2

		# Create a semi-transparent surface for the box
		box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
		box_surface.fill((16, 78, 139, 225))

		# Blit semi-transparent box
		self.win.blit(box_surface, (box_x, box_y))

		# Render and position text inside the box
		for i, line in enumerate(message_lines):
			text_surface = self.font_bold_regular.render(line, True, text_color)
			#text_rect = text_surface.get_rect(
				#center=(box_x + (box_width // 2), box_y + (padding // 2) + (i * (font_height + 10))))
			text_rect = text_surface.get_rect(
				center=(box_x + (box_width // 2), box_y + (padding // 2) + 15 + (i * (font_height + 10))))

			self.win.blit(text_surface, text_rect)

		pygame.display.flip()

	def render_filename_text(self, text, y, font_size=60,outline_style="default"):
		"""Renders OSD text with a bold black outline for better visibility on light backgrounds."""
		# Perfect!
		font = pygame.font.Font(self.FONT_DIR + "luximb.ttf", font_size)

		# Render text with no outline
		text_render = font.render(text, True, pygame.color.THECOLORS['dodgerblue'])
		text_width, text_height = text_render.get_size()

		# Create transparent surface for text
		text_surface = pygame.Surface((text_width + 20, text_height + 30), pygame.SRCALPHA)
		text_surface.fill((0, 0, 0, 0))  # Fully transparent background

		# **Render thicker outline**
		#outline_color = (0, 0, 0)  # Black outline
		#outline_color = (255, 255, 255)
		outline_color = pygame.color.THECOLORS['dodgerblue4']
		#outline_render = font.render(text, True, outline_color)

		if outline_style == "blurred":
			# Simulate a blurred outline using multiple transparent layers
			for alpha, offset in [(100, 5), (80, 3), (60, 1)]:  # Different transparency levels and offsets
				temp_outline = font.render(text, True, outline_color)
				temp_outline.set_alpha(alpha)  # Apply transparency
				for dx, dy in [(-offset, -offset), (offset, -offset), (-offset, offset), (offset, offset)]:
					text_surface.blit(temp_outline, (dx + 10, dy + 10))

		else:
			#outline_render = font.render(text, True, outline_color)
			#for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (-2, 0), (2, 0), (0, -2), (0, 2)]:
			#for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (-1, 0), (1, 0), (0, -1), (0, 1)]:
			for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)]:
			#for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
				outline_render = font.render(text, True, outline_color)
				#outline_render.set_alpha(150)
				text_surface.blit(outline_render, (dx + 10, dy + 10))  # More offsets for thicker outline

		# **Render the actual text in the center**
		text_surface.blit(text_render, (10, 10))

		ts_width, ts_height = text_surface.get_size()
		x_centered = (self.displayWidth - ts_width) // 2
		# **Blit final text surface onto the main window**
		self.win.blit(text_surface, (x_centered, y))

	def draw_filename(self):
		self.render_filename_text(self.vid.name, self.OSD_FILENAME_Y, font_size=28)

	def draw_play_icon(self, x, y):
		"""Draws a play triangle with a bold black outline."""
		#color = (255, 255, 255)  # White play icon
		color = pygame.color.THECOLORS['dodgerblue']
		#outline_color = (0, 0, 0)  # Black outline
		#print(f"{pygame.color.THECOLORS['dodgerblue4']}")
		outline_color = (16, 78, 139)

		# Triangle points
		points = [(x, y), (x + 25, y + 25), (x, y + 50)]

		# **Step 1: Draw Outline First (Offset in Multiple Directions)**
		offsets = [-2, 2]  # Outline thickness
		for dx in offsets:
			for dy in offsets:
				outline_points = [(px + dx, py + dy) for px, py in points]  # Offset triangle points
				pygame.draw.polygon(self.win, outline_color, outline_points)  # Black outline

		# **Step 2: Draw Play Triangle on Top**
		pygame.draw.polygon(self.win, color, points)  # White play icon

	def draw_pause_icon(self, x, y):
		"""Draws two pause bars with a slightly stronger black outline."""
		#color = (255, 255, 255)  # White pause bars
		color = pygame.color.THECOLORS['dodgerblue']
		#outline_color = (30, 30, 30)  # Slightly darker outline
		outline_color = pygame.color.THECOLORS['dodgerblue4']

		# **Step 1: Expand Surface Slightly**
		pause_surface = pygame.Surface((50, 80), pygame.SRCALPHA)
		pause_surface.fill((0, 0, 0, 0))  # Fully transparent

		# **Step 2: Apply a Slightly More Pronounced Outline**
		pygame.draw.rect(pause_surface, outline_color, (4, 4, 14, 72))  # Left bar outline
		pygame.draw.rect(pause_surface, outline_color, (29, 4, 14, 72))  # Right bar outline

		# **Step 3: Draw Pause Bars on Top**
		pygame.draw.rect(pause_surface, color, (6, 6, 10, 68))  # Left bar
		pygame.draw.rect(pause_surface, color, (31, 6, 10, 68))  # Right bar

		# **Step 4: Blit the Pause Icon onto the Main Display**
		self.win.blit(pause_surface, (x, y))

	def play_icon(self, x, y):
		self.win.blit(self.playIcon, (x, y))

	def pause_icon(self, x, y):
		self.win.blit(self.pauseIcon, (x, y))

	def foward_icon(self, x, y):
		self.win.blit(self.forwardIcon, (x, y))

	def rewind_icon(self, x, y):
		self.win.blit(self.rewindIcon, (x, y))

	def get_fade_color(self,time_left, max_fade_time=10):
		"""Interpolates between DodgerBlue and Amber based on remaining time."""
		# Define colors as RGB values
		dodgerblue = pygame.Color('dodgerblue')
		amber = pygame.Color(255, 191, 0)  # Amber RGB value
		blue4 = pygame.Color(0, 0, 139)    # blue4
		cfblue = pygame.Color(100,149, 237)
		yellow = pygame.Color(255, 255, 0)
		lightpink = pygame.Color(255,182, 193)
		hotpink = pygame.Color(255, 105, 180)
		# Calculate fade percentage (0 when > max_fade_time, 1 when time_left = 0)
		fade_ratio = max(0, min(1, (max_fade_time - time_left) / max_fade_time))

		# Interpolate between DodgerBlue and Amber
		faded_color = pygame.Color(
			int(dodgerblue.r + (hotpink.r - dodgerblue.r) * fade_ratio),
			int(dodgerblue.g + (hotpink.g - dodgerblue.g) * fade_ratio),
			int(dodgerblue.b + (hotpink.b - dodgerblue.b) * fade_ratio)
		)

		return faded_color

	def render_osd_text(self, text, x, y, curPos, font_size=50, outline_style="default"):
		"""Renders OSD text with a bold black outline for better visibility on light backgrounds."""
		color = pygame.color.THECOLORS['dodgerblue']  # Default assignment
		# Excellent!
		START_FADE_TIME = 20
		font = pygame.font.Font(self.FONT_DIR + "luximb.ttf", font_size)

		time_delta = round(self.vid.duration, 1) - round(curPos, 1)
		cutoff_time = int(round(START_FADE_TIME * self.vid.speed,1))

		if int(time_delta) <= cutoff_time:
			color = self.get_fade_color(time_delta, cutoff_time) if self.OSD_curPos_flag else pygame.color.THECOLORS['dodgerblue']

		text_render = font.render(text, True, color)
		#text_width, text_height = text_render.get_size()
		self.osd_text_width, self.osd_text_height = text_render.get_size()

		# Create transparent surface for text
		text_surface = pygame.Surface((self.osd_text_width + 20, self.osd_text_height + 30), pygame.SRCALPHA)
		text_surface.fill((0, 0, 0, 0))  # Fully transparent background

		outline_color = (pygame.color.THECOLORS['dodgerblue4'] if int(time_delta)  > cutoff_time else pygame.color.THECOLORS['black'])
		#outline_render = font.render(text, True, outline_color)

		if outline_style == "blurred":
		# Simulate a blurred outline using multiple transparent layers
			for alpha, offset in [(100, 5), (80, 3), (60, 1)]:  # Different transparency levels and offsets
				temp_outline = font.render(text, True, outline_color)
				temp_outline.set_alpha(alpha)  # Apply transparency
				for dx, dy in [(-offset, -offset), (offset, -offset), (-offset, offset), (offset, offset)]:
					text_surface.blit(temp_outline, (dx + 10, dy + 10))

		elif outline_style == "default":
			#outline_render = font.render(text, True, outline_color)
			#for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (-2, 0), (2, 0), (0, -2), (0, 2)]:
			#for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)]:
			for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (-1, 0), (1, 0), (0, -1), (0, 1)]:
				outline_render = font.render(text, True, outline_color)
				text_surface.blit(outline_render, (dx + 15, dy + 15))  # More offsets for thicker outline

		# **Render the actual text in the center**
		text_surface.blit(text_render, (15, 15))
		# **Blit final text surface onto the main window**
		self.win.blit(text_surface, (x, y))

	def draw_osd_background(self, x, y, width, height):
		"""Draws a semi-transparent background behind OSD text."""
		bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)  # Fully transparent layer
		bg_surface.fill((0, 0, 0, 128))  # Semi-transparent black

		# **Blit this background onto the main display**
		self.win.blit(bg_surface, (x, y))

	def OSD_clear(self, x, y):
		# Account for max outline size
		outline_padding = 6  
		clear_x, clear_y = x - outline_padding, y - outline_padding
		clear_width, clear_height = self.osd_text_width + (outline_padding * 2), self.osd_text_height + (outline_padding * 2)

		# Fill expanded area to remove text + outline
		self.win.fill((0, 0, 0), (clear_x, clear_y, clear_width, clear_height))
		#pygame.display.update(clear_x, clear_y, clear_width, clear_height)

	def OSD_icon_clear(self,x, y):
		background = pygame.Surface((48, 48))  # Create a blank surface
		background.fill((0, 0, 0))  # Fill it with the background color
		self.win.blit(background, (x, y))  # Overwrite the icon with the background
		#pygame.display.update(x, y, 48, 48)

	def draw_OSD(self):
		raw_position = self.vid.get_pos()
		corrected_position = round(raw_position / self.vid.speed, 1)

		# Ensure tracking variable exists
		if not hasattr(self, "last_osd_position"):
			self.last_osd_position = corrected_position

		# **Detect Seeking Events (Mouse Wheel or Keyboard Seek)**
		if hasattr(self, "seek_flag") and self.seek_flag:
			#print(f"🔄 Seek action detected! Locking new position at {corrected_position}")
			self.last_osd_position = corrected_position  # Lock new seek position
			self.seek_flag = False  # Reset seek flag

		# **Prevent Position Drops**
		if corrected_position < self.last_osd_position:
			#print(
				#f"⚠️ REJECTING GLITCH: Position tried to drop! Previous: {self.last_osd_position}, New: {corrected_position}")
			corrected_position = self.last_osd_position  # Stick to last valid position

		# Update last known position
		self.last_osd_position = corrected_position

		# **Ensure Pause/Play Icons Are Rendered**
		if not (self.seekFwd_flag or self.seekRewind_flag):
			if self.vid.paused:
				self.pause_icon(self.OSD_ICON_X, self.OSD_ICON_Y)
			else:
				self.play_icon(self.OSD_ICON_X, self.OSD_ICON_Y)

		# **Render the OSD text**S
		total_duration = self.format_seconds(round(self.vid.duration / self.vid.speed, 1))
		if self.OSD_curPos_flag:
			osd_text = f"{self.format_seconds(corrected_position)}"
			#osd_text = f"{self.format_seconds(corrected_position)} / {total_duration}"
		else:
			#osd_text = f"{self.format_seconds(corrected_position)}"
			osd_text = f"{self.format_seconds(corrected_position)} / {total_duration}"

		self.render_osd_text(osd_text, self.OSD_TEXT_X, self.OSD_TEXT_Y, raw_position, font_size=60, outline_style="default")

	def draw_progress_bar(self):
		if self.progress_active:
			progress_width = 400  # Initial width
			progress_height = 30
			DodgerBlue = pygame.color.THECOLORS['dodgerblue']
			progress_alpha = 150  # Transparency level (0-255)
			progress_color = DodgerBlue
			progress_bg = (20, 20, 20, progress_alpha)  # Background with transparency

			#font = pygame.font.SysFont("Arial", 24)  # Choose your preferred font and size
			font = pygame.font.Font(self.FONT_DIR + "LiberationSans-Regular.ttf", 24)
			progress_text = font.render(f"{int(self.progress_percentage)}%", True, (255, 255, 255))  # White text

			# Create transparent surface
			progress_surface = pygame.Surface((progress_width, progress_height), pygame.SRCALPHA)
			progress_surface.fill(progress_bg)  # Semi-transparent background

			progress_bar_rect = progress_surface.get_rect()

			progress_x = progress_bar_rect.x + (progress_width // 2) - (progress_text.get_width() // 2)
			progress_y = progress_bar_rect.y + (progress_height // 2) - (progress_text.get_height() // 2)

			# Fill progress dynamically
			fill_width = int(progress_width * (self.progress_value / 100))  # Scale width based on progress

			pygame.draw.rect(progress_surface, progress_color, (0, 0, fill_width, progress_height))

			progress_surface.blit(progress_text, (progress_x, progress_y))
			# Blit progress bar to screen center
			self.win.blit(progress_surface, ((self.displayWidth - progress_width) // 2, self.displayHeight // 2))

	def create_thumbnail(self, video_path):
		"""Extract thumbnail and store it permanently."""
		#thumbnail_path = os.path.join(self.CACHE_DIR, os.path.basename(video_path) + ".jpg")
		thumbnail_path = os.path.join(self.CACHE_DIR, os.path.splitext(os.path.basename(video_path))[0] + ".jpg")

		# **Check if the file is a GIF**
		if video_path.lower().endswith(".gif"):
			ffmpeg_cmd = [
				"ffmpeg", "-hide_banner", "-loglevel", "error",
				"-i", video_path, "-vf", "scale=256:144",
				"-frames:v", "1", "-update", "1", thumbnail_path
			]
		else:
			# **For stander video files**
			ffmpeg_cmd = [
				"ffmpeg", "-hide_banner", "-loglevel", "error",
				"-i", video_path, "-ss", "00:00:05", "-vframes", "1",
				"-vf", "scale=256:144", "-update", "1", thumbnail_path
			]

		# ** Ensure cache directory exists **
		os.makedirs(self.CACHE_DIR, exist_ok=True)

		# ** Generate thumbnail from video **
		#subprocess.call(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", video_path, "-ss", "00:00:05", "-vframes", "1", "-vf", "scale=256:144", "-update", "1", thumbnail_path])
		subprocess.call(ffmpeg_cmd)

		return thumbnail_path

	def load_thumbnail(self, video_path):
		"""Load from cache or generate if missing."""
		if video_path in self.thumbnail_cache:
			return self.thumbnail_cache[video_path]  # ✅ Return cached thumbnail immediately

		#thumbnail_path = os.path.join(self.CACHE_DIR, os.path.basename(video_path))
		thumbnail_path = os.path.join(self.CACHE_DIR, os.path.splitext(os.path.basename(video_path))[0] + ".jpg")

		# **Generate thumbnail if missing**
		if not os.path.exists(thumbnail_path):
			thumbnail_path = self.create_thumbnail(video_path)

		# **Load the image**
		image_surface = pygame.image.load(thumbnail_path)
		image_surface = pygame.transform.scale(image_surface, (256, 144))

		# **Store in cache for faster access**
		self.thumbnail_cache[video_path] = image_surface

		return image_surface

	def fade_in_out(self, video_info):
		self.vid.stop()
		self.image_surface = self.load_thumbnail(self.videoList[self.currVidIndx])
		self.progress_timeout = 50

		DodgerBlue = pygame.color.THECOLORS['dodgerblue']
		DodgerBlue4 = pygame.color.THECOLORS['dodgerblue4']

		"""Handles fade-in and fade-out animation for splash screen."""
		splash_surface = pygame.Surface((self.Splash_Width, self.Splash_Height))
		splash_surface.fill(DodgerBlue4)
		splash_rect = (0,0, self.Splash_Width, self.Splash_Height)
		pygame.draw.rect(splash_surface, DodgerBlue, splash_rect, 2, 15)

		alpha = 0  # Start fully transparent

		# Fade In
		while alpha < 255:
			alpha += 5  # Increase alpha to fade in
			splash_surface.set_alpha(alpha)
			self.draw_video_splash(splash_surface, video_info)
			pygame.time.delay(30)  # Control speed of fade-in
		# Length of time to hold splash visible
		pygame.time.delay((self.opts.loopDelay * 1000))

		# Fade Out
		while alpha > 100:
			alpha -= 5  # Decrease alpha to fade out
			splash_surface.set_alpha(alpha)
			self.draw_video_splash(splash_surface, video_info)
			pygame.time.delay(30)  # Control speed of fade-out

		self.vid.play()

	def draw_video_splash(self, splash_surface, video_info):

		WHITE = (255, 255, 255)
		BLACK = (0, 0, 0)
		gray = (103,103,103)
		Blue = pygame.color.THECOLORS['darkblue']
		DarkViolet = pygame.color.THECOLORS['darkviolet']
		DarkOrchid = pygame.color.THECOLORS['darkorchid']
		Crimson = pygame.color.THECOLORS['crimson']
		DarkSlateBlue = pygame.color.THECOLORS['darkslateblue']
		Fuchsia = pygame.color.THECOLORS['fuchsia']

		RECT_X = (self.displayWidth - self.Splash_Width) // 2
		RECT_Y = (self.displayHeight - self.Splash_Height) // 2
		self.win.fill(BLACK)

		# Text positions
		text_x =  RECT_X + 50
		text_y = RECT_Y + 0

		self.win.blit(splash_surface, (RECT_X, RECT_Y))

		sp_dur_text = f"{video_info['speed_duration']} @ {self.format_playback_speed(self.vid.speed)}"
		playing_text = self.font_regular_36.render(f"Playing {self.currVidIndx+1} of {len(self.videoList)}", True, WHITE)

		title_text = self.font_regular_28.render(f"{video_info['name']}", True, Fuchsia)
		duration_text = self.font_regular_28.render(f"Duration: {video_info['duration']}", True, WHITE)
		speed_dur_text = self.font_regular_28.render(sp_dur_text, True, pygame.color.THECOLORS['red'])
		size_text = self.font_regular_28.render(f"File Size: {video_info['file_size']}", True, WHITE)
		access_text = self.font_regular_28.render(f"Last Accessed: {video_info['last_accessed']}", True, WHITE)

		# Thumbnail positions
		image_x = RECT_X + 500
		image_y = RECT_Y + 150

		self.win.blit(playing_text, (text_x, text_y + 50))
		self.win.blit(title_text, (text_x, text_y + 100)) 		#50
		self.win.blit(duration_text, (text_x, text_y + 150))	#100

		if round(self.vid.speed) != 1.0:
			self.win.blit(speed_dur_text, (text_x, text_y + 200)) #150
			self.win.blit(size_text, (text_x, text_y + 250))      #200
			self.win.blit(access_text, (text_x, text_y + 300))	  #250
		else:
			self.win.blit(size_text, (text_x, text_y + 200))	  #150
			self.win.blit(access_text, (text_x, text_y + 250))	  #200

		self.win.blit(self.image_surface, (image_x, image_y))
		pygame.display.flip()

	def print_cli_options(self):
		# Print cli options to the console for debug purposes
		print()
		# Required but mutually exclusive options
		Paths = self.opts.Paths
		loadPlayList = self.opts.loadPlayList

		# Video Playback Options
		loop = self.opts.loop
		shuffle = self.opts.shuffle
		disableGIF = self.opts.disableGIF
		#scale  = self.opts.scale
		enableFFprobe = self.opts.enableFFprobe
		enableOSDcurpos = self.opts.enableOSDcurpos
		reader = self.opts.reader
		interp = self.opts.interp
		loopDelay = self.opts.loopDelay
		playSpeed = self.opts.playSpeed

		# Audio Settings
		mute = self.mute_flag
		noAudio = self.opts.noAudio
		usePygameAudio = self.opts.usePygameAudio

		# System Settings
		verbose = self.opts.verbose
		display = self.opts.display
		consoleStatusBar = self.opts.consoleStatusBar

		# File Handling
		noIgnore = self.opts.noIgnore
		noRecurse = self.opts.noRecurse
		printVideoList = self.opts.printVideoList
		printIgnoreList = self.opts.printIgnoreList

		print(f"{self.bcolors.BOLD}{self.bcolors.Blue_f}Mutually Exclusive Items:{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.Paths:{(self.bcolors.Magenta_f if Paths is not None else self.bcolors.Yellow_f)} {Paths}{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.loadPlayList:{(self.bcolors.Magenta if loadPlayList is not None else self.bcolors.Yellow_f)} {loadPlayList}{self.bcolors.RESET}")
		print()
		print(f"{self.bcolors.BOLD}{self.bcolors.Blue_f}Video Playback Options:{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.loop: {(self.bcolors.BOOL_TRUE + 'True' if loop else self.bcolors.BOOL_FALSE + 'False')}{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.shuffle: {(self.bcolors.BOOL_TRUE + 'True' if shuffle else self.bcolors.BOOL_FALSE + 'False')}{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.disableGIF: {(self.bcolors.BOOL_TRUE + 'True' if disableGIF else self.bcolors.BOOL_FALSE + 'False')}{self.bcolors.RESET}")
		#print(f"{self.bcolors.BOLD}opts.scale: {(self.bcolors.BOOL_TRUE + 'True'  if scale else self.bcolors.BOOL_FALSE + 'False' )}{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.enableFFprobe: {(self.bcolors.BOOL_TRUE + 'True' if enableFFprobe else self.bcolors.BOOL_FALSE + 'False')}{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.enableOSDcurpos: {(self.bcolors.BOOL_TRUE + 'True' if self.opts.enableOSDcurpos else self.bcolors.BOOL_FALSE + 'False')}{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}self.OSD_curPos_flag: {(self.bcolors.BOOL_TRUE + 'True' if self.OSD_curPos_flag else self.bcolors.BOOL_FALSE + 'False')}{self.bcolors.RESET}")
		
		print(f"{self.bcolors.BOLD}opts.reader: {self.bcolors.Magenta_f}{reader}{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.interp: {self.bcolors.Magenta_f}{interp}{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.loopDelay: {self.bcolors.Magenta_f}{loopDelay}{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.playSpeed: {self.bcolors.Magenta_f}{playSpeed}{self.bcolors.RESET}")


		print(f"{self.bcolors.BOLD}{self.bcolors.Blue_f}Audio Settings:{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.mute: {(self.bcolors.BOOL_TRUE + 'True' if mute else self.bcolors.Yellow_f + 'False')}{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.noAudio: {(self.bcolors.BOOL_TRUE + 'True' if noAudio else self.bcolors.BOOL_FALSE + 'False')}{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.usePygameAudio: {(self.bcolors.BOOL_TRUE + 'True' if usePygameAudio else self.bcolors.BOOL_FALSE + 'False')}{self.bcolors.RESET}")
		print()
		print(f"{self.bcolors.BOLD}{self.bcolors.Blue_f}System Settings:{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.verbose: {(self.bcolors.BOOL_TRUE + 'True' if verbose else self.bcolors.BOOL_FALSE + 'False')}{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.display: {self.bcolors.Magenta_f}{display}{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.consoleStatusBar: {(self.bcolors.BOOL_TRUE + 'True' if consoleStatusBar else self.bcolors.BOOL_FALSE + 'False')}{self.bcolors.RESET}")
		print()
		print(f"{self.bcolors.BOLD}{self.bcolors.BOLD}{self.bcolors.Blue_f}File Handling:{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.noIgnore: {(self.bcolors.BOOL_TRUE + 'True' if noIgnore else self.bcolors.BOOL_FALSE + 'False')}{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.noRecurse: {(self.bcolors.BOOL_TRUE + 'True' if noRecurse else self.bcolors.BOOL_FALSE + 'False')}{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.printVideoList: {(self.bcolors.BOOL_TRUE + 'True' if printVideoList else self.bcolors.BOOL_FALSE + 'False')}{self.bcolors.RESET}")
		print(f"{self.bcolors.BOLD}opts.printIgnoreList: {(self.bcolors.BOOL_TRUE + 'True' if printIgnoreList else self.bcolors.BOOL_FALSE + 'False')}{self.bcolors.RESET}")
		print()

	def DrawVideoInfoBox(self, FilePath, Filename):
		self.drawVidInfo = DrawVideoInfo(self.win, FilePath, Filename, self.USER_HOME)
		self.drawVidInfo.draw_info_box()
		#pygame.display.flip()

	def playVideo(self, video):
		"""
		Method that creates a VideoPygame object and starts playing it.
		:param video:   Path/Filename of video to play
		:type video: str
		:return: An instance of a  VideoPygame object
		:rtype: VideoPygame
		"""

		self.progress_active = False
		self.progress_value = 0
		self.progress_percentage = 0
		try:
			self.vid: VideoPygame = Video(video,
										  use_pygame_audio=self.opts.usePygameAudio,
										  interp=self.opts.interp,
			                              audio_track=self.opts.aTrack,
										  speed=self.opts.playSpeed,
										  no_audio=self.opts.noAudio,
										  reader=self.opts.reader_val_int
										  )

			'''
			Uses FFprobe to find information about the video.  When using cv2 to read videos,
			information such as frame count or frame rate are read through the file headers,
			which is sometimes incorrect. For more accuracy, call this method to start a probe
			and update the video information.
			'''
			if self.opts.enableFFprobe:
				self.vid.probe()

			self.vid.change_resolution(self.displayHeight)
			# Global variable needed to show the actual duration of the video in seconds.
			self.opts.actualDuration = int(self.vid.duration / self.opts.playSpeed)
		except Exception as e:
			if self.opts.verbose:
				print(f"An Error occurred: {e}")
			return None
		self.vid.set_volume(self.volume)
		return self.vid

	def play(self, eventHandler):
		"""
		Method to play videos that are listed in self.videoList.
		The method will exit once all the videos in self.videoList are played
		unless the commandline argument --loop is given.
		:param eventHandler:
		:type eventHandler:
		:return:
		:rtype:
		"""
		while True:
			self.currVidIndx = -1
			while self.currVidIndx < len(self.videoList) - 1:
				self.forwardsFlag = False
				self.win.fill((0, 0, 0))
				if not self.backwardsFlag:
					if not self.opts.loop_flag:
						self.currVidIndx += 1
				else:
					if self.currVidIndx < 0:
						self.currVidIndx = 0
					self.backwardsFlag = False
					if self.currVidIndx > 0:
						self.currVidIndx -= 1
				if self.currVidIndx == len(self.videoList):
					break

				if self.videoList[self.currVidIndx].lower().endswith(".gif"):
					self.disableSplash = True
				else:
					self.disableSplash = False
				'''Play the video'''
				# **Step 1: Reset tracking when loading a new video**
				self.last_osd_position = 0.0    # Clear previous timestamp tracking
				self.seek_flag = False          # Reset seek behavior
				self.last_vid_info_pos = 0.0
				self.seek_flag2 = False
				#
				# reset the video metadata box  and tooltip if active
				self.video_info_box = False
				self.video_info_box_tooltip = False

				#print(f"📌 New video loaded! Resetting OSD tracking to prevent glitches.")

				self.vid = self.playVideo(self.videoList[self.currVidIndx])
				if self.vid is None:
					continue
				print(f"Playing {self.currVidIndx+1} of {len(self.videoList  )}: {self.vid.name}{self.vid.ext}")
				if not self.disableSplash:
					file_path = self.videoList[self.currVidIndx]
					filename = os.path.basename(file_path)
					last_access_timestamp = os.path.getatime(self.videoList[self.currVidIndx])
					last_access_datetime = datetime.datetime.fromtimestamp(last_access_timestamp).strftime("%m-%d-%Y %H:%M:%S")
					file_size_mb = os.path.getsize(self.videoList[self.currVidIndx]) / (1024 * 1024)
					duration = self.format_duration(self.vid.duration)
					fast_duration = self.format_duration( round( self.vid.duration / self.vid.speed) )

					video_info = {
						"name": f"{filename}",
						"duration": f"{duration}",
						"speed": f"{self.opts.playSpeed}",
						"speed_duration": f"{fast_duration}",
						"file_size": f"{file_size_mb:.2f} MB",
						"last_accessed": f"{last_access_datetime}"
						}

					self.fade_in_out(video_info)

				# The event handler loop
				while self.vid.active:
					eventHandler.handle_events()


					if self.opts.enableOSDcurpos:
						self.opts.enableOSDcurpos = False
						self.OSD_curPos_flag = not self.OSD_curPos_flag
						self.draw_OSD_active = (not self.draw_OSD_active if not self.OSD_curPos_flag else True)


					if self.mute_flag or self.key_mute_flag:
						self.vid.mute()

					'''
					if self.draw_OSD_active and self.vid.paused:
						if not (self.seekFwd_flag or self.seekRewind_flag):
							self.draw_OSD()
							self.draw_filename()
					'''

					pos_w, pos_h = self.getResolutions()
					if self.vid.draw(self.win, (pos_w, pos_h), force_draw=(False if not self.vid.paused else True)) or self.vid.paused:

						if self.draw_OSD_active:
							if not (self.seekFwd_flag or self.seekRewind_flag):
								self.draw_OSD()
								self.draw_filename()

						if self.status_bar_visible:
							self.displayVideoInfo(self.win,
												  self.vid.name,
												  self.format_duration(self.vid.duration),
												  self.format_duration(self.opts.actualDuration),
												  round(self.opts.playSpeed,1),
												  self.vid.get_volume(),
												  self.vid.get_pos()
												  )

						if self.video_info_box:
							self.drawVidInfo.draw_info_box()
							if self.video_info_box_tooltip:
								self.drawVidInfo.draw_tooltip(self.win,
								                              self.vid.name + self.vid.ext,
								                              self.video_info_box_tooltip_mouse_x,
								                              self.video_info_box_tooltip_mouse_y
								                              )

						if self.progress_active:
							if pygame.time.get_ticks() - self.last_update_time > 10:
								self.draw_progress_bar()
								self.progress_timeout -= 1
								if self.progress_timeout <= 0:
									self.progress_active = False
									self.last_update_time = 0
								self.last_update_time = pygame.time.get_ticks()

						if self.savePlayListFlag:
							self.savePlayListFlag = False
							self.vid.pause()
							fileName = 'VideoPlayList-' + str(len(self.videoList)) + '.txt'
							self.saveSplash(self.savePlayListPath, fileName)
							time.sleep(3)
							self.vid.resume()

						if self.shuffleSplashFlag:
							self.shuffleSplashFlag = False
							self.vid.pause()
							self.shuffleSplash()
							time.sleep(3)
							self.vid.resume()

						if self.saveScreenShotFlag:
							self.saveScreenShotFlag = False
							self.sshot_splash()
							#time.sleep(1)
							pygame.time.delay(1000)
							self.vid.resume()

						self.update()
					pygame.time.wait(int(1000 / (self.vid.frame_rate * self.vid.speed)))
				# End of while vid.active
				# Close the object to free up resources.
				self.vid.close()

				if self.forwardsFlag is not True and self.backwardsFlag is not True:
					# The length of time delay between each video
					pass
					#pygame.time.wait((self.opts['vidLoopDelay'] * 1000))
			# End of videoList playback loop
			if not self.opts.loop:
				break
		# End of main loop
		self.quit()
