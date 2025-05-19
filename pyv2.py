#!/usr/bin/env python
#   pyv.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
import os
from Bcolors import Bcolors
from cmdLineOpts import cmdLineOptions
from PlayVideo import PlayVideo
from EventHandler import EventHandler
from FindVideos import FindVideos


def main():
	# Create a Bcolors instance to give us colors in the console.
	bcolors = Bcolors()
	#bcolors.clear()
	Version = '0.50'
	program_path = __file__
	program_name = os.path.basename(program_path)
	# Retrieve all command line arguments and default variables, as well as user specified directories
	print(
		f"{bcolors.RESET}\n{bcolors.Green_f}{program_name} "
		f"version {bcolors.Cyan_f}{Version}{bcolors.RESET}"
		f" A video player for Linux written in Python.{bcolors.RESET}")

	#opts, pathList, reader = cliOptions(bcolors)
	opts = cmdLineOptions()
	# Create a FindVideos instance, populate Videos.videoList with the path/filename of all found playable media.
	Videos = FindVideos(opts)

	if opts.printIgnoreList or opts.printVideoList:
		if opts.printIgnoreList:
			Videos.print_ignores()
		if opts.printVideoList:
			Videos.videoList_print()
		exit()

	# Create a PlayVideo instance, pass our cli arguments and variables to it, also pass our videoList created
	# by FindVideos().  Finally, pass a bcolors object to it so we can have some colors in the console.
	playVid = PlayVideo(opts, Videos.videoList, bcolors)
	# Clear the console screen
	#bcolors.clear()
	if opts.shuffle:
		playVid.shuffleVideoList()
	# Create an instance of a pygame EventHandler and run it.
	eventHandler = EventHandler(playVid)
	# Finally, play all the videos that are specified in playVid.videoList
	playVid.play(eventHandler)

if __name__ == "__main__":
	main()

