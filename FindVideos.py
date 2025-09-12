#  FindVideos.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Class to generate the pyVid2 internal master playlist.

import os
import subprocess
from typing import Tuple
import magic

class FindVideos:
    """
    Class that searches for supported video files in user-specified directories or
    within a provided playlist file.

    The FindVideos class offers functionality to search for video files in directories
    or from a playlist file specified by the user. It identifies supported video files,
    ignores unwanted directories as directed, and provides the results in a manageable
    list format. The class is designed to allow recursive search within directories
    and gives the option to disable specific video file formats like GIFs.
    """
    def __init__(self, opts: object) -> None:
        """
        Represents a playlist manager object that handles loading and managing a list
        of videos based on the options provided during initialization.

        Attributes:
            opts (object): Contains configuration options and paths for the playlist.
            playListFile: Specifies the file path of the playlist to be loaded.
            pathList: A list of paths where the videos are located.
            videoList: A list that stores the video information after parsing.
            ignoreList: A list containing videos to be ignored during processing.
            numVideos: Holds the total number of videos loaded into the playlist.

        Methods:
            __init__(opts: object) -> None
            getVideos() -> int
        """
        self.opts = opts
        self.playListFile = opts.loadPlayList
        self.pathList = opts.Paths

        self.videoList  = []
        self.ignoreList = []

        self.numVideos = self.getVideos()

    def getVideos(self):
        """
        Retrieves and processes a list of videos based on current configurations and user options.

        Attributes:
            videoList (list): Stores the list of videos processed.

        Parameters:
            None

        Returns:
            int: The number of videos in the processed video list.
        """
        if self.opts.loadFilesFlag:                    #  The cli argument --Files was used (resulting in self.opts.loadFilesFlag being set to True).
            self.buildPlayList(self.opts.Files)        #  Build a playlist from the list of files provided by the cli argument --Files.
        elif not self.opts.loadPlayListFlag:           #  Otherwise, if we are not loading a playlist,
            for videoDir in self.pathList:             #  then --Paths was specified along with at least one subfolder.
                self.recursive(                        #  Scan all user-supplied subfolders for supported video files.
                                videoDir,                                                   #  Iterate over all subfolders in self.pathList,
                                recurse=False if self.opts.noRecurse is True else True,     #  if recurse into each subfolder unless --noRecurse was specified.
                                ignore=True if self.opts.noIgnore is True else False,       #  Ignore .ignore files if --noIgnore was specified.
                                disableGIF=True if self.opts.disableGIF is True else False  #  Exclude GIF files if --disableGIF was specified.
                              )
        else:
            self.loadPlayList(self.playListFile)      # Otherwise, we are going to load a playlist from a file.
        return len(self.videoList)                    # Always return the number of videos in the playlist.

    def buildPlayList(self, Files):
        """
        Build a playlist from a list of files.

        The method processes a list of file paths, validates their extensions based on
        a predefined list of supported video formats, and adds the valid ones to the
        playlist. If the 'disableGIF' option in the object is set to True, '.gif' files
        are excluded from the supported extensions.  Argparse in cmdLineOpts ensures that
        the files exist.

        Args:
            Files (list[str]): A list of file paths to be processed and added to
            the playlist.

        Returns:
            None
        """
        # Supported extensions.
        ext = ['.vob', '.mp4', '.mkv', '.mov', '.avi', '.flv', '.wmv', '.webm', '.3gp', '.gif']
        # Remove '.gif' from the ext list if the opts['disableGif_flag'] is set
        if self.opts.disableGIF:
            ext = [e for e in ext if e != '.gif']

        # All files were validated by argparse, so no need to validate them again.
        # Instead, make sure their extensions are supported.
        Files.sort()
        for file in Files:
            file_lower = file.lower()
            if file_lower.endswith(tuple(ext)):
                result, result_str = FindVideos.is_video_file(file)
                if result:
                    self.videoList.append(file)

    def loadPlayList(self, playListFile):
        """
        Loads a list of video files from a specified playlist file. The function
        reads each line of the file, strips any leading or trailing whitespace, and
        stores the resulting list of video names in the instance's `videoList`
        attribute.

        Args:
            playListFile: Path to the playlist file to be loaded

        Raises:
            FileNotFoundError: If the specified playlist file does not exist
            IOError: If an error occurs while reading the file
        """
        with open(os.path.expanduser(playListFile) ) as file:
            self.videoList = [line.strip() for line in file]

    def recursive(self, dpath: str, recurse: bool = False, ignore: bool = False, disableGIF: bool = False) -> None:
        """
        This method processes a directory recursively, identifies video files, and '.ignore' files or directories
        as specified. It manages video files with supported extensions and adds their paths to a list. The method
        supports options to toggle recursion, ignore specific files and directories, and exclude GIF files.

        Parameters:
        dpath: str
            The directory path to be processed.
        recurse: bool, optional
            If set to True, enables recursive traversal of subdirectories. Defaults to False.
        ignore: bool, optional
            If set to True, skips processing of directories containing files named ".ignore". Defaults to False.
        disableGIF: bool, optional
            If set to True, excludes GIF files from the supported extensions list. Defaults to False.
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
        """
        Returns the size of the video list.

        This method provides the size of the `videoList` attribute by returning the
        number of elements stored in it. It allows users to determine how many videos
        are contained within the list.

        Returns:
            int: The number of elements in the `videoList`.
        """
        return len(self.videoList)

    def videoList_print(self):
        """
        Prints the contents of the video list along with the total number of entries.

        This method checks if the video list is empty. If it is not, it prints each video
        contained in the list and the total count of the videos.

        Raises:
            None
        """
        if self.videoList_size() == 0:
            return
        print("\nContents of videoList:")
        for video in self.videoList:
            print(video)
        print(f"Total number of entries in the videoList: {len(self.videoList)}\n\n")

    def print_ignores(self):
        """
        Prints the contents of the `ignoreList` attribute if it is not empty.

        This method provides the ability to print all entries currently stored in
        the `ignoreList` attribute. It also displays the total count of entries
        in the list. If `ignoreList` is empty, the method exits without performing
        any actions.

        Raises:
            None
        """
        if len(self.ignoreList) == 0:
            return
        print("\nContents of ignoreList:")
        for entry in self.ignoreList:
            print(entry)
        print(f"Total number of entries in the ignoreList: {len(self.ignoreList)}\n\n")

    @staticmethod
    def is_video_file(file_path: str) -> Tuple[bool, str]:
        """
        Determines if a file is a valid video file using multiple validation methods.

        Args:
            file_path: Path to the file to check

        Returns:
            Tuple[bool, str]: (is_valid, message)
            - is_valid: True if the file is a valid video, False otherwise
            - message: Description of why file is invalid, or mime type if valid
        """

        if not os.access(file_path, os.R_OK):
            return False, f"File is not readable: {file_path}"

        try:
            # Use python-magic to get a MIME type
            mime = magic.Magic(mime=True)
            file_mime = mime.from_file(file_path)

            # Check if the MIME type indicates video
            if not file_mime.startswith('video/'):
                return False, f"Not a video file (MIME type: {file_mime})"

            # Additional validation using FFprobe
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries',
                 'stream=codec_type', '-of', 'default=noprint_wrappers=1:nokey=1',
                 file_path],
                capture_output=True,
                text=True
            )

            # Check if FFprobe found any video streams
            if 'video' not in result.stdout:
                return False, "No video streams found in file"

            return True, file_mime

        except magic.MagicException as e:
            return False, f"Error reading file magic: {str(e)}"
        except subprocess.SubprocessError as e:
            return False, f"Error running FFprobe: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
