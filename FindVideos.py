#  FindVideos.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
import os

class FindVideos:
	def __init__(self, opts: object) -> None:
		"""
		Class with methods that will search for supported videos
		in the user supplied directories given on the command line.
		All found media files are listed in self.videoList
		:param opts: Contains our variable flags base on options given on the command line.
		:type opts:
		"""
		self.opts = opts
		self.playListFile = opts.loadPlayList
		self.pathList = opts.Paths
		self.videoList  = []
		self.ignoreList = []

		self.numVideos = self.getVideos()

	def getVideos(self):
		"""
		Method that either:
		(A) Iterates through a list of user supplied paths looking for supported media to play.
		(B) Iterates through a playListFile that was loaded on the command line.  The playListFile
		already has the path/filenames of the media to play.
		In both cases, the found media, or the loaded playListFile contents are appended to self.videoList.
		This method is called by the class constructor.

		:return: Returns the length of self.videoList
		:rtype: int
		"""
		# --loadPlayList takes priority
		if not self.opts.loadPlayListFlag:
			for videoDir in self.pathList:
				# print(f"videoDirs: {videoDirs}"
				self.recursive(
							    videoDir,
								recurse=False if self.opts.noRecurse is True else True,
				                ignore=True if self.opts.noIgnore is True else False,
								disableGIF=True if self.opts.disableGIF is True else False
				              )
		else:
			self.loadPlayList(self.playListFile)
		return len(self.videoList)

	def loadPlayList(self, playListFile):
		with open(os.path.expanduser(playListFile) ) as file:
			self.videoList = [line.strip() for line in file]

	def recursive(self, dpath: str, recurse: bool = False, ignore: bool = False, disableGIF: bool = False) -> None:
		"""
		A method that recurses into a directory structure looking for media files.
		If a supported media file is found, the path/filename of this file is appended to a
		list called 'self.videoList'. This list contains the master path/filenamess of
		all videos that will be played.

		:param str self, dpath:  Path containing the directory to recurse into.
		:param bool recurse:    Flag to tell the function whether it should recurse into 'dpath' (recurse=True).
		:param bool ignore:     Flag if set to True will ignore all directories containing .ignore files
		:param bool disableGIF: Flag if set to True, disables GIF support.
		:return:                None. However, it will append found and supported media path/filenames to self.videoList
		:rtype: None
		"""
		# Supported extensions.
		ext = ['.vob', '.mp4', '.mkv', '.mov', '.avi', '.flv', '.wmv', '.webm', '.3gp', '.gif']

		# Remove '.gif' from the ext list if the opts['disableGif_flag'] is set
		if disableGIF:
			ext = [e for e in ext if e != '.gif']

		files = os.listdir(dpath)
		files.sort()
		for obj in files:
			if os.path.isfile(os.path.join(dpath, obj)):
				file = os.path.join(dpath, obj)
				file_lower = file.lower()
				# If directory has a file called '.ignore',
				# The contents of this directory are ignored.
				if not ignore:
					if '.ignore' in file_lower:
						if file_lower.endswith('.ignore'):
							self.ignoreList.append(file)
						break
				if file_lower.endswith(tuple(ext)):
					# Append our path/file to videoList
					self.videoList.append(file)
			elif os.path.isdir(os.path.join(dpath, obj)):
				_dr = os.path.join(obj)
				# Ignore hidden directories
				if not _dr.startswith('.'):
					if recurse:
						self.recursive(os.path.join(dpath, obj), recurse, ignore, disableGIF)

	def videoList_size(self):
		return len(self.videoList)

	def videoList_print(self):
		if self.videoList_size() == 0:
			return
		else:
			print("\nContents of videoList:")
			for video in self.videoList:
				print(video)
			print(f"Total number of entries in the videoList: {len(self.videoList)}\n\n")

	def print_ignores(self):
		if len(self.ignoreList) == 0:
			return
		else:
			print("\nContents of ignoreList:")
			for entry in self.ignoreList:
				print(entry)
			print(f"Total number of entries in the ignoreList: {len(self.ignoreList)}\n\n")

