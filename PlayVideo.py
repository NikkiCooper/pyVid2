#  PlayVideo.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Class that plays the video and updates all information dialog boxes ETC.
#
import os
import json
import datetime
import cachetools
import subprocess
from typing import Optional
import help_text as  _help_
import upScale as up_scale
import warnings

warnings.filterwarnings('ignore', category=UserWarning,
                       message='pkg_resources is deprecated as an API.*')

# This must be called BEFORE importing pygame
# else set it in ~/.bashrc
# Or run it from the command line:
# PYGAME_HIDE_SUPPORT_PROMPT=1 pyvid [options] (more trouble than what its worth)
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import sys
import time
import psutil
import random
import pygame
from pygame.locals import *
from fractions import Fraction
import cv2
import numpy as np
import numpy
from pyvidplayer2.video_pygame import VideoPygame
from pyvidplayer2 import Video, PostProcessing
import pyvidplayer2
from DrawVideoInfo import DrawVideoInfo
from VideoPlayBar import VideoPlayBar
from ControlPanel import ControlPanel
from edgeDetectPanel import edgeDetectPanel
from CUDABilateralFilterPanel import CUDABilateralFilterPanel

# Define colors
WHITE = (255, 255, 255)
HEADING_COLOR = (255, 200, 0)  # Yellow for headings
TEXT_COLOR = WHITE   # White for regular text
BLACK = (0, 0, 0)
DODGERBLUE = (30, 144, 255)
DODGERBLUE4 = (16, 78, 139)

class PlayVideo:
    """
    A class to manage video playback including various controls, settings, and graphical user
    interface operations.

    This class provides functionality for managing video files, configuring application settings,
    and rendering video playback with graphical elements such as on-screen display (OSD) icons,
    text, and status bars. It initializes required resources, manages playback controls like play,
    pause, forward, and rewind, and maintains video settings such as volume, playback speed, and
    video information display. The class also includes functionality for scaling video resolution,
    handling user preferences, and caching thumbnail images.

    Attributes:
        opts (object): An object that contains all command-line argument flags for configuration.
        bcolors (object): An object to enable colored output in the terminal.
        vid (object): A reference to the current video object being played.
        reader (object): A reference to the video reader used for decoding and processing videos.
        videoList (list): A list of file paths or filenames of videos to be played.
        USER_HOME (str): Directory path to the user's home folder for resource and cache management.
        drawVidInfo (object): Stores information related to video rendering.
        video_info_box (bool): Flag to indicate if the video information overlay box is displayed.
        video_info_temp (bool): Temporary toggle flag for video information display.
        video_info_box_tooltip (bool): Flag to determine if the video info overlay tooltip is displayed.
        video_info_box_tooltip_mouse_x (int): Mouse X-coordinate for tooltip positioning.
        video_info_box_tooltip_mouse_y (int): Mouse Y-coordinate for tooltip positioning.
        video_info_box_path_tooltip (bool): Boolean indicating path-tooltip rendering.
        video_info_box_path_tooltip_mouse_x (int): X-coordinate for path-tooltip positional reference.
        video_info_box_path_tooltip_mouse_y (int): Y-coordinate for path-tooltip positional reference.
        currVidIndx (int): Index of the current video being played from the video list.
        backwardsFlag (bool): Flag indicating intention to play a previously played video.
        forwardsFlag (bool): Flag indicating intention to play the next video in the list.
        vol (float): Default playback volume.
        volume (float): Playback volume setting.
        vol_rect (object): Graphical object representing the volume icon or bar.
        play_speed_rect (object): Graphical object representing the playback speed slider.
        fileNum (int): Counter to track the current file being processed.
        pause (bool): State indicator for playback pause functionality.
        muted (bool): Determines if the playback volume is muted.
        key_mute_flag (bool): Command-line derived flag for keyboard mute functionality.
        mute_flag (bool): Command-line derived flag for muting audio output.
        savePlayListFlag (bool): Indicates if the current playlist is being saved.
        savePlayListPath (str): File path for saving the active playlist.
        smoothscaleBackend (str): Pygame backend for smooth scaling of video resolution.
        progress_active (bool): Toggles the progress bar or seek functionality.
        progress_percentage (float): Percentage completion of the current video's playback.
        last_update_time (float): Timestamp marker for the last progress update.
        progress_timeout (int): Timeout threshold for progress-related tasks in seconds.
        progress_value (float): Current progress value or position.
        current_position (float): Current playback elapsed time or position in the video.
        total_duration (float): Total duration of the currently played video.
        status_bar_visible (bool): Flag to toggle the visibility of the playback status bar.
        disableSplash (bool): Disable the initial splash screen or startup message.
        Splash_Width_Base (int): Horizontal width for rendering the splash screen.
        Splash_Height_Base (int): Vertical height for rendering the splash screen.
        image_surface (object): Pygame surface object for rendering images or thumbnails.
        shuffleSplashFlag (bool): Randomizes the splash screen if set to True.
        filePath (str): Path to the current video or media resource being played.
        saveScreenShotFlag (bool): Toggles the screenshot functionality for video playback.
        save_sshot_filename (str): Filename for saving a captured screenshot.
        save_sshot_error (exception): Exception details for screenshot save error, if any.
        SCREEN_SHOT_DIR (str): Directory path for storing video screenshots.
        dFlags (int): Pygame display flags used to set up the video renderer.
        win (object): Pygame display window used for rendering video output.
        clock (object): Pygame clock for managing frame rate and gameplay loops.
        RESOURCES_DIR (str): Directory for storing OSD resources or asset files.
        playIcon (object): Icon for the playback play state.
        pauseIcon (object): Icon for the playback pause state.
        forwardIcon (object): Icon for fast forward functionality.
        rewindIcon (object): Icon for rewind functionality.
        check_icon (object): Checkmark icon for visual confirmations.
        OSD_ICON_X (int): X-coordinate for positioning OSD icons.
        OSD_ICON_Y (int): Y-coordinate for OSD icon positioning.
        OSD_ICON_WIDTH (int): The width of OSD icons.
        OSD_ICON_HEIGHT (int): The height of OSD icons.
        OSD_TEXT_X (int): X-coordinate for on-screen text position.
        OSD_TEXT_Y (int): Top margin or Y-axis reference for OSD text rendering.
        OSD_FILENAME_Y (int): Vertical Y-coordinate for the current filename's OSD text.
        osd_text_width (int): Width of the last rendered OSD text.
        osd_text_height (int): Height of the last rendered OSD text.
        draw_OSD_active (bool): Toggles OSD visibility and rendering state.
        OSD_curPos_flag (bool): Determines the current playback position for OSD updates.
        seek_flag (bool): Toggles status bar seek functionality.
        last_osd_position (float): Playback time or position correlating with the last OSD update.
        seekFwd_flag (bool): Fast-forward operation toggling flag.
        seekRewind_flag (bool): Toggles the rewind operation state.
        FONT_DIR (str): Directory path containing font resources for text rendering.
        font_italic (object): Italic font style.
        font_bold_italic (object): Bold italic font style.
        font_regular (object): Regular font style.
        font_regular_big (object): Large regular font style.
        font_regular_big_bold (object): Large bold font style.
        font_CPOS_bold (object): Large centered-position bold font style.
        font_bold_regular (object): Bold regular font style.
        font_regular_28 (object): Regular font style with size 28.
        font_regular_32 (object): Regular font style with size 32.
        font_regular_36 (object): Regular font style with size 36.
        font_regular_50 (object): Regular font style with size 50.
        font_bold_regular_75 (object): Bold regular font style with size 75.
        font_button (object): Font style for button labels.
        font_help_bold (object): Bold font style for help-related text.
        font_help (object): Font style for help text.
        font (object): A general font object used for shadow effects.
        CACHE_DIR (str): Cache directory path for thumbnail storage.
        thumbnail_cache (object): An LRU cache for storing thumbnail image data.
    """
    def __init__(self, opts: object, videoList: list, bcolors: object) -> None:
        """
        This constructor initializes the video playback application. It sets up the user environment, attributes,
        and configures pygame for interactive video viewing. It also manages essential variables related to playback
        such as options, video list, video settings, UI elements, and playback controls.
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
        self.video_info_temp = False
        # Flag to render the video info box tooltip
        self.video_info_box_tooltip = False
        self.video_info_box_tooltip_mouse_x = 0
        self.video_info_box_tooltip_mouse_y = 0
        # The path tooltip
        self.video_info_box_path_tooltip = False
        self.video_info_box_path_tooltip_mouse_x = 0
        self.video_info_box_path_tooltip_mouse_y = 0

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
        self.Splash_Width_Base   = 800
        self.Splash_Height_Base  = 375
        self.image_surface = None
        self.shuffleSplashFlag = False
        self.filePath = None

        # screenshot splash
        self.saveScreenShotFlag = False
        self.save_sshot_filename = None
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
        self.displayResolution = self.displayWidth, self.displayHeight
        self.displayType = up_scale.get_display_type(self.displayResolution)
        self.width_multiplier, self.height_multiplier = up_scale.scale_resolution(self.displayType) \
                                    if self.displayType in up_scale.resolution_multipliers else (1, 1)

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
        self.check_icon = pygame.image.load(self.RESOURCES_DIR + 'checkmark.png').convert_alpha()
        self.check_icon = pygame.transform.scale(self.check_icon, (32, 32))

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
        self.OSD_FILENAME_Y = self.displayHeight - 125
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
        self.font_regular_big = pygame.font.Font(self.FONT_DIR + 'RobotoCondensed-Regular.ttf', 26)
        self.font_regular_big_bold = pygame.font.Font(self.FONT_DIR + 'Roboto-Bold.ttf', 26)
        self.font_CPOS_bold = pygame.font.Font(self.FONT_DIR + 'Roboto-Bold.ttf', 30)
        self.font_bold_regular = pygame.font.Font( self.FONT_DIR + 'Roboto-Bold.ttf', 18)
        self.font_regular_28 = pygame.font.Font(self.FONT_DIR + 'RobotoCondensed-Regular.ttf', 28)
        self.font_regular_32 = pygame.font.Font( self.FONT_DIR + 'RobotoCondensed-Regular.ttf', 32)
        self.font_regular_36 = pygame.font.Font( self.FONT_DIR + 'RobotoCondensed-Regular.ttf', 36)
        self.font_regular_50 = pygame.font.Font(self.FONT_DIR + 'RobotoCondensed-Regular.ttf',  50)
        self.font_bold_regular_75 = pygame.font.Font(self.FONT_DIR + 'Roboto-Bold.ttf',75)
        self.font_button = pygame.font.Font(self.FONT_DIR + 'Montserrat-Bold.ttf', 24)
        #self.font_help = pygame.font.Font(self.FONT_DIR + 'Montserrat-Regular.ttf', 15)
        #self.font_help = pygame.font.Font(self.FONT_DIR + 'Arial.ttf', 16)
        self.font_help_bold = pygame.font.Font(self.FONT_DIR + 'Arial_Black.ttf', 18)
        self.font_help = pygame.font.Font(self.FONT_DIR + 'Arial_Bold.ttf', 17)

        # Referenced in addShadowEffect()
        self.font = None

        # Location of the thumbnail cache directory
        self.CACHE_DIR = self.USER_HOME + '/.local/share/pyVid/thumbs'
        # Create a thumbnail cache with a maximum of 25 entries that reside in memory.
        self.thumbnail_cache = cachetools.LRUCache(maxsize=25)

        #Initialize the video playback bar
        self.vidPlaybackSpeed = 1.0
        self.videoPlayBar = VideoPlayBar(self.win,
                                         self.USER_HOME,
                                         self.opts.loop_flag,
                                         self.volume,
                                         self.muted,
                                         self.vidPlaybackSpeed,
                                         self.pause,
                                         '00:00:00',
                                         '00:00:00'
                                         )
        self.drawVideoPlayBarFlag = False
        self.drawVideoPlayBarToolTip = False
        self.drawVideoPlayBarToolTipMouse_x = 0
        self.drawVideoPlayBarToolTipMouse_y = 0
        self.VideoPlayBarToolTipMouseLast_x = 0
        self.VideoPlayBarToolTipMouseLast_y = 0

        self.drawVideoPlayBarToolTipText = ""
        self.drawVideoPlayBarToolTipTextLast = ""
        self.drawVideoPlayBarToolTipLastIcon = None

        self.stopButtonClicked = False
        self.playButtonClicked = False

        # Help window
        self.help_visible = False
        self.is_hovered = False
        self.help_button_rect = None

        # saveMode
        self.saveMode = False
        self.saveModeVisible = False
        self.saveCount = 0
        self.message = ""
        self.saveSurfFrame = False

        self.frameSaveDir = None
        self.frameCount = 0
        self.counter  = 0

        # mp4 video title
        self.video_title = ""

        # simple_comic_effect
        self.frame_counter = 0
        self.last_comic_frame = None
        self.comic_effect_enabled = False

        self.opts.adjust_video = True
        self.opts.brightness = 0
        self.opts.contrast =  0
        # adjust brightness and contrast
        self.control_panel = ControlPanel(self.displayWidth, self.displayHeight, self)
        self.edge_panel = edgeDetectPanel(self.displayWidth, self.displayHeight, self)
        self.cb_panel_is_visible = False

        # Frame processing buffers
        self.original_frame_array = None
        self.processed_frame_array = None
        self.processed_frame_surf = None

        # Check CUDA availability on video player startup
        cuda_devices = cv2.cuda.getCudaEnabledDeviceCount()
        print(f"🎬 Video Player: CUDA devices available: {cuda_devices}")
        if cuda_devices > 0:
            print("🚀 CUDA-accelerated bilateral filter ready!")
        else:
            print("⚠️  Using CPU bilateral filter")

        #   CUDA bilateral
        self.bilateral_filter_enabled = False
        # Initialize bilateral filter panel with proper scaling
        scaling_factor = up_scale.get_scaling_factor(self.displayHeight)
        self.bilateral_panel = CUDABilateralFilterPanel(self.displayWidth,self.displayHeight)
        self.bilateral_panel.opts_reference = opts

        self.show_filter_panel = False
        print(f"🖥️  Display: {self.displayType}, Resolution: {self.displayResolution}, Scaling: {scaling_factor:.2f}")

    '''
    Static methods
    '''
    @staticmethod
    def apply_gradient(surface, color_start, color_end, width, height, alpha_start=50, alpha_end=200):
        """
        Apply a vertical gradient to a given surface by interpolating between two colors
        and alpha values from top to bottom.

        Parameters:
            surface: The surface object where the gradient will be applied.
            color_start: Tuple[int, int, int]. The starting color of the gradient in RGB format.
            color_end: Tuple[int, int, int]. The ending color of the gradient in RGB format.
            width: int. The width of the gradient area on the surface.
            height: int. The height of the gradient area on the surface.
            alpha_start: int, optional. The starting alpha transparency value of the gradient.
            Default is 50.
            alpha_end: int, optional. The ending alpha transparency value of the gradient.
            Default is 200.
        """
        for y in range(height):
            ratio = y / height
            new_color = (
                int(color_start[0] * (1 - ratio) + color_end[0] * ratio),  # Red
                int(color_start[1] * (1 - ratio) + color_end[1] * ratio),  # Green
                int(color_start[2] * (1 - ratio) + color_end[2] * ratio),  # Blue
                int(alpha_start * (1 - ratio) + alpha_end * ratio)  # Alpha blending
            )
            pygame.draw.line(surface, new_color, (0, y), (width, y))

    @staticmethod
    def format_playback_speed(playback_speed):
        """
        Formats the playback speed into a string representation for display purposes.

        If the playback speed is a whole number, it is formatted as an integer without
        a decimal point (e.g., "2X"). If it is not a whole number, it is formatted with
        one decimal place (e.g., "2.5X").

        Args:
            playback_speed (float): The playback speed to format.

        Returns:
            str: The formatted playback speed string.
        """
        # If playback_speed is a whole number, display it as an integer (e.g., 2X)
        if playback_speed.is_integer():
            return f"[ {int(playback_speed)}X ]"  # Remove th e decimal part
        # Otherwise, display with one decimal place (e.g., 2.5X)
        return f"[ {playback_speed:.1f}X ]"

    @staticmethod
    def quit():
        """
        Static method to handle safely quitting the Pygame application. Ensures the system's terminal
        echo setting is reset to its default, particularly addressing cases where the terminal might
        not echo input after quitting the application.

        Raises:
            SystemExit: Raised to terminate the application after executing required cleanup actions.
        """
        pygame.quit()
        # The following is needed to fix the terminal not echoing to the terminal when program ends.
        output = os.popen("stty -a").read()
        if "-echo" in output:
            os.system("stty echo")
            time.sleep(0.1)
        exit()

    @staticmethod
    def update():
        """
        Update the display of a Pygame application.

        This static method refreshes or updates the current display surface in a
        Pygame application. The update ensures that any changes made to the
        display are rendered and made visible to the user.

        Returns:
            None
        """
        pygame.display.update()

    @staticmethod
    def float_to_fraction_aspect_ratio(aspect_ratio):
        """
        Converts a floating-point aspect ratio to a string representation in fractional aspect ratio format.

        This method takes a floating-point representation of an aspect ratio and converts
        it to a simplified fractional string format (e.g., "16:9"). It ensures that the
        fraction is presented in its simplest form.

        Args:
            aspect_ratio: A float representing the aspect ratio, e.g., 1.77777777778
                          (which corresponds to "16:9").

        Returns:
            A string representing the aspect ratio in fractional format, with the
            numerator and denominator separated by a colon, e.g., "16:9".
        """
        # Convert the float aspect ratio to a Fraction
        fraction = Fraction(aspect_ratio).limit_denominator()
        return f"{fraction.numerator}:{fraction.denominator}"

    @staticmethod
    def format_seconds(seconds):
        """
        Formats a given number of seconds into a string representing time in the
        format "HH:MM:SS". The string always includes two digits for hours, minutes,
        and seconds, padding with zeros if necessary.

        Args:
            seconds (int): Total time in seconds to be formatted.

        Returns:
            str: A string formatted as "HH:MM:SS" representing the time equivalent
            of the given seconds.

        Raises:
            ValueError: If the input is not of type int or is a negative number.
        """
        hours, remainder = divmod(seconds, 3600)  # Separate hours
        minutes, seconds = divmod(remainder, 60)  # Separate minutes and seconds

        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    @staticmethod
    def format_duration(seconds):
        """
        Formats a duration represented in seconds into a string formatted as 'MM:SS'.

        Converts the given number of seconds into minutes and seconds, then formats the
        result as a string with two digits for minutes and two digits for seconds,
        separated by a colon. For example, a duration of 125 seconds will be formatted
        as "02:05".

        Parameters:
            seconds (int): The total duration in seconds that needs to be formatted.

        Returns:
            str: The formatted duration string in 'MM:SS' format.
        """
        minutes, seconds = divmod(seconds, 60)
        return f"{int(minutes):02}:{int(seconds):02}"

    @staticmethod
    def is_portrait(image_surface, DisplayWidth ):
        """
        Determines whether a given image surface represents a "portrait" orientation by analyzing
        its pixel data. The method inspects specific regions on the left and right edges of the
        image to verify if they contain predominantly black pixels (with a threshold applied for
        RGB channel values). The function relies on efficient pixel access and locks the input
        surface during processing. The portrait detection is based on specified areas and is
        useful for identifying images surrounded by black padding.

        Parameters:
            image_surface (Surface): The input surface to evaluate, typically an image loaded with pygame.
            DisplayWidth (int): The total width of the display where the image resides.

        Returns:
            bool: True if the provided image satisfies the "portrait" criteria, otherwise False.
        """
        width, height = image_surface.get_size()
        total_image_width = DisplayWidth

        black_threshold = 50  # Accept near-black pixels (≤50,50,50)

        # Lock the surface for efficient pixel access
        image_surface.lock()
        px_array = pygame.PixelArray(image_surface)

        # Check all pixels in the left black bar (0 to 1200)
        for x in range(0, 1000):
            pixel_color = image_surface.unmap_rgb(px_array[x, int(height // 1.25)])[:3]
            if any(channel > black_threshold for channel in pixel_color):
                # print(f"Left-side: Non-black pixel at ({x}, {height // 2}): {pixel_color}")
                image_surface.unlock()
                return False  # Not a portrait

        # Check all pixels in the right black bar (total_image_width - 1200 to total_image_width)
        for x in range(total_image_width - 1000, total_image_width):
            pixel_color = image_surface.unmap_rgb(px_array[x, int(height // 1.25)])[:3]
            if any(channel > black_threshold for channel in pixel_color):
                # print(f"Right-side: Non-black pixel at ({x}, {height // 2}): {pixel_color}")
                image_surface.unlock()
                return False  # Not a portrait

        # Unlock surface after processing
        image_surface.unlock()

        return True  # Successfully found only black pixels, marking as portrait

    @staticmethod
    def get_average_processing_time(times_list):
        """
        Calculates the average processing time from a list of time durations.

        This static method is designed to compute the average of provided time durations.
        If the list is empty, it will return 0 instead of performing calculations.

        Parameters:
        times_list: list[float]
            A list of time durations (in any measurement unit) for which the
            average needs to be calculated.

        Returns:
        float
            The average of the times_list. If the input list is empty,
            the return value is 0.
        """
        return sum(times_list) / len(times_list) if times_list else 0

    @staticmethod
    def dynamic_select_interp(avg_time, current_cpu, target_time, benchmark_threshold=12.0):
        """
        Determines the appropriate interpolation method for an image smoothing or processing task
        based on the provided average time, current CPU usage, target processing time, and a
        benchmark threshold.

        Attributes:
            None

        Args:
            avg_time (float): The average processing time of the interpolation task.
            current_cpu (float): The current CPU usage percentage.
            target_time (float): The target processing time for an interpolation task.
            benchmark_threshold (float, optional): A benchmark threshold value to determine
                suitability for specific interpolation methods. Default is 12.0.

        Returns:
            str: The selected interpolation method, which can be "lanczos4", "cubic", or "linear".
        """
        if avg_time < benchmark_threshold and current_cpu < 80:
            return "lanczos4"
        elif avg_time < (target_time * 0.9):
            return "cubic"
        else:
            return "linear"

    '''
    Class methods
    '''
    def addShadowEffect(self, screen, font, video_name, org_dur, cur_dur, play_speed, curPos):
        """
        Renders styled text with a shadow effect on a given screen surface. The function displays
        information about the current video being played, including its name, original and current
        durations, playback speed, and current position. The text is styled with a shadow color and
        main text color and rendered at a specific location on the screen.

        Parameters:
        screen (Surface): The pygame screen surface where the shadowed text should be rendered.
        font: The pygame font object used for rendering the text.
        video_name (str): The name of the video currently playing, displayed in the text.
        org_dur (str): The original duration of the video in string format.
        cur_dur (str): The current duration of the video playback in string format.
        play_speed (float): The current playback speed of the video; displayed by rounding
            it to one decimal place if it's not an integer.
        curPos (str): The current position of the video playback, displayed alongside the
            other video details.
        """
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

    def displayVideoInfo(self, screen, video_name, org_dur, cur_dur, play_speed, vol,  curPos):

        """
        Displays video playback information such as status, file details, video name, playback speed, volume level,
        current position, and original duration on the screen.

        This function handles rendering and displaying relevant information about the current video playback in a
        custom status bar. It uses different font styles, colors, and formatting depending on the playback state,
        volume level, and playback speed. The status bar adapts dynamically to reflect changes in these parameters.

        Attributes
        ----------
        FONT_DIR : str
            The directory containing font files to be used for rendering text.
        displayWidth : int
            The width of the video display.
        displayHeight : int
            The height of the video display.
        height_multiplier : float
            A scaling factor for heights based on screen resolution.
        width_multiplier : float
            A scaling factor for widths based on screen resolution.
        last_vid_info_pos : float
            Tracks the last displayed position for the video to handle cases where playback position jumps.
        seek_flag2 : bool
            A flag used to handle manual seeking of the video.
        vid : object
            An object representing video playback details, including paused/muted state.
        opts : object
            Contains configuration options, including loop settings.
        currVidIndx : int
            Index of the current video being played in the video playlist.
        videoList : list
            A list of videos available for playback.
        play_speed_rect : pygame.Rect
            Defines the screen rectangle for displaying playback speed text.
        vol_rect : pygame.Rect
            Defines the screen rectangle for displaying volume text.

        Parameters
        ----------
        screen : pygame.Surface
            The surface where the status bar is drawn (usually the main video display screen).
        video_name : str
            The name of the video file currently being played.
        org_dur : str
            The original duration of the video in "MM:SS" format (e.g., 10:00).
        cur_dur : str
            The current duration of the video adjusted for playback speed in "MM:SS" format.
        play_speed : float
            The playback speed of the video (1.0 for normal speed, 2.0 for twice speed, etc.).
        vol : float
            The current volume level of the playback (between 0.0 to 1.0).
        curPos : float
            The current playback position as a float value rounded to the nearest second.

        Raises
        ------
        None

        Returns
        -------
        None
        """
        pct = str(int(round(100 * vol)))
        arrow_surface   =   None
        arrow_rect      =   None
        cur_dur_surface =   None
        cur_dur_rect    =   None
        position = (self.displayWidth //2 - (325 * self.width_multiplier), self.displayHeight - (45 * self.height_multiplier))

        # Define the colors for each text segment
        play_status_color   =   (pygame.color.THECOLORS['white']
                                    if self.vid.paused is False else pygame.color.THECOLORS['yellow'])
        video_name_color    =   (pygame.color.THECOLORS['aqua']
                                    if self.opts.loop_flag is True else (255, 170, 0))
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
        curPos_text         =   f"   {self.format_seconds(corrected_position)}"
        org_dur_text        =   f"   {org_dur}"
        vol_text            =   f"   [ {pct}% ]   " if self.vid.muted is False else f"   [ Muted ]   "

        font_regular_big_upscaled = up_scale.scale_font(26,self.displayHeight)
        font_regular_big_bold_upscaled = up_scale.scale_font(26, self.displayHeight)
        font_CPOS_bold_upscaled = up_scale.scale_font(30, self.displayHeight)

        font_regular_big = pygame.font.Font(self.FONT_DIR + 'RobotoCondensed-Regular.ttf', font_regular_big_upscaled)
        font_regular_big_bold = pygame.font.Font(self.FONT_DIR + 'Roboto-Bold.ttf', font_regular_big_bold_upscaled)
        font_CPOS_bold = pygame.font.Font(self.FONT_DIR + 'Roboto-Bold.ttf', font_CPOS_bold_upscaled)

        # Render each part separately with its color
        play_status_surface =   font_regular_big.render(play_status_text, True, play_status_color)
        file_number_surface =   font_regular_big.render(file_number_text, True, file_number_color)

        video_name_surface  =   (font_regular_big_bold.render(video_name_text, True, video_name_color)
                                 if self.opts.loop_flag is True else font_regular_big.render(video_name_text, True, video_name_color))
        org_dur_surface     =   font_regular_big.render(org_dur_text, True, org_dur_color)
        play_speed_surface  =   font_regular_big.render(play_speed_text, True, play_speed_color)
        vol_surface         =   font_regular_big.render(vol_text, True, vol_color)
        curPos_surface      =   font_CPOS_bold.render(curPos_text, True, curPos_color)

        base_x, base_y      =   position
        play_status_rect    =   play_status_surface.get_rect(topleft=(base_x, base_y))
        file_number_rect    =   file_number_surface.get_rect(topleft=(play_status_rect.right + 8*self.width_multiplier, base_y))
        video_name_rect     =   video_name_surface.get_rect(topleft=(file_number_rect.right + 12*self.width_multiplier, base_y))
        org_dur_rect        =   org_dur_surface.get_rect(topleft=(video_name_rect.right + 5*self.width_multiplier, base_y))
        '''
        do the following block of code
        if play_speed is not equal to 1
        '''
        if play_speed != 1.0:
            arrow = '-->'
            arrow_text      =   f"{arrow}"
            arrow_surface   =   font_regular_big.render(arrow_text, True, arrow_color)
            arrow_rect      =   arrow_surface.get_rect(topleft=(org_dur_rect.right + 3, base_y))
            cur_dur_text    =   f"{cur_dur}"
            cur_dur_surface =   font_regular_big.render(cur_dur_text, True, cur_dur_color)
            cur_dur_rect    =   cur_dur_surface.get_rect(topleft=(arrow_rect.right + 5, base_y))
            self.play_speed_rect =   play_speed_surface.get_rect(topleft=(cur_dur_rect.right + 6, base_y))
        else:
            self.play_speed_rect =   play_speed_surface.get_rect(topleft=(org_dur_rect.right + 6, base_y))

        self.vol_rect        =   vol_surface.get_rect(topleft=(self.play_speed_rect.right + 20*self.width_multiplier, base_y ))
        curPos_rect          =   curPos_surface.get_rect(topleft=(self.vol_rect.right + 6*self.width_multiplier, base_y))

        # Calculate a background rectangle large enough for all text
        background_rect = pygame.Rect(
            play_status_rect.left - 10*self.width_multiplier,                         # Add padding to the left
            play_status_rect.top - 5*self.height_multiplier,                           # Add padding to the top
            curPos_rect.right - play_status_rect.left + 20*self.width_multiplier,     # Width spans all text
            play_status_rect.height + 10*self.height_multiplier                        # Add padding to the height
        )

        # Draw the semi-transparent background
        background_surface = pygame.Surface((background_rect.width, background_rect.height), pygame.SRCALPHA)
        background_surface.fill((0, 0, 0, 0))                 # Black with 150 alpha (semi-transparent)
        background_surface.set_colorkey((0, 255, 0))
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

        screen.blit(play_speed_surface, self.play_speed_rect)   # Show "play_Speed" in brackets: I.E.  [2X]
        screen.blit(vol_surface, self.vol_rect)                 # Next show the volume indicator:  I.E.  [100%] or [ 50% ] or [ Muted ] even.
        screen.blit(curPos_surface, curPos_rect)                # Last, show the current play position in MM:SS. This is on the far extreme Right of the bar.

    def __environmentSetup(self):
        """
        Sets up the environment variables and directories required for the application.

        This method determines the user's home directory, sets fixed or default values
        for specific environmental variables, and handles directories for saving
        playlists and screenshots. It ensures relevant backend configurations for
        smooth scaling, display settings, and other necessary environment-related
        aspects are appropriately accommodated.

        Attributes:
            USER_HOME (str): The user's home directory path.
            smoothscaleBackend (str): The backend type for smooth scaling, defaulting
                to 'SSE' if unspecified or invalid.
            savePlayListPath (str): Path where playlists are saved. Defaults to the home
                directory if no valid environment variable is found.
            SCREEN_SHOT_DIR (str): Directory for saving screenshots. Defaults to
                'pyVidSShots' in the user's home directory if no valid environment
                variable is specified.

        Parameters:
            None

        Raises:
            SystemExit: Exits the script with status code 99 if the user's home
                directory cannot be determined.
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

        if self.opts.display is not None:
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
            self.SCREEN_SHOT_DIR = self.USER_HOME + '/pyVidSShots'

    def shuffleVideoList(self):
        """
        Shuffles the video list twice to randomize its order more effectively.

        This method ensures that the provided video list is randomized
        by shuffling it twice consecutively. It mutates the internal
        state of the 'videoList' attribute. The purpose is to achieve a
        more thorough reordering of the list entries.

        Raises:
            None
        """
        random.shuffle(self.videoList)
        random.shuffle(self.videoList)

    def savePlayList(self, filename):
        """
        Saves the current playlist to a specified file.

        Writes each video from the current video list into a specified file
        within the save playlist directory. Each video entry is written in
        a new line.

        Parameters:
        filename (str): The name of the file where the playlist will be stored.
        """
        _File = self.savePlayListPath + '/' + filename
        with open(_File, "w") as file:
            for line in self.videoList:
                file.write(str(line) + "\n")

    def getResolutions(self):
        """
        Calculates and returns the resolution offsets required to center the video
        on the display based on the current video size and display dimensions.

        Returns
        -------
        tuple[int, int]
            A tuple containing the horizontal and vertical offsets needed to
            center the video on the display.
        """
        vid_width = self.vid.current_size[0]
        vid_height = self.vid.current_size[1]
        return (self.displayWidth - vid_width) // 2, (self.displayHeight - vid_height) // 2

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

    def format_output(self, vid_paused, index, num_vids, video_name, volume: float, muted: bool, vid_aspect_ratio,
                      resolution, new_resolution, org_duration, current_duration, playback_speed, curPos):
        """
        Formats and displays a detailed status line for video playback including various attributes such as
        playback state, video name, volume, resolution, aspect ratio, and more.

        Parameters:
        vid_paused (bool): Indicates if the video is paused.
        index (int): Current video index in the playlist.
        num_vids (int): Total number of videos in the playlist.
        video_name (str): The name of the video being played.
        volume (float): The current volume level.
        muted (bool): Indicates if the video is muted.
        vid_aspect_ratio: Aspect ratio of the video being played.
        resolution: Tuple representing the original resolution of the video (width, height).
        new_resolution: Tuple representing the new resolution if the video is resized (width, height).
        org_duration: String displaying the original duration of the video at normal speed.
        current_duration: String showing the adjusted duration based on playback speed.
        playback_speed: Current playback speed of the video.
        curPos: Current frame or timestamp position in the video playback.
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
        """
        Advances the video to the next one in the playlist, ensuring the current video's looping
        option is disabled before proceeding.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Function to advance video
        self.forwardsFlag = True
        # Disable video loop for current video before advancing to the next one.
        if self.opts.loop_flag:
            self.opts.loop_flag = False
        self.vid.stop()
        self.vid.close()

    def previous_video(self):
        """
        Disables looping for the current video and navigates to the previous video if possible.

        The function first disables the video looping flag for the current video and checks if
        there is a previous video in the playlist. If so, it sets the backward navigation flag,
        stops the current video playback, and prepares it for closure.

        Raises:
            None
        """
        # Fucntion to go back
        # Disable video loop for the current video before going back to the previous one.
        if self.opts.loop_flag:
            self.opts.loop_flag = False
        if self.currVidIndx != 0:
            self.backwardsFlag = True
            self.vid.stop()
            self.vid.close()

    def quit_video(self):
        """
        Stops and closes the video playback and exits the application.

        This method ensures that the video is stopped and its resources are properly
        released before the application is terminated.

        """
        self.vid.stop()
        self.vid.close()
        self.quit()

    def scale_simple_box(self, box_width, original_font_size, box_height=0):
        """
        Scales the dimensions of a simple box and font size based on display type and resolution
        multipliers. This function adjusts the width and height of a box, as well as the font size,
        to suit the display settings and resolution scaling factors.

        Parameters:
            box_width (int): The width of the box to be scaled.
            original_font_size (int): The original font size to be scaled.
            box_height (int, optional): The height of the box to be scaled. Defaults to 0.

        Returns:
            tuple: A tuple containing the scaled box width (int), scaled box height (int),
            and scaled font size (int).
        """
        width_multiplier, height_multiplier = up_scale.scale_resolution(self.displayType) \
                if self.displayType in up_scale.resolution_multipliers else (1, 1)
        scaled_font_size = up_scale.scale_font(original_font_size, self.displayHeight)
        boxWidth = int(box_width * width_multiplier)
        boxHeight = int(box_height * height_multiplier)
        return boxWidth, boxHeight, scaled_font_size

    def generate_screenshot_name(self,save_dir):
        """
        Generates a screenshot file name with a timestamp based on the provided
        directory and video name.

        Args:
            save_dir (str): The directory where the screenshot will be saved.

        Returns:
            str: The complete file name including the save directory, video name,
            and timestamp.
        """
        timestamp = time.strftime("%m%d%y_%H_%M_%S")  # 24-hour format
        return f"{save_dir}/{self.vid.name}_{timestamp}.png"

    def check_SSHOT_dir(self, noImgType=False):
        """
        Determines the appropriate directory for saving screenshots based on the type of image
        (Portrait or Landscape) detected from the video and ensures the directory exists or is
        created. In case of errors during directory creation, handles exceptions and provides
        error feedback to the user.

        Returns the path to the screenshot directory if successful, and None in case of errors
        with appropriate error management.

        Returns:
            str or None: The directory path where screenshots will be saved if successful,
            otherwise None in case of error.

        Raises:
            PermissionError: If the program does not have permissions to create the directory.
            OSError: For unexpected operating-system-related errors that occur while creating
            the directory.
        """
        if not noImgType:
            imageType = "Portrait" if PlayVideo.is_portrait(self.vid.frame_surf, self.displayWidth) else "Landscape"
        '''
        if imageType == "Portrait":
            print("Detected image type is portrait")
        else:
            print("Detected image type is landscape")
        '''
        # saveDir is the base directory + the video name + the imageType
        saveDir = (f"{self.SCREEN_SHOT_DIR}/{self.vid.name}/{imageType}" if noImgType is False else f"/home/nikki/FrameData/{self.vid.name}")
        if not os.path.isdir(saveDir):
            try:
                os.makedirs(saveDir, exist_ok=True)
                self.save_sshot_error = None
                return saveDir
            except PermissionError:
                self.save_sshot_error = f"No permission to create '{saveDir}'"
                self.vid.pause()
                self.saveModeDialogBox(self.save_sshot_error, True)
                self.vid.resume()
                return None
            except OSError as e:
                self.save_sshot_error =  f"Unexpected OS error: {e}"
                self.vid.pause()
                self.saveModeDialogBox(self.save_sshot_error, True)
                self.vid.resume()
                return None
        else:
            self.save_sshot_error = None
            return saveDir

    def debug_saveModeDialogBox(self, file, error):
        """
        Handles the debugging of save mode dialog box errors by mapping error codes to specific error messages.

        This function categorizes and assigns error messages based on the given error code, distinguishing between
        pygame-specific errors and operating-system-related errors. It determines the appropriate error message for
        a given error code associated with saving operations, utilizing predefined lists of messages.

        Attributes
        ----------
        save_sshot_error: str
            The string representing the specific error message assigned when an error occurs during the save operation.

        Parameters
        ----------
        file: str
            The file path attempted during the save operation.
        error: int
            An integer code representing the type of error encountered.

        Returns
        -------
        bool
            Always returns False after assigning the corresponding error message for a failure scenario.
        """
        pygame_errors = [
            f"Cannot save null surface to {file}",                     # error = 1
            f"Invalid surface argument for {file}",                    # error = 2
            f"Couldn't save image to {file}",                          # error = 3
            f"Error:  frame_surf is None, cannot save to {file}."      # error = 4
        ]

        OSErrors = [
            f"[Errno 13] Permission denied: '{file}'",      # error = 5
            f"[Errno 2] No such file or directory: {file}", # error = 6
            f"[Errno 28] No space left on device: {file}"   # error = 7
        ]

        match error:
            case 1:
                self.save_sshot_error = pygame_errors[0]
            case 2:
                self.save_sshot_error = pygame_errors[1]
            case 3:
                self.save_sshot_error = pygame_errors[2]
            case 4:
                self.save_sshot_error = pygame_errors[3]
            case 5:
                self.save_sshot_error = OSErrors[0]
            case 6:
                self.save_sshot_error = OSErrors[1]
            case 7:
                self.save_sshot_error = OSErrors[2]

        return False

    def save_frame_surf(self, file):
        """
        Saves the current frame surface to a file. The method attempts to save a copy of the
        current `frame_surf` attribute as an image file. The method handles various exceptions,
        including `pygame.error`, file permission issues, disk space issues, or other unforeseen
        exceptions during the saving process.

        Parameters
        ----------
        file : str
            The path to the file where the surface image will be saved.

        Returns
        -------
        bool
            Returns `True` if the frame surface is successfully saved to the specified file.
            Returns `False` otherwise.

        Raises
        ------
        pygame.error
            Raised when the Pygame library encounters an issue while copying or saving
            the surface image.
        OSError
            Raised in case of file system-related errors, such as insufficient permissions
            or lack of available disk space.
        Exception
            Raised for any unexpected errors that occur during the saving process.
        """
        if self.vid.frame_surf is not None:
            try:
                # Lock the surface
                self.vid.frame_surf.lock()
                try:
                    # Create a copy of the surface while locked
                    surface_copy = self.vid.frame_surf.copy()
                finally:
                    # Make sure we always unlock, even if copy fails
                    self.vid.frame_surf.unlock()

                # Save the copy (after unlocking the original)
                pygame.image.save(surface_copy, file, self.smoothscaleBackend)
                return True
            except pygame.error as e:
                self.save_sshot_error = f"Pygame error: {e}, cannot save image: {file}"
                print(self.save_sshot_error)
                return False
            except OSError as e:
                if e.errno == 13:  # Permission denied
                    self.save_sshot_error = f"Permission denied saving to {file}"
                    print(self.save_sshot_error)
                elif e.errno == 28:  # No space left on device
                    self.save_sshot_error = f"Disk full - cannot save image to {file}"
                    print(self.save_sshot_error)
                else:
                    self.save_sshot_error = f"File system error saving image: {e}"
                    print(self.save_sshot_error)
                return False
            except Exception as e:
                self.save_sshot_error = f"Unexpected error while saving frame to: {e}"
                print(self.save_sshot_error)
                return False
        else:
            self.save_sshot_error = f"Error: frame_surf is None, cannot save {file}"
            print(self.save_sshot_error)
            return False

    def handle_queued_screenshot(self):
        """
        Handles queued screenshot operations during the render loop.
        """
        if not self.saveScreenShotFlag:
            return

        try:
            # Temporarily pause without blocking
            was_playing = not self.vid.paused
            self.vid.paused = True

            # Show splash first
            self.sshot_splash()

            # Do the save operation
            if self.save_frame_surf(self.save_sshot_filename):
                # Add delay AFTER saving is complete to ensure splash remains visible
                pygame.time.wait(500)
            else:
                self.message = self.save_sshot_error
                self.saveModeDialogBox(self.message, sleep=True)

        finally:
            # Restore previous playing state
            if was_playing:
                self.vid.paused = False
            self.saveScreenShotFlag = False
            self.save_sshot_filename = None
            #print("self.vid.resume()")
            #self.vid.resume()

    def saveModeDialogBox(self,Message, sleep=False):
        """
        Displays a dialog box with a specified message in the save mode
        and optionally executes a sleep timer.

        This method renders a semi-transparent dialog box at the
        center of the display with a given message. It optionally
        pauses the execution for a specified period to display the
        message visibly.

        Parameters:
            Message (str): The message text to be displayed within the dialog box.
            sleep (bool, optional): Determines whether the function should
                pause longer for visibility (default is False).

        Raises:
            None

        Returns:
            None
        """
        text_color = pygame.color.THECOLORS['white']
        # Define box dimensions
        box_width = int(300 * self.width_multiplier)
        box_height = int(100 * self.height_multiplier)
        baseFontSize = 22
        scaled_font_size = up_scale.scale_font(baseFontSize, self.displayHeight)
        font_bold_regular = pygame.font.Font(self.FONT_DIR + 'Roboto-Bold.ttf', scaled_font_size)  # 22
        box_width, font_height = font_bold_regular.size(Message)
        padding = int(25 * self.width_multiplier)  # Extra space around the text
        box_width += padding
        #font_height = font_bold_regular.get_height()
        #padding = 50  # Extra space around the text
        box_x = (self.displayWidth - box_width) // 2
        box_y = (self.displayHeight - box_height) // 2
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        box_surface_rect = box_surface.get_rect()
        # box_surface.set_alpha(190)
        box_surface.set_colorkey((0, 255, 0))
        PlayVideo.apply_gradient(
            box_surface, (0, 0, 200), (0, 0, 100),
            box_width, box_height,
            alpha_start=225, alpha_end=225
        )
        pygame.draw.rect(
            box_surface,
            WHITE,
            (0, 0, box_width, box_height),
            2, border_radius=10
        )
        # Blit semi-transparent box
        self.win.blit(box_surface, (box_x, box_y))
        text_surface = font_bold_regular.render(Message, True, text_color)
        text_rect = text_surface.get_rect(center=(self.displayWidth // 2, box_y + font_height + 40))
        self.win.blit(text_surface, text_rect)
        pygame.display.flip()
        if sleep:
            time.sleep(10)
        else:
            time.sleep(1)
        self.saveModeVisible = False

    def sshot_splash(self):
        """
        Render a screenshot splash notification on the screen.

        This method creates a semi-transparent notification box and populates it
        with a message indicating the screenshot filename and a screenshot count.
        The notification is centered on the display screen and includes dynamic
        text and box rendering based on the provided parameters, font size,
        and display dimensions.

        Attributes
        ----------
        save_sshot_filename : str | bytes
            The filename of the screenshot. Internally converted to string if not
            already one.
        saveCount : int
            The count of saved screenshots, included in the notification message.
        FONT_DIR : str
            Directory containing the required font files.
        displayType : Any
            The type of display for scaling resolution purposes.
        displayHeight : int
            The height of the display, used to scale font size dynamically.
        displayWidth : int
            The width of the display, used to center the notification box.
        height_multiplier : float
            Factor used to scale dimensions based on the display height.
        width_multiplier : float
            Factor used to scale dimensions based on the display width.
        win : pygame.Surface
            The main window surface where the notification is rendered.

        Raises
        ------
        TypeError
            If `save_sshot_filename` is not able to generate a valid screenshot
            name during execution.
        """
        if not isinstance(self.save_sshot_filename, (str, bytes)):
            self.save_sshot_filename = str(self.save_sshot_filename)

        #text_color = WHITE
        #base_box_width = 600 * self.width_multiplier
        #base_box_height = 200 * self.height_multiplier
        base_font_size = 18
        up_scale.scale_resolution(self.displayType)
        scaled_up_font_size = up_scale.scale_font(base_font_size,self.displayHeight)
        font_bold_regular = pygame.font.Font(self.FONT_DIR + 'Roboto-Bold.ttf', scaled_up_font_size)

        message_lines =[f"PyVid2 Screenshot: #{self.saveCount}", self.save_sshot_filename]
        # Calculate box height dynamically based on the number of lines
        try:
            box_width, font_height = font_bold_regular.size(self.save_sshot_filename)
        except typeError:
            self.save_sshot_filename = self.generate_screenshot_name()
            box_width, font_height = font_bold_regular.size(self.save_sshot_filename)

        padding = int(25 * self.width_multiplier)  # Extra space around the text
        box_width += padding
        box_height = (len(message_lines) * int(font_height + 10 * self.height_multiplier)) + int(1 * padding)
        # Center box position
        box_x = (self.displayWidth - box_width) // 2
        box_y = (self.displayHeight - box_height) // 2
        # Create a semi-transparent surface for the box
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        box_surface.set_colorkey((0, 255, 0))
        pygame.draw.rect(
                box_surface,
                WHITE,
                (0, 0, box_width, box_height),
                1,
                border_radius=10
        )
        box_surface.set_colorkey((0, 255, 0))
        PlayVideo.apply_gradient(box_surface, (0, 0, 200), (0, 0, 100), box_width, box_height)
        pygame.draw.rect(
                box_surface,
                WHITE,
                (0, 0, box_width, box_height),
                1,
                border_radius=10
        )
        # Blit semi-transparent box
        self.win.blit(box_surface, (box_x, box_y))
        # Render and position text inside the box
        for i, line in enumerate(message_lines):
            #print(i, line)
            text_surface = font_bold_regular.render(line, True, (pygame.color.THECOLORS['yellow']  if i == 1 else WHITE))
            text_rect = text_surface.get_rect(
                                            center = (box_x + (box_width // 2),
                                                      box_y + (padding // 2)  + int(15 * self.height_multiplier) \
                                                      + (i * int((font_height + 10 * self.height_multiplier))))
            )
            self.win.blit(text_surface, text_rect)
        pygame.display.flip()

    def saveSplash(self, path, filename):
        """
        Displays a save splash screen with a semi-transparent box and custom text
        to indicate that a file is being saved.

        Parameters:
            path (str): The path to which the file is being saved.
            filename (str): The name of the file being saved.

        Raises:
            FileNotFoundError: If the font file is not located in the specified FONT_DIR.
            pygame.error: If there is an issue with rendering fonts or display surfaces.
        """
        text_color = pygame.color.THECOLORS['white']
        # Define box dimensions

        box_width = int(250*self.width_multiplier)
        box_height = int(100*self.height_multiplier)
        baseFontSize = 18
        scaled_font_size = up_scale.scale_font(baseFontSize, self.displayHeight)
        font_bold_regular = pygame.font.Font(self.FONT_DIR + 'Roboto-Bold.ttf', scaled_font_size) # 18
        font_height = font_bold_regular.get_height()
        padding = 20  # Extra space around the text
        message_lines = [f"Saving {filename} to: ", os.path.expanduser(path)]
        box_height = (len(message_lines) * int((font_height + 10*self.height_multiplier)) + padding*self.height_multiplier)
        box_x = (self.displayWidth - box_width) // 2
        box_y = (self.displayHeight - box_height) // 2

        # Create a semi-transparent surface for the box
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)  # Allows transparency
        box_surface_rect = box_surface.get_rect()
        #box_surface.set_alpha(165)

        box_surface.set_colorkey((0, 255, 0))
        PlayVideo.apply_gradient(box_surface,

                                     (0, 0, 200),
                                     (0, 0, 100),
                                     box_width,
                                     box_height,
                                     alpha_start=100,
                                     alpha_end=200
        )
        pygame.draw.rect(
                             box_surface,
                             WHITE,
                             (0, 0, box_width, box_height),
                             1,
                             border_radius=10
        )

        # Blit semi-transparent box
        self.win.blit(box_surface, (box_x, box_y))
        # Render and position text
        line_spacing = 25

        for i, line in enumerate(message_lines):
            text_surface = font_bold_regular.render(line, True, text_color)
            text_rect = text_surface.get_rect(
                                                center=(box_x + (box_width // 2),
                                                box_y + (padding // 2) + 15 + (i * (font_height + 10)))
            )
            text_rect = text_surface.get_rect(center=(self.displayWidth // 2, box_y + padding +20 + (i * font_height + 10)))
            self.win.blit(text_surface, text_rect)
        pygame.display.flip()

    def shuffleSplash(self):
        """
        Displays a splash screen indicating that the master playlist is being randomized. This function creates
        a styled, semi-transparent box with a gradient background in the center of the screen, along with a
        message displayed inside it. It adapts the box and font size to the display dimensions and applies
        appropriate styling including borders and text alignment.

        Parameters
        ----------
        self : object
            The instance of the class that contains the display settings `displayWidth` and `displayHeight`,
            window surface `win`, and `FONT_DIR` for locating fonts.

        Raises
        ------
        pygame.error
            If the specified font file cannot be loaded or if any Pygame graphic operation fails.
        """
        text_color = pygame.color.THECOLORS['white']
        # Define box dimensions
        base_box_width, base_box_height = 300, 100
        base_font_size = 18
        (box_width,box_height,scaled_font_size) =(
            self.scale_simple_box(
            base_box_width,
            base_font_size,
            base_box_height
        ))

        font_bold_regular = pygame.font.Font(self.FONT_DIR + 'Roboto-Bold.ttf', scaled_font_size) #18
        box_x = (self.displayWidth - box_width) // 2
        box_y = (self.displayHeight - box_height) // 2

        # Create a semi-transparent surface for the box
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)  # Allows transparency
        box_surface_rect = box_surface.get_rect()

        box_surface.set_colorkey((0, 255, 0))
        PlayVideo.apply_gradient(
                        box_surface,
               (0, 0, 200),
               (0, 0, 100),
                        box_width,
                        box_height,
                        alpha_start=100,
                        alpha_end=200
        )
        pygame.draw.rect(
                    box_surface,
                    WHITE,
                (0, 0, box_width, box_height),
                    1,
                    border_radius=10
        )
        message_line = "Randomizing master playlist..."

        # Blit semi-transparent box
        self.win.blit(box_surface, (box_x, box_y))

        # Render and position text
        line_spacing = 40
        text_surface = font_bold_regular.render(message_line, True, text_color)
        text_rect = text_surface.get_rect(center=(self.displayWidth // 2, box_y + 35 + line_spacing))
        self.win.blit(text_surface, text_rect)
        pygame.display.flip()

    def render_filename_text(self, text, y, font_size=60,outline_style="default"):
        """
        Renders and displays text with an optional outline on the screen.

        This method is used to render text on a Pygame surface with a specific font,
        color, and optional outline style. The rendered text is then displayed at the
        desired position on the main window. The text can be displayed with no outline,
        a default outline, or a blurred outline effect, depending on the selected
        outline style.

        Parameters:
            text (str): The text to be rendered and displayed.
            y (int): The y-coordinate at which to display the text on the screen.
            font_size (int, optional): The font size to use for the text. Defaults to 60.
            outline_style (str, optional): The style of the outline applied to the text.
                Available options are "default" for a standard outline and "blurred"
                for a blurred effect. Defaults to "default".

        Raises:
            Any errors that may occur during font loading, rendering, or blitting onto
            the Pygame window will be propagated as exceptions.
        """
        font = pygame.font.Font(self.FONT_DIR + "luximb.ttf", font_size)

        # Render text with no outline
        text_render = font.render(text, True, pygame.color.THECOLORS['dodgerblue'])
        text_width, text_height = text_render.get_size()

        # Create transparent surface for text
        text_surface = pygame.Surface((text_width + 20, text_height + 30), pygame.SRCALPHA)
        text_surface.fill((0, 0, 0, 0))  # Fully transparent background
        outline_color = pygame.color.THECOLORS['dodgerblue4']

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
        """
        Renders the filename text on the output display.

        This method handles the rendering of the filename associated with
        the video object at a specified vertical position on the display.
        It allows configuration of the font size used for rendering the
        filename text.

        Parameters:
            self: The instance of the class.

        Raises:
            None

        Returns:
            None
        """
        self.render_filename_text(self.vid.name, self.OSD_FILENAME_Y, font_size=26)

    def draw_play_icon(self, x, y):
        """
        Draws a play icon, including its outline, onto a pygame surface.

        This method renders a triangular play icon with an outline at a specified
        location on the display surface. The outline is drawn first by offsetting
        the play triangle in multiple directions, and then the actual triangle
        is drawn on top of the outline to create a visually distinct icon.

        Parameters:
        x (int): The x-coordinate of the top-left corner of the play icon.
        y (int): The y-coordinate of the top-left corner of the play icon.
        """
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
        """
        Draws a pause icon with two vertical bars at the specified position on the display.

        This method creates a pause icon by first preparing a transparent surface,
        adding outlined rectangles to represent the pause bars, filling the inner
        part of the rectangles with the desired color, and finally blitting the
        completed icon onto the main display at the specified coordinates.

        Args:
            x (int): The x-coordinate where the pause icon should be drawn.
            y (int): The y-coordinate where the pause icon should be drawn.
        """
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
        """
        Blits the play icon image at a specified position on the screen.

        Parameters:
        x (int): The x-coordinate where the play icon will be blitted.
        y (int): The y-coordinate where the play icon will be blitted.

        Returns:
        None
        """
        self.win.blit(self.playIcon, (x, y))

    def pause_icon(self, x, y):
        """
        Draws the pause icon at the specified coordinates on the screen.
        This method uses the blit function to render the pause icon image
        on the main display surface.

        Args:
            x (int): The x-coordinate where the pause icon should be drawn.
            y (int): The y-coordinate where the pause icon should be drawn.
        """
        self.win.blit(self.pauseIcon, (x, y))

    def foward_icon(self, x, y):
        """
        Blits the forward icon image onto the given coordinates on the display window.

        Parameters:
            x (int): The x-coordinate where the forward icon will be drawn.
            y (int): The y-coordinate where the forward icon will be drawn.

        Returns:
            None
        """
        self.win.blit(self.forwardIcon, (x, y))

    def rewind_icon(self, x, y):
        """
        Blits the rewind icon at the specified position on the screen.

        This method renders the rewind icon on the game window (or any
        designed surface). The position is specified by the x and y parameters,
        defining where the icon should appear on the target surface.

        Args:
            x (int): The x-coordinate for the position where the rewind icon
                     will be rendered.
            y (int): The y-coordinate for the position where the rewind icon
                     will be rendered.
        """
        self.win.blit(self.rewindIcon, (x, y))

    def get_fade_color(self,time_left, max_fade_time=10):
        """
        Calculate a faded color based on the time left and a maximum fade duration.

        The function interpolates between two colors (DodgerBlue and HotPink) based on
        a fade ratio derived from the amount of time left relative to a defined maximum
        fade time. The result is returned as an interpolated color in RGB format.

        Attributes:
            dodgerblue (pygame.Color): The RGB color value for 'dodgerblue'.
            amber (pygame.Color): The RGB color value for amber (255, 191, 0).
            blue4 (pygame.Color): The RGB color value for 'blue4' (0, 0, 139).
            cfblue (pygame.Color): The RGB color value for 'cool blue' (100, 149, 237).
            yellow (pygame.Color): The RGB color value for yellow (255, 255, 0).
            lightpink (pygame.Color): The RGB color value for light pink (255, 182, 193).
            hotpink (pygame.Color): The RGB color value for hot pink (255, 105, 180).

        Parameters:
            time_left (float): The current remaining time.
            max_fade_time (float): The maximum time over which fading occurs (default: 10).

        Returns:
            pygame.Color: The interpolated RGB color based on the fade ratio.
        """
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
        """
        Renders an on-screen display (OSD) text with optional fading and outlining effects.
        This function enables flexible customization for text positioning, appearance, and
        dynamic behavior based on video playback time.

        Arguments:
            text (str): The text content to be rendered on the OSD.
            x (int): The x-coordinate for placing the OSD text surface.
            y (int): The y-coordinate for placing the OSD text surface.
            curPos (float): The current playback position of the video in seconds.
            font_size (int, optional): Font size for rendering the OSD text. Defaults to 50.
            outline_style (str, optional): Style of the outline for the rendered text.
                Can be "default" or "blurred". Defaults to "default".
        """
        color = pygame.color.THECOLORS['dodgerblue']  # Default assignment
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
                text_surface.blit(outline_render, (dx + 15, dy + 15))  # More offsets for a thicker outline

        # **Render the actual text in the center**
        text_surface.blit(text_render, (15, 15))
        # **Blit the final text surface onto the main window**
        self.win.blit(text_surface, (x, y))

    def draw_osd_background(self, x, y, width, height):
        """
        Draws a semi-transparent on-screen display (OSD) background rectangle on the display at a specified position
        and size. This function is typically used for enhancing the visibility of overlay text or UI elements
        by dimming the underlying screen area.

        Args:
            x (int): The x-coordinate of the top-left corner of the background.
            y (int): The y-coordinate of the top-left corner of the background.
            width (int): The width of the background in pixels.
            height (int): The height of the background in pixels.
        """
        bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)  # Fully transparent layer
        bg_surface.fill((0, 0, 0, 128))  # Semi-transparent black

        # **Blit this background onto the main display**
        self.win.blit(bg_surface, (x, y))

    def OSD_clear(self, x, y):
        """
        Clears the on-screen display (OSD) text and its outline by filling the specified region with black.

        Attributes:
            osd_text_width: int
                The width of the OSD text.
            osd_text_height: int
                The height of the OSD text.

        Parameters:
            x: int
                The x-coordinate for the top-left of the OSD text.
            y: int
                The y-coordinate for the top-left of the OSD text.
        """
        # Account for max outline size
        outline_padding = 6
        clear_x, clear_y = x - outline_padding, y - outline_padding
        clear_width, clear_height = self.osd_text_width + (outline_padding * 2), self.osd_text_height + (outline_padding * 2)

        # Fill the expanded area to remove text + outline
        self.win.fill((0, 0, 0), (clear_x, clear_y, clear_width, clear_height))
        #pygame.display.update(clear_x, clear_y, clear_width, clear_height)

    def OSD_icon_clear(self,x, y):
        """
        Clears an on-screen display (OSD) icon by overwriting it with a background surface.

        This method removes an OSD icon from the specified position on the screen by
        creating a blank surface of the same size as the icon and placing it at the
        designated coordinates. The overwrite operation ensures the specified area
        is cleared and filled with the background color.

        Args:
            x (int): The x-coordinate of the top-left corner of the icon to be cleared.
            y (int): The y-coordinate of the top-left corner of the icon to be cleared.
        """
        background = pygame.Surface((48, 48))  # Create a blank surface
        background.fill((0, 0, 0))  # Fill it with the background color
        self.win.blit(background, (x, y))  # Overwrite the icon with the background
        #pygame.display.update(x, y, 48, 48)

    def reset_OSD_tracking(self):
        """
        Reset OSD tracking for a new video session.

        This method clears the previous timestamp tracking, resets seek behavior,
        and initializes relevant variables to ensure correct operation when loading
        a new video.

        Attributes
        ----------
        last_osd_position : float
            Tracks the timestamp position for the on-screen display.
        seek_flag : bool
            Indicates whether a seek operation is in progress.
        last_vid_info_pos : float
            Tracks the last known position in the video information.
        seek_flag2 : bool
            Indicates secondary seek operation behavior or state.
        """
        # Reset tracking when loading a new video**
        self.last_osd_position = 0.0  # Clear previous timestamp tracking
        self.seek_flag = False  # Reset seek behavior
        self.last_vid_info_pos = 0.0
        self.seek_flag2 = False

    def draw_OSD(self):
        """
        Handles the logic for drawing On-Screen Display (OSD) elements in a video player, such as pause/play
        icons and current playback position.

        Notes
        -----
        This method ensures that certain playback-related scenarios are handled correctly, such as seeking,
        position drops, and rendering the appropriate OSD elements. The OSD text is updated with the corrected
        playback position and total video duration.

        Raises
        ------
        AttributeError
            If the vid attribute or required attributes like seek_flag, OSD_curPos_flag are not set properly
            within the instance using this method.
        """
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
        """
        Render the progress bar onto the display window with visual customization, including colors,
        transparency, and dynamic resizing based on resolution.

        Attributes:
            progress_active (bool): Indicates whether the progress bar should be rendered.
            displayType (str): Specifies the display type used for determining resolution scaling.
            progress_percentage (float): Represents the current percentage of progress completed.
            progress_value (float): Current progress value used to calculate the fill width of the bar.
            displayHeight (int): The height of the display, used for scaling various parameters.
            displayWidth (int): The width of the display, used to calculate bar placement.
            FONT_DIR (str): Path to the directory containing font files for rendering text.
            help_visible (bool): Indicates whether the help overlay is visible on the display.
            video_info_box (bool): Determines if the video information box is currently displayed.

        Parameters:
            None

        Raises:
            None

        Returns:
            None
        """
        if self.progress_active:

            progressWidthBase = 400
            progressHeightBase = 30

            width_multiplier, height_multiplier = up_scale.scale_resolution(self.displayType) \
                if self.displayType in up_scale.resolution_multipliers else (1,1)
            progress_width = int(progressWidthBase * width_multiplier)
            progress_height = int(progressHeightBase * height_multiplier)
            DodgerBlue = pygame.color.THECOLORS['dodgerblue']
            progress_alpha = 150  # Transparency level (0-255)
            progress_color = DodgerBlue
            border_color = DODGERBLUE4
            progress_bg = (30, 30, 30, progress_alpha)  # Background with transparency
            scaled_font_size = up_scale.scale_font(24, self.displayHeight)
            font = pygame.font.Font(self.FONT_DIR + "LiberationSans-Regular.ttf", scaled_font_size)
            progress_text = font.render(f"{int(self.progress_percentage)}%",
                                        True,
                                        (255, 255, 255))  # White text

            # Create transparent surface
            progress_surface = pygame.Surface((progress_width, progress_height), pygame.SRCALPHA)
            #progress_surface.set_alpha(165)
            progress_surface.set_colorkey((0, 255, 0))
            progress_bar_rect = progress_surface.get_rect()
            if not self.help_visible and not self.video_info_box:
                PlayVideo.apply_gradient(progress_surface,
                                         DODGERBLUE,
                                         DODGERBLUE4,
                                         progress_width,
                                         progress_height,
                                         alpha_start=100,
                                         alpha_end=225
                                         )
            else:
                PlayVideo.apply_gradient(progress_surface,
                                         DODGERBLUE4,
                                         DODGERBLUE,
                                         progress_width,
                                         progress_height,
                                         alpha_start=100,
                                         alpha_end=225
                                         )

            progress_x = progress_bar_rect.x + (progress_width // 2) - (progress_text.get_width() // 2)
            progress_y = progress_bar_rect.y + (progress_height // 2) - (progress_text.get_height() // 2)

            # Fill progress dynamically
            fill_width = int(progress_width * (self.progress_value / 100))  # Scale width based on progress
            pygame.draw.rect(progress_surface,
                             (0, 0, 100),
                             (0, 0, fill_width, progress_height)
                             )
            pygame.draw.rect(progress_surface,
                             (30, 30, 30),
                             (0, 0, fill_width, progress_height),
                             1
                             )
            progress_surface.blit(progress_text,
                                  (progress_x, progress_y))
            # Blit progress bar to screen center
            self.win.blit(progress_surface,
                          ((self.displayWidth - progress_width) // 2, self.displayHeight // 2))

    def create_thumbnail(self, video_path):
        """
        Creates a thumbnail image from a video file by utilizing the FFmpeg utility. The
        method checks for valid input, scales the thumbnail based on the display type, and
        ensures the thumbnail file is correctly generated and saved in the specified cache
        directory.

        Parameters
        ----------
        video_path : str
            The file path of the video for which the thumbnail is to be created.

        Returns
        -------
        str
            The file path of the successfully created thumbnail image.

        Raises
        ------
        ValueError
            If the input video path is invalid or if there is an error related to the
            configured display type.
        OSError
            If the FFmpeg utility fails to process the video or the thumbnail file is not
            created successfully.
        Exception
            If an unexpected error occurs while creating the thumbnail.
        """
        try:
            if not video_path or not os.path.exists(video_path):
                raise ValueError(f"Invalid video path: {video_path}")

            thumbnail_path = os.path.join(self.CACHE_DIR, os.path.splitext(os.path.basename(video_path))[0] + ".jpg")

            try:
                # Scale up based on display resolution
                thumb_width, thumb_height = up_scale.scale_thumbnails(self.displayType) \
                    if self.displayType in up_scale.thumbnails else (256, 144)
                scale = f"scale={thumb_width}:{thumb_height}:flags=lanczos"

                # **Check if the file is a GIF**
                if video_path.lower().endswith(".gif"):
                    ffmpeg_cmd = [
                        "ffmpeg", "-hide_banner", "-loglevel", "error",
                        "-i", video_path, "-vf", scale, "-q:v", "2",
                        "-frames:v", "1", "-update", "1", thumbnail_path
                    ]
                else:
                    # **For standard video files**
                    ffmpeg_cmd = [
                        "ffmpeg", "-hide_banner", "-loglevel", "error",
                        "-i", video_path, "-ss", "00:00:05", "-vframes", "1",
                        "-vf", scale, "-q:v", "2", "-update", "1", thumbnail_path
                    ]

                # ** Ensure cache directory exists **
                os.makedirs(self.CACHE_DIR, exist_ok=True)

                # Run ffmpeg and check return code
                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    raise OSError(f"FFmpeg failed: {result.stderr}")

                # Verify thumbnail was created
                if not os.path.exists(thumbnail_path):
                    raise OSError("Thumbnail file was not created")

                return thumbnail_path

            except AttributeError as e:
                raise ValueError(f"Invalid display type configuration: {str(e)}")
            except subprocess.SubprocessError as e:
                raise OSError(f"Error running ffmpeg: {str(e)}")

        except (OSError, ValueError) as e:
            # Re-raise these exceptions as they already have appropriate messages
            raise
        except Exception as e:
            # Catch any other unexpected errors
            raise Exception(f"Unexpected error creating thumbnail: {str(e)}") from e

    def load_thumbnail(self, video_path):
        """
        Loads and caches a thumbnail for a given video file. The function retrieves the
        thumbnail from a cache if available, otherwise generates a new thumbnail, scales
        it to the appropriate size, and stores it in the cache for future use.

        Arguments:
            video_path: str
                Path to the video file for which the thumbnail is to be loaded.

        Returns:
            pygame.Surface or None
                The scaled thumbnail image as a pygame.Surface object if successfully
                loaded. Returns None if thumbnail generation or loading fails.

        Raises:
            pygame.error
                If an error occurs during loading or scaling of the thumbnail.

        """
        if video_path in self.thumbnail_cache:
            return self.thumbnail_cache[video_path]  # ✅ Return cached thumbnail immediately

        thumbnail_path = os.path.join(self.CACHE_DIR, os.path.splitext(os.path.basename(video_path))[0] + ".jpg")

        # **Generate thumbnail if missing**
        if not os.path.exists(thumbnail_path):
            thumbnail_path = self.create_thumbnail(video_path)
            if not os.path.exists(thumbnail_path):
                print(f"Failed to create thumbnail: {thumbnail_path}")
                return None

        try:
            # **Load the image**
            image_surface = pygame.image.load(thumbnail_path)
            thumb_width, thumb_height = up_scale.scale_thumbnails(self.displayType)  \
                if self.displayType in  up_scale.thumbnails else (256, 144)
            image_surface = pygame.transform.scale(image_surface, (thumb_width, thumb_height))
        except pygame.error as e:
            print(f"Error loading thumbnail: {e}")
            return None
        # **Store in cache for faster access**
        self.thumbnail_cache[video_path] = image_surface
        return image_surface

    def fade_in_out(self, video_info):
        """
        Handles fade-in and fade-out animation for the splash screen.

        This method stops the current video playback, displays a thumbnail
        image and performs a fade-in and fade-out animation on the splash
        screen using a gradient effect. Once the animation is complete, the
        previous video continues to play.

        Attributes:
            image_surface: pygame.Surface
                The object used to store and display the current thumbnail
                image on the screen.
            progress_timeout: int
                Timeout value used to control the animation's progress.
            Splash_Width: int
                The width of the splash screen surface.
            Splash_Height: int
                The height of the splash screen surface.
            vid: VideoObject
                An object controlling the video playback operations.

        Args:
            video_info (dict): A dictionary containing information about the video
                to be displayed during the fade-in and fade-out animation.
        """
        self.vid.stop()
        self.image_surface = self.load_thumbnail(self.videoList[self.currVidIndx])
        self.progress_timeout = 50

        DodgerBlue = pygame.color.THECOLORS['dodgerblue']
        DodgerBlue4 = pygame.color.THECOLORS['dodgerblue4']

        """Handles fade-in and fade-out animation for splash screen."""
        splash_surface = pygame.Surface((self.Splash_Width, self.Splash_Height), pygame.SRCALPHA)
        #splash_surface.set_alpha(175)
        splash_surface.set_colorkey((0, 255, 0))
        PlayVideo.apply_gradient(splash_surface,
                                 DODGERBLUE,
                                 DODGERBLUE4,
                                 self.Splash_Width,
                                 self.Splash_Height,
                                 alpha_start=125,
                                 alpha_end=225
                                 )
        splash_rect = (0, 0, self.Splash_Width, self.Splash_Height)
        pygame.draw.rect(splash_surface,
                         DodgerBlue,
                         splash_rect,
                         4,
                         border_radius=8
                         )

        '''
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
        '''
        self.vid.play()

    def setup_video_splash(self):
        """
        Sets up the video splash screen by collecting metadata about the current video,
        including file name, duration, playback speed, file size, and last accessed timestamp.

        Arguments:
            self

        Returns:
            A dictionary containing the video's metadata.

        """
        file_path = self.videoList[self.currVidIndx]
        filename = os.path.basename(file_path)
        last_access_timestamp = os.path.getatime(self.videoList[self.currVidIndx])
        last_access_datetime = datetime.datetime.fromtimestamp(last_access_timestamp).strftime("%m-%d-%Y %H:%M:%S")
        file_size_mb = os.path.getsize(self.videoList[self.currVidIndx]) / (1024 * 1024)
        duration = self.format_duration(self.vid.duration)
        fast_duration = self.format_duration(round(self.vid.duration / self.vid.speed))

        video_info = {
            "name": f"{filename}",
            "duration": f"{duration}",
            "speed": f"{self.opts.playSpeed}",
            "speed_duration": f"{fast_duration}",
            "file_size": f"{file_size_mb:.2f} MB",
            "last_accessed": f"{last_access_datetime}"
        }
        return video_info

    def reset_video_info_splash(self):
        """
        Resets the video metadata splash information.

        This method clears the video metadata display box and disables any active
        tooltips associated with it. It resets internal flags related to the video
        information display state.

        Raises:
            This method does not raise any exceptions.
        """
        # reset the video metadata box and tooltip if active
        if self.video_info_box:
            self.video_info_temp = True
            self.video_info_box = False
            self.video_info_box_tooltip = False

    def draw_video_splash(self):
        """
        Draws a video splash screen with relevant details such as video title, duration, speed, file size, thumbnail,
        playback order, and last access time. The splash screen includes gradient styling, text, and video thumbnail.

        Parameters:
            None

        Raises:
            None

        Returns:
            None
        """
        video_info = self.setup_video_splash()
        Blue = pygame.color.THECOLORS['darkblue']
        DarkViolet = pygame.color.THECOLORS['darkviolet']
        DarkOrchid = pygame.color.THECOLORS['darkorchid']
        Crimson = pygame.color.THECOLORS['crimson']
        DarkSlateBlue = pygame.color.THECOLORS['darkslateblue']
        Fuchsia = pygame.color.THECOLORS['fuchsia']
        DodgerBlue = pygame.color.THECOLORS['dodgerblue']
        DodgerBlue4 = pygame.color.THECOLORS['dodgerblue4']

        w_multi, h_multi = up_scale.scale_resolution(self.displayType) \
            if self.displayType in up_scale.resolution_multipliers else (1,1)
        Splash_Width = int(w_multi * self.Splash_Width_Base)
        Splash_Height = int(h_multi * self.Splash_Height_Base)

        self.vid.stop()
        self.image_surface = self.load_thumbnail(self.videoList[self.currVidIndx])
        self.progress_timeout = 50

        splash_surface = pygame.Surface((Splash_Width, Splash_Height), pygame.SRCALPHA)
        splash_surface.set_alpha(175)
        splash_surface.set_colorkey((0, 255, 0))
        PlayVideo.apply_gradient(splash_surface,
                                 (0, 0, 255),
                                 (0, 0, 100),
                                 Splash_Width,
                                 Splash_Height,
                                 alpha_start=100,
                                 alpha_end=225
                                 )
        splash_rect = (0, 0, Splash_Width, Splash_Height)
        pygame.draw.rect(splash_surface,
                         DodgerBlue,
                         splash_rect,
                         4,
                         border_radius=8
                         )

        RECT_X = (self.displayWidth - Splash_Width) // 2
        RECT_Y = (self.displayHeight - Splash_Height) // 2
        self.win.fill(BLACK)

        # Text positions
        text_x =  RECT_X + 50
        text_y = RECT_Y + 0

        self.win.blit(splash_surface, (RECT_X, RECT_Y))

        original_font_sizes = [28, 36, 40]
        scaled_font_sizes = up_scale.get_scaled_fonts(original_font_sizes, self.displayHeight)

        font_regular_28 = pygame.font.Font(self.FONT_DIR + 'RobotoCondensed-Regular.ttf', scaled_font_sizes[0])    # 28
        font_regular_36 = pygame.font.Font(self.FONT_DIR + 'RobotoCondensed-Regular.ttf', scaled_font_sizes[1])    # 36
        font_regular_40 = pygame.font.Font(self.FONT_DIR + 'RobotoCondensed-Regular.ttf', scaled_font_sizes[2])    # 40

        title_text = font_regular_28.render(f"{video_info['name']}", True, Fuchsia)
        duration_text = font_regular_28.render(f"Duration: {video_info['duration']}", True, WHITE)
        sp_dur_text = f"{(video_info['speed_duration'] if int(self.vid.speed) != 1 else video_info['duration'])} @ {self.format_playback_speed(self.vid.speed)}"
        speed_dur_text = font_regular_28.render(sp_dur_text, True, (pygame.color.THECOLORS['red'] if round(self.vid.speed) != 1.0 else DarkViolet))
        size_text = font_regular_28.render(f"File Size: {video_info['file_size']}", True, WHITE)
        access_text = font_regular_28.render(f"Last Accessed: {video_info['last_accessed']}", True, WHITE)
        playing_text = font_regular_40.render(f"Playing {self.currVidIndx + 1} of {len(self.videoList)}", True, WHITE)

        #self.win.blit(splash_surface, (RECT_X, RECT_Y))

        # Thumbnail positions
        image_x = RECT_X + 975
        image_y = RECT_Y + 225

        thumb_surface = pygame.Surface((image_x, image_y), pygame.SRCALPHA)
        thumb_surface.set_alpha(175)
        thumb_surface.set_colorkey((0, 255, 0))

        image_rect = (0, 0, 512, 288)
        pygame.draw.rect(
                    self.image_surface,
                    DodgerBlue,
                    image_rect,
                         2,
                    border_radius=8
        )

        self.win.blit(playing_text, (text_x, text_y + 25))          #50
        self.win.blit(title_text, (text_x, text_y + 125)) 		    #100
        self.win.blit(duration_text, (text_x, text_y + 225))	    #150
        self.win.blit(speed_dur_text, (text_x, text_y + 325))  # 200
        self.win.blit(size_text, (text_x, text_y + 425))  # 250
        self.win.blit(access_text, (text_x, text_y + 525))  # 300
        self.win.blit(self.image_surface, (image_x, image_y))

        pygame.display.flip()
        pygame.time.delay((self.opts.loopDelay * 1000))
        self.vid.play()

    def print_cli_options(self):
        """
        Prints debugging information about various configuration options to the console.

        This method outputs the state of configuration options related to paths, video playback,
        audio settings, and file handling in a formatted, color-coded manner. It prints debug
        information for internal CLI options and flags that are used to control the program's
        behavior and operations.

        Attributes:
            opts (object): An object containing various CLI option properties related to paths,
                video playback, audio settings, system, and file handling.
            mute_flag (bool): Internal flag to mute or unmute audio.
            OSD_curPos_flag (bool): Flag denoting whether On-Screen Display cursor position is enabled.
            bcolors (object): Object containing color codes for formatted console output.
        """
        # Print cli options to the console for debug purposes
        print()
        # Required but mutually exclusive options
        Paths = self.opts.Paths
        loadPlayList = self.opts.loadPlayList
        result = subprocess.run(["xrandr", "--listactivemonitors"], capture_output=True, text=True)

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
        dispTitles = self.opts.dispTitles

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
        print(f"{self.bcolors.BOLD}opts.loadPlayList:{(self.bcolors.Magenta_f if loadPlayList is not None else self.bcolors.Yellow_f)} {loadPlayList}{self.bcolors.RESET}")
        print(f"{self.bcolors.BOLD}listActiveMonitors:\n{self.bcolors.Magenta_f}{result.stdout}{self.bcolors.RESET}")

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
        print(f"{self.bcolors.BOLD}opts.dispTitles: {self.bcolors.Magenta_f}{dispTitles}{self.bcolors.RESET}")
        print()
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
        """
        Draws a video information box using the provided file details.

        This function generates a visual panel displaying information about a video
        file, including file path and filename, and utilizes a predefined drawing
        utility to render the details within the application window.

        Attributes:
            drawVidInfo (DrawVideoInfo): An instance of the DrawVideoInfo class used
                for rendering the information box.

        Args:
            FilePath (str): The complete path to the video file including the
                directory location.
            Filename (str): The name of the video file without the directory path.
        """
        self.drawVidInfo = DrawVideoInfo(self.win, FilePath, Filename, self.USER_HOME)
        self.drawVidInfo.draw_info_box()
        #pygame.display.flip()

    def DrawVideoPlayBar(self):
        """
        Draws the video play bar component within the application.

        This method is responsible for rendering the video play bar through
        the associated functionality of the `videoPlayBar` instance. It
        provides a visual interface for controlling video playback.

        """
        self.videoPlayBar.drawVideoPlayBar()

    def printMetaData(self):
        """
        Prints the metadata of the currently active video.

        This method checks if the video is active and then retrieves its metadata using
        the `get_metadata` method. The metadata is subsequently printed in key-value
        pairs.

        Raises:
            AttributeError: If the video attribute `vid` is not set or an expected method
            or property within it does not exist.
        """
        if self.vid.active:
            metadata = self.vid.get_metadata()
            print()
            for key, value in metadata.items():
                print(f"{key} : {value}")
            print()

    def draw_help(self, is_hovered):
        """
        Draws the help overlay and returns the bounding rectangle of the help button.

        Generates the rect object representing the help button area and draws the
        overlay depending on the hover state. This function is frequently used to
        interact with the UI and allow users to toggle help display.

        Args:
            is_hovered (bool): Specifies whether the help button is currently hovered.

        Returns:
            pygame.Rect: A rectangle object representing the boundary of the help
            button for further interaction or positioning.
        """
        self.help_button_rect =  self.draw_help_overlay(is_hovered)
        return self.help_button_rect

    def draw_help_overlay(self, is_hovered):
        """
        Draws a help overlay window with explanatory text and a clickable button.

        The help overlay is visually styled with a gradient background, formatted text
        (headings and regular lines), and an "OK" button for interaction. The overlay
        adapts its size, fonts, and layout dynamically based on the display resolution
        and scaling factors. Text is split into left and right columns, with properly
        formatted headings and body content. The "OK" button has hover effects and
        can be clicked to perform an action.

        Parameters:
            is_hovered (bool): Determines if the mouse is hovering over the "OK" button.

        Returns:
            pygame.Rect: A rect object representing the clickable area of the "OK" button.
        """
        # Scale fonts
        originalFontSizes = [18, 17, 24]
        scaled_font_size = up_scale.get_scaled_fonts(originalFontSizes, self.displayHeight)
        font_help_text = pygame.font.Font(self.FONT_DIR + 'Arial.ttf', scaled_font_size[0])
        font_help_heading = pygame.font.Font(self.FONT_DIR + 'Arial_Bold.ttf', scaled_font_size[1])
        font_button = pygame.font.Font(self.FONT_DIR + 'Montserrat-Bold.ttf', scaled_font_size[2])

        # Scale box dimensions using display type multipliers
        baseBoxWidth = 600
        baseBoxHeight = 600
        w_mult, h_mult = up_scale.resolution_multipliers[self.displayType]
        BOX_WIDTH = int(baseBoxWidth * w_mult)
        BOX_HEIGHT = int(baseBoxHeight * h_mult)
        BOX_X = (self.displayWidth - BOX_WIDTH) // 2
        BOX_Y = (self.displayHeight - BOX_HEIGHT) // 2

        y_offset_heading = int(font_help_heading.get_height() * (h_mult + 0.1))
        y_offset_text = int(font_help_text.get_height() * (h_mult - 0.6))

        # Create and draw the gradient background
        gradient_surface = pygame.Surface((BOX_WIDTH, BOX_HEIGHT), pygame.SRCALPHA)
        gradient_surface.set_colorkey((0, 255, 0))
        PlayVideo.apply_gradient(
            gradient_surface,
            (0, 0, 255),
            (0, 0, 100),
            BOX_WIDTH,
            BOX_HEIGHT,
            alpha_start=100,
            alpha_end=200
        )

        pygame.draw.rect(
            self.win,
            DODGERBLUE,
            (BOX_X, BOX_Y, BOX_WIDTH, BOX_HEIGHT),
            4,
            border_radius=8
        )
        #self.win.blit(gradient_surface, (BOX_X, BOX_Y))

        y_constant_start = 20 / BOX_HEIGHT
        y_constant_end = round((0.875/h_mult), 3)
        # Draw a vertical separator line (this will always be drawn)
        pygame.draw.line(
            gradient_surface,
            WHITE,
            (BOX_WIDTH // 2, int(BOX_HEIGHT * y_constant_start)),
            # (BOX_WIDTH // 2, int(BOX_HEIGHT * 0.875)),
            (BOX_WIDTH // 2, int(BOX_HEIGHT * h_mult * y_constant_end)),
            2
        )

        pygame.draw.rect(
                         self.win,
                         DODGERBLUE,
                         (BOX_X, BOX_Y, BOX_WIDTH, BOX_HEIGHT),
                         4,
                         border_radius=8
        )
        # The rest of the drawing code remains the same until button dimensions...
        LEFT_MARGIN = int(BOX_WIDTH * 0.05)     # 5% of box width
        RIGHT_COLUMN_X = int(BOX_WIDTH * 0.55)  # Slightly right of center line

        # Render left column text
        y_start = 25
        line_offset = font_help_text.get_height() + 5
        y_offset = y_start
        for line in _help_.HELP_TEXT_LEFT.split("\n"):
            color = HEADING_COLOR if line.isupper() else TEXT_COLOR
            text_surface = (
                font_help_text.render(line.strip(), True, color)) \
                if not line.isupper() \
                else \
                font_help_heading.render(line.strip(),True, color)

            gradient_surface.blit(text_surface, (LEFT_MARGIN, y_offset))    # left column
            if line.isupper():
                text_width, _ = font_help_heading.size(line.strip())
                pygame.draw.aaline(
                    gradient_surface,
                    HEADING_COLOR,
                    (LEFT_MARGIN, y_offset + line_offset),
                    (LEFT_MARGIN + text_width, y_offset + line_offset)
                )
                #y_offset += int(font_help_heading.get_height() * 1.9)
                y_offset += y_offset_heading
            else:
                #y_offset += int(font_help_text.get_height() * 1.2)
                y_offset += y_offset_text

        # Render right column text
        y_offset = y_start
        for line in _help_.HELP_TEXT_RIGHT.split("\n"):
            color = HEADING_COLOR if line.isupper() else TEXT_COLOR
            text_surface = (
                font_help_text.render(line.strip(), True, color)) \
                if not line.isupper() \
                else font_help_heading.render(line.strip(), True, color)

            gradient_surface.blit(text_surface, (RIGHT_COLUMN_X, y_offset))       # Right column
            if line.isupper():
                text_width, _ = font_help_heading.size(line.strip())
                pygame.draw.aaline(
                    gradient_surface,
                    HEADING_COLOR,
                    (RIGHT_COLUMN_X, y_offset + line_offset),
                    (RIGHT_COLUMN_X + text_width, y_offset + line_offset)
                )

                #y_offset += int(font_help_heading.get_height() * 1.9)
                y_offset += y_offset_heading
            else:
                 #y_offset += int(font_help_text.get_height() * 1.2)
                y_offset += y_offset_text

        self.win.blit(gradient_surface, (BOX_X, BOX_Y))

        # Scale button dimensions
        buttonWidthBase = 120
        buttonHeightBase = 40
        button_width = int(buttonWidthBase * w_mult)
        button_height = int(buttonHeightBase * h_mult)

        # Scale button position
        button_x = BOX_X + BOX_WIDTH // 2 - button_width // 2
        button_y = BOX_Y + BOX_HEIGHT - int(61 * h_mult)  # Scale the offset too
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # Draw the OK button with the hover effect
        button_color = DODGERBLUE if is_hovered else DODGERBLUE4
        pygame.draw.rect(self.win, button_color, button_rect, border_radius=8)
        pygame.draw.rect(self.win, BLACK, button_rect, 1, border_radius=8)

        # Scale icon position
        icon_x_offset = int(20 * w_mult)
        icon_y_offset = int(9 * h_mult)
        text_x_offset = int(45 * w_mult)
        text_y_offset = int(4 * h_mult)

        # Draw check icon and button text
        self.win.blit(self.check_icon, (button_x + icon_x_offset, button_y + icon_y_offset))
        ok_surface = font_button.render("OK", True, WHITE)
        self.win.blit(ok_surface, (button_x + text_x_offset, button_y + text_y_offset))

        self.help_button_rect = button_rect
        return button_rect

    def get_video_title(self, video_path: str) -> Optional[str]:
        """
        Retrieves the title from the metadata of a video file using ffprobe. The function attempts to
        extract the title from the tags in the format metadata if it exists. If the title is
        not available or an error occurs during processing, the function will return None.

        Args:
            video_path: Path to the video file as a string.

        Returns:
            An optional string containing the title of the video. If the title is not present or
            an error occurs, returns None.

        Raises:
            This function does not raise exceptions explicitly but will handle errors internally
            such as subprocess execution failures or JSON decoding issues.
        """
        try:
            # Construct the ffprobe command
            cmd = [
                'ffprobe',
                '-v', 'quiet',  # Suppress unnecessary output
                '-print_format', 'json',  # Output in JSON format
                '-show_format',  # Show format information (including metadata)
                video_path
            ]

            # Run ffprobe command and capture output
            result = subprocess.run(cmd, capture_output=True, text=True)

            # Check if the command was successful
            if result.returncode != 0:
                return None

            # Parse the JSON output
            data = json.loads(result.stdout)

            # Extract title from metadata if it exists
            if 'format' in data and 'tags' in data['format']:
                # FFprobe stores metadata in tags, and title might be uppercase or lowercase
                tags = data['format']['tags']
                # Try both uppercase and lowercase keys
                return tags.get('title') or tags.get('TITLE')

            return None

        except (subprocess.SubprocessError, json.JSONDecodeError, KeyError) as e:
            # Handle any errors that might occur during execution
            print(f"Error reading video metadata: {str(e)}")
            return None

    '''
    def draw_help_overlay(self, is_hovered):

        """
        Redraws the entire help overlay, including the gradient background,
        text, and OK button. The button color changes when hovered.
        Returns a pygame.Rect representing the OK button.
        """
        BOX_HEIGHT = 570
        BOX_WIDTH = 800
        BOX_X = (self.displayWidth - BOX_WIDTH) // 2
        BOX_Y = (self.displayHeight - BOX_HEIGHT) // 2

        # Create and draw the gradient background
        gradient_surface = pygame.Surface((BOX_WIDTH, BOX_HEIGHT), pygame.SRCALPHA)
        gradient_surface.fill((0, 0, 0, 175))
        gradient_surface.set_colorkey((0, 255, 0))
        PlayVideo.apply_gradient(
                                 gradient_surface,
                                 DODGERBLUE,
                                 DODGERBLUE4,
                                 BOX_WIDTH,
                                 BOX_HEIGHT,
                                 alpha_start=165,
                                 alpha_end=200
        )
        self.win.blit(gradient_surface, (BOX_X, BOX_Y))

        # Draw a vertical separator line (this will always be drawn)
        pygame.draw.line(gradient_surface, WHITE, (400, 20), (400, 500), 2)

        pygame.draw.rect(self.win,
                         WHITE,
                        (BOX_X, BOX_Y, BOX_WIDTH, BOX_HEIGHT),
                         3,
                         border_radius=15
                        )

        # Render left column text
        y_start = 20
        line_offset = self.font_help.get_height() + 5
        y_offset = y_start
        for line in _help_.HELP_TEXT_LEFT.split("\n"):
            color = HEADING_COLOR if line.isupper() else TEXT_COLOR
            text_surface = (self.font_help.render(line.strip(), True, color)) if not line.isupper() else self.font_help_bold.render(line.strip(), True, color )
            gradient_surface.blit(text_surface, (50, y_offset))
            if line.isupper():
                text_width, _ = self.font_help_bold.size(line.strip())
                pygame.draw.aaline(gradient_surface, HEADING_COLOR, (50, y_offset + line_offset),
                                   (50 + text_width, y_offset + line_offset))
                y_offset += 35
            else:
                y_offset += 25

        # Render right column text
        y_offset = y_start
        for line in _help_.HELP_TEXT_RIGHT.split("\n"):
            color = HEADING_COLOR if line.isupper() else TEXT_COLOR
            #text_surface = self.font_help.render(line.strip(), True, color)
            text_surface = (self.font_help.render(line.strip(), True,color)) if not line.isupper() else self.font_help_bold.render(line.strip(), True, color)
            gradient_surface.blit(text_surface, (450, y_offset))
            if line.isupper():
                text_width, _ = self.font_help_bold.size(line.strip())
                pygame.draw.aaline(gradient_surface, HEADING_COLOR, (450, y_offset + line_offset),
                                   (450 + text_width, y_offset + line_offset))
                y_offset += 35
            else:
                y_offset += 25

        self.win.blit(gradient_surface, (BOX_X, BOX_Y))

        # Define button geometry (OK button)blit(
        button_x = BOX_X + BOX_WIDTH // 2 - 60
        button_y = BOX_Y + BOX_HEIGHT - 60
        button_width = 120
        button_height = 40
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # Draw the OK button with hover effect
        button_color = DODGERBLUE4 if is_hovered else DODGERBLUE
        pygame.draw.rect(self.win, button_color, button_rect, border_radius=10)
        pygame.draw.rect(self.win, BLACK, button_rect, 1, border_radius=10)

        # Draw check icon and button text
        self.win.blit(self.check_icon, (button_x + 10, button_y + 4))
        ok_surface = self.font_button.render("OK", True, WHITE)
        self.win.blit(ok_surface, (button_x + 50, button_y + 5))

        # Update the full display (or you can update only portions if desired)
        self.help_button_rect = button_rect
        return button_rect
    '''

    # brightness/contrast
    def render_frame(self):
        """
        Renders the current video frame with optional effects if the  brightness/contrast control panel
        is visible. This process involves locking the video surface, creating a copy
        of the frame, applying effects if needed, and unlocking the surface.

        Returns
        -------
        Optional[Surface]
            A copy of the current frame with effects applied if the control panel
            is visible, or None if the video frame surface is not available.
        """
        if self.vid.frame_surf is None:
            return None

        # Lock the surface before creating a copy
        self.vid.frame_surf.lock()
        try:
            frame = self.vid.frame_surf.copy()
        finally:
            # Always unlock the surface
            self.vid.frame_surf.unlock()

        # Now apply effects if control panel is visible
        if self.control_panel.is_visible:
            frame = self.control_panel.apply_effects(frame)

        return frame

    # brightness/contrast
    def draw(self, screen):
        """
        Draws the UI components on the provided screen.

        This method is responsible for rendering the control panel and the edge
        panel on the specified screen. It assumes the screen passed as an argument
        has the necessary context to display these components.

        Parameters:
        screen: Any
            The graphical surface or canvas object where the UI components
            will be drawn.
        """
        # ... other drawing code ...
        self.control_panel.draw(screen)
        self.edge_panel.draw(screen)

    def blit_video_title(self):
        """
        Renders a video title on a display, centering it horizontally and positioning it at a fixed
        vertical offset from the bottom of the screen. Applies a bold font and a text outline for
        better readability.

        Attributes:
            video_title (str): The title of the video to be displayed.
            displayHeight (int): The height of the display in pixels.
            displayWidth (int): The width of the display in pixels.
            FONT_DIR (str): The directory containing the font files.
            win (pygame.Surface): The display surface where the title is rendered.

        Raises:
            Exception: If an error occurs during the rendering process.

        Notes:
            - The function only renders the title if the `video_title` attribute is defined and not
              empty.
            - The text is outlined by rendering the same text in a black color with slight offsets
              in multiple directions.
            - The main text is rendered in a Dodger Blue color on top of the outline.
        """
        if not hasattr(self, 'video_title') or not self.video_title:
            return
        try:
            font_size = up_scale.scale_font(36, self.displayHeight)
            font_bold = pygame.font.Font(self.FONT_DIR + 'Arial_Black.ttf', font_size)

            # Create the outline by rendering the text in black with small offsets
            outline_color = (0, 0, 0)  # Black color for outline
            outline_surfaces = []
            for dx, dy in [(1, 1), (-1, -1), (1, -1), (-1, 1),  # Diagonals
                           (0, 1), (0, -1), (1, 0), (-1, 0)]:  # Sides
                outline_surface = font_bold.render(self.video_title, True, outline_color)
                outline_surfaces.append((outline_surface, dx, dy))

            # Create the main text surface
            text_surface = font_bold.render(self.video_title, True, DODGERBLUE)

            # Get the width of the text surface
            text_width = text_surface.get_width()

            # Calculate position to center the text horizontally
            x_position = (self.displayWidth - text_width) // 2
            # Position 250 pixels from the bottom
            y_position = self.displayHeight - 250

            # First render all the outline surfaces
            for outline_surf, dx, dy in outline_surfaces:
                self.win.blit(outline_surf, (x_position + dx, y_position + dy))

            # Finally render the main colored text on top
            self.win.blit(text_surface, (x_position, y_position))

        except Exception as e:
            print(f"Error blitting title: {str(e)}")

    def print_frame_surf(self):
        print(f"size:({self.vid.frame_surf.get_size()}x{self.vid.frame_surf.get_bitsize()}: flags: {self.vid.frame_surf.get_flags()})")

    def update_GUI_components(self):
        """
        Updates and manages the GUI components based on the current state of the
        application and provided flags. Responsible for rendering, interacting with
        video controls, displaying video information, and handling other GUI-specific
        tasks.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Raises
        ------
        None
        """

        # Draw bilateral filter panel if it's visible
        if hasattr(self, 'show_filter_panel') and self.show_filter_panel:
            if hasattr(self, 'bilateral_panel'):
                # Simple approach - let the panel handle everything
                self.bilateral_panel.draw(self.win)

        '''        
        # Draw bilateral filter panel if it's visible
        if hasattr(self, 'show_filter_panel') and self.show_filter_panel:
            if hasattr(self, 'bilateral_panel'):
                BOX_WIDTH = 365
                BOX_HEIGHT = 220
                # Create a scaled surface for 4K displays
                scaling_factor = up_scale.get_scaling_factor(self.displayHeight)
                if scaling_factor > 1.0:
                    # Draw to a temporary surface, then scale it up
                    temp_surface = pygame.Surface((BOX_WIDTH, BOX_HEIGHT), pygame.SRCALPHA)
                    temp_surface.set_alpha(150)

                    #temp_surface.fill((0, 255, 255))  # Fill with CYAN so you can see it!
                    temp_surface.fill(DODGERBLUE4)
                   # self.bilateral_panel.draw(temp_surface)

                    # Scale up and blit to main screen
                    #scaled_size = (int(400 * scaling_factor), int(300 * scaling_factor))
                    scaled_size = (int(BOX_WIDTH * scaling_factor), int(BOX_HEIGHT * scaling_factor))
                    scaled_surface = pygame.transform.scale(temp_surface, scaled_size)
                    print(f"scaled display: width: {scaled_size[0]}, height: {scaled_size[1]}")
                    PlayVideo.apply_gradient(
                        scaled_surface,
                        (0, 0, 100),
                        (0, 0, 255),
                        scaled_size[0],
                        scaled_size[1],
                        alpha_start=100,
                        alpha_end=225
                    )
                    self.bilateral_panel.draw(scaled_surface)
                    self.win.blit(scaled_surface, (self.displayWidth - scaled_size[0] - 20, 20))
                else:
                    self.bilateral_panel.draw(self.win)
        '''

        if self.help_visible:
            self.help_button_rect = self.draw_help(self.is_hovered)

        if self.drawVideoPlayBarFlag:
            self.videoPlayBar.loop_flag = self.opts.loop_flag
            self.videoPlayBar.volume = self.vid.get_volume()
            self.videoPlayBar.muted = self.vid.muted
            self.videoPlayBar.playbackSpeed = self.vid.speed
            self.videoPlayBar.vid_paused = self.vid.paused
            self.videoPlayBar.vid_duration = self.format_seconds(round(self.vid.duration / self.vid.speed, 1))
            self.videoPlayBar.vid_curpos = self.format_seconds(int(self.vid.get_pos()))
            self.videoPlayBar.drawVideoPlayBar()
            if self.drawVideoPlayBarToolTip:
                self.videoPlayBar.draw_tooltip(self.drawVideoPlayBarToolTipText,
                                               self.drawVideoPlayBarToolTipMouse_x,
                                               self.drawVideoPlayBarToolTipMouse_y
                                               )

        if self.draw_OSD_active:
            if not (self.seekFwd_flag or self.seekRewind_flag):
                self.draw_OSD()
                # self.draw_filename()

        if self.status_bar_visible:
            self.displayVideoInfo(self.win,
                                  self.vid.name,
                                  self.format_duration(self.vid.duration),
                                  self.format_duration(self.opts.actualDuration),
                                  round(self.opts.playSpeed, 1),
                                  self.vid.get_volume(),
                                  self.vid.get_pos()
                                  )

        if self.video_info_temp:
            self.video_info_box = True
            filename = self.vid.name + self.vid.ext
            path = os.path.dirname(self.videoList[self.currVidIndx])
            filepath = os.path.join(path, "")
            self.filePath = filepath
            self.DrawVideoInfoBox(filepath, filename)
            self.video_info_temp = False
            self.video_info_box_tooltip = False
            self.video_info_box_path_tooltip = False

        if self.video_info_box:
            self.drawVidInfo.draw_info_box()
            if self.video_info_box_tooltip:
                self.drawVidInfo.draw_tooltip(self.win,
                                              # self.vid.name + self.vid.ext,
                                              self.vid.path,
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
            time.sleep(1)
            self.vid.resume()

        if self.shuffleSplashFlag:
            self.shuffleSplashFlag = False
            self.vid.pause()
            self.shuffleSplash()
            time.sleep(1)
            self.vid.resume()

        # Attempt to adjust vid.frame so the title doesn't blit on a blank screen
        if self.opts.dispTitles is not None and self.vid.frame >= 125:
            match self.opts.dispTitles:
                case 'all':
                    self.blit_video_title()
                case 'landscape':
                    if not PlayVideo.is_portrait(self.win, self.displayWidth):
                        self.blit_video_title()
                case 'portrait':
                    if PlayVideo.is_portrait(self.win, self.displayWidth):
                        self.blit_video_title()

    @staticmethod
    def median_blur(frame, kernel_size=5):
        """
        Apply a median blur to the given image frame using a specified kernel size.

        Median blur is primarily used to reduce noise in an image while preserving edges,
        by replacing each pixel's value with the median of the intensities of pixels in
        a defined neighborhood. This helps maintain the sharpness of edges in the image.

        Arguments:
            frame: numpy.ndarray
                The input image frame to which the median blur will be applied. Must be
                a valid 2D or 3D array representing a grayscale or colored image.
            kernel_size: int, optional
                The size of the kernel to be used for the blur. Must be a positive odd
                integer greater than 1. Default value is 5.

        Returns:
            numpy.ndarray
                The blurred image frame, resulting from applying the median blur
                operation.
        """
        return cv2.medianBlur(frame, kernel_size)

    @staticmethod
    def gaussian_blur(frame, kernel_size=(5, 5)):
        """
        Apply Gaussian Blur to an image frame.

        This method applies a Gaussian blur to the input image using a specified kernel
        size. The Gaussian blur is used to reduce image noise and detail.

        Args:
            frame: The input image frame to be blurred.
            kernel_size (tuple[int, int], optional): The size of the Gaussian kernel.
                Default is (5, 5).

        Returns:
            numpy.ndarray: The blurred image.
        """
        return cv2.GaussianBlur(frame, kernel_size, 0)

    @staticmethod
    def sepia(frame):
        """
        Applies a sepia-tone effect to the given image frame.

        This static method transforms the colors of an image frame using a predefined
        sepia conversion matrix. The transformation alters the intensity of the
        original pixels to create a classic sepia-tone effect, commonly used to give
        images a vintage appearance.

        Args:
            frame (numpy.ndarray): A 2D or 3D numpy array representing the image frame
            to which the sepia effect will be applied.

        Returns:
            numpy.ndarray: A new image frame with the sepia effect applied, having the
            same dimensions as the input frame.

        """
        sepia_matrix = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131]
        ])
        return cv2.transform(frame, sepia_matrix)

    @staticmethod
    def edge_detect(frame):
        """
        Performs edge detection on a given image frame using the Canny algorithm and
        converts the resultant edges back to a 3-channel image.

        Second parameter (100) = Lower threshold for edge detection
        Third parameter (200) = Upper threshold for edge detection

        Edges with intensity gradient above the upper threshold are sure edges
        Edges with intensity gradient below the lower threshold are discarded
        Edges between the thresholds are considered edges only if they're connected to sure edges

        (50, 150): More sensitive, detects more edges including weaker ones
        (100, 200): Balanced detection (default)
        (150, 250): Less sensitive, only detects strong edges


        Attributes:
            None

        Parameters:
            frame: numpy.ndarray
                The input image frame on which edge detection is to be applied. It
                is assumed to be a single-channel grayscale image.

        Returns:
            numpy.ndarray: A 3-channel image containing the detected edges, with each
            channel being identical.

        Raises:
            None
        """
        edges = cv2.Canny(frame, 100, 200)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def vignette(frame):
        """
        Applies a vignette effect to the given image frame.

        The vignette effect is achieved by creating a Gaussian kernel mask and applying it
        to each channel of the image. The mask reduces the brightness or intensity of the
        pixels near the edges compared to the center.

        Parameters:
            frame (numpy.ndarray): The input image frame as a 3D array. It is expected to have
                                   three color channels (e.g., RGB or BGR).

        Returns:
            numpy.ndarray: The image frame with the vignette effect applied.
        """
        rows, cols = frame.shape[:2]
        # Generate vignette mask
        kernel_x = cv2.getGaussianKernel(cols, cols / 2)
        kernel_y = cv2.getGaussianKernel(rows, rows / 2)
        kernel = kernel_y * kernel_x.T
        mask = kernel / kernel.max()

        # Apply the mask to each channel
        for i in range(3):
            frame[:, :, i] = frame[:, :, i] * mask
        return frame

    @staticmethod
    def adjust_saturation(frame, factor=1.5):
        """
        Adjusts the saturation of a given image frame by a specified factor.

        This method takes an image frame as input, converts it to HSV color space,
        modifies the saturation channel by multiplying it with the given factor,
        and converts the image back to BGR color space.

        Parameters:
            frame: numpy.ndarray
                The input image frame in BGR color space, represented as a NumPy array.

            factor: float, optional
                The factor by which the image's saturation is adjusted. Defaults to 1.5.

        Returns:
            numpy.ndarray
                The image with adjusted saturation, in BGR color space.
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * factor, 0, 255)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    @staticmethod
    def simple_comic_effect(frame):
        """
        Very simple comic-style effect focusing just on edges and basic color reduction
        """
        try:
            if frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)

            # Simple edge detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

            # Simple color quantization
            result = frame // 32 * 32

            # Combine
            result = cv2.subtract(result, edges)
            return cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print(f"Error in comic effect: {str(e)}")
            return frame

    @staticmethod
    def comic_sharp_effect(frame,
                           bilateral_d=5,
                           bilateral_color=60,  # Reduced from default
                           bilateral_space=60,  # Reduced from default
                           edge_low=40,  # Slightly more sensitive
                           edge_high=140,
                           color_quant=20,  # Slightly more colors
                           sharpen_amount=0.5):  # Moderate sharpening by default
        """
        1. bilateral_d (Diameter of pixel neighborhood)
            - Valid Range: Positive odd numbers (1, 3, 5, 7, 9, 11, 13, 15)
            - Default: 5
            - Effect: Larger values mean more pixels are considered for smoothing
            - Performance Impact: Larger values significantly slow down processing
            - Note: Must be odd number. Values > 15 are very slow

        2. bilateral_color (Color Space Sigma)
            - Valid Range: 10-200
            - Default: 60
            - Effect: Controls how much different colors are smoothed together
            - Lower values (10-50): Preserve more color edges
            - Higher values (100-200): More color smoothing
            - Note: Values above 200 rarely provide better results

        3. bilateral_space (Coordinate Space Sigma)
            - Valid Range: 10-200
            - Default: 60
            - Effect: Controls how much influence distant pixels have
            - Lower values (10-50): More detail preservation
            - Higher values (100-200): More smoothing
            - Note: Values above 200 rarely provide better results

        4. **edge_low** (Canny Edge Detection Lower Threshold)
            - Valid Range: 0-255
            - Default: 40
            - Effect: Controls edge sensitivity
            - Lower values: Detect more edges (more sensitive)
            - Higher values: Detect fewer edges (less sensitive)
            - Note: Should be less than edge_high

        5. edge_high (Canny Edge Detection Upper Threshold)
            - Valid Range: 0-255
            - Default: 140
            - Effect: Controls edge sensitivity
            - Lower values: Detect more edges
            - Higher values: Detect stronger edges only
            - Note: Should be greater than edge_low

        6. color_quant (Color Quantization Factor)
            - Valid Range: 1-64
            - Default: 20
            - Effect: Controls how many distinct colors appear
            - Lower values (1-15): More colors, more detail
            - Higher values (30-64): Fewer colors, more cartoon-like
            - Note: Should be a power of 2 or multiple of 5 for best results

        7. sharpen_amount (Amount of sharpening))
            - Valid Range: 0.1-1.0
            - Default: 0.5

        """
        try:
            if frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)

            # Initial sharpening to enhance details
            kernel_sharp = numpy.array([[-1, -1, -1],
                                        [-1, 9, -1],
                                        [-1, -1, -1]]) * sharpen_amount
            sharpened = cv2.filter2D(frame, -1, kernel_sharp)

            # Bilateral filter with reduced parameters since we're sharpening
            smoothed = cv2.bilateralFilter(sharpened, bilateral_d, bilateral_color, bilateral_space)

            # Edge detection on the sharpened image
            gray = cv2.cvtColor(smoothed, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, edge_low, edge_high)

            # Thicken edges slightly less since they're already enhanced
            kernel = numpy.ones((2, 2), numpy.uint8)
            edges = cv2.dilate(edges, kernel, iterations=1)
            edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

            # More subtle color quantization
            smoothed = smoothed // color_quant * color_quant

            # Combine
            result = cv2.subtract(smoothed, edges)

            return cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print(f"Error in comic-sharp effect: {str(e)}")
            return frame


    # Part of comic_effect2
    def process_frames(self, frame):
        if self.comic_effect_enabled:
            # Process every 2nd frame
            if self.frame_counter % 2 == 0:
                self.last_comic_frame = PlayVideo.comic_effect2(frame)
            self.frame_counter += 1
            return self.last_comic_frame
        return frame

    @staticmethod
    def apply_denoising(image):
        """Apply denoising to the image using fastNlMeansDenoisingColored."""
        return cv2.fastNlMeansDenoisingColored(image)

    @staticmethod
    def apply_contrast_enhancement(image):
        """Enhance image contrast using CLAHE in LAB color space."""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)

        # Merge channels and convert back to BGR
        enhanced = cv2.merge((cl, a, b))
        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    @staticmethod
    def apply_sharpening(image):
        """Apply sharpening filter to the image."""
        kernel = np.array([[-1, -1, -1],
                           [-1, 9, -1],
                           [-1, -1, -1]])
        return cv2.filter2D(image, -1, kernel)

    @staticmethod
    def enhancement_effects(image):
        """Apply all enhancement effects to the image."""
        denoised = apply_denoising(image)
        enhanced = apply_contrast_enhancement(image)
        sharpened = apply_sharpening(image)
        return denoised, enhanced, sharpened

    @staticmethod
    def apply_edges_sobel(image):
        """Apply Sobel edge detection to the image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
        sobel = np.uint8(np.absolute(sobel))
        # Convert back to 3-channel format to match the expected buffer size
        sobel = cv2.cvtColor(sobel, cv2.COLOR_GRAY2BGR)
        return sobel

    @staticmethod
    def apply_inverted(image):
        """Invert the image."""
        return cv2.bitwise_not(image)

    @staticmethod
    def artistic_filters(image):
        # Edge detection with different methods
        edges_canny = cv2.Canny(image, 100, 200)
        edges_sobel = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=5)

        # Emboss effect
        kernel = np.array([[-2, -1, 0],
                           [-1, 1, 1],
                           [0, 1, 2]])
        emboss = cv2.filter2D(image, -1, kernel) + 128

        # Invert colors
        inverted = cv2.bitwise_not(image)

        return edges_canny, edges_sobel, emboss, inverted

    @staticmethod
    def comic_effect2(frame):
        """
        Apply a comic-style effect to a video frame
        """
        try:
            # Ensure the frame is in BGR format (OpenCV default)
            if frame.shape[2] == 4:  # If RGBA
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)

            # Edge detection on grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.blur(gray, (3, 3))
            edges = cv2.Canny(edges, 50, 150, apertureSize=3)

            # Thicken edges
            kernel = numpy.ones((3, 3), dtype=numpy.float32) / 12.0
            edges = cv2.filter2D(edges, -1, kernel)
            edges = cv2.threshold(edges, 50, 255, cv2.THRESH_BINARY)[1]

            # Convert edges back to BGR
            edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

            # Color smoothing while preserving edges
            shifted = cv2.pyrMeanShiftFiltering(frame, 5, 20)

            # Combine the smoothed image with edges
            result = cv2.subtract(shifted, edges)

            # Convert back to RGB for PyGame
            result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

            return result
        except Exception as e:
            print(f"Error in comic effect: {str(e)}")
            return frame

    @staticmethod
    def adjust_brightness_contrast(frame, brightness, contrast):
        """
        Adjust brightness and contrast of a video frame
        :param frame: Input frame
        :param brightness: Brightness adjustment (-100 to 100)
        :param contrast: Contrast adjustment (-127 to 127)
        :return: Adjusted frame
        """
        #print(f"brightness: {brightness}, contrast: {contrast}")
        # Bounds checking with warnings
        if not (-100 <= brightness <= 100):
            print(f"Warning: Brightness value {brightness} out of range (-100 to 100). Clamping to valid range.")
            brightness = max(-100, min(100, brightness))

        if not (-127 <= contrast <= 127):
            print(f"Warning: Contrast value {contrast} out of range (-127 to 127). Clamping to valid range.")
            contrast = max(-127, min(127, contrast))

        if brightness <= -100:
            return np.zeros_like(frame)  # Completely black
        elif brightness >= 100:
            return np.ones_like(frame) * 255  # Completely white
        else:
            frame = frame.astype(np.float32)
            frame += (brightness * 2.55)  # Scale -100:100 to -255:255

            # Apply contrast if specified
            if contrast != 0:
                # Scale -127:127 to a reasonable factor range
                # At -127: factor ≈ 0.2
                # At 0: factor = 1.0
                # At 127: factor ≈ 2.0
                contrast_factor = max(0.2, min(2.0, 1.0 + (contrast / 127.0)))
                frame = (frame - 128) * contrast_factor + 128

            return np.clip(frame, 0, 255).astype(np.uint8)

    @staticmethod
    def sharpen(image, strength=1.0):
        # Create the sharpening kernel
        kernel = np.array([
            [0, -1, 0],
            [-1, 4 + strength, -1],
            [0, -1, 0]
        ]) / (strength + 1)  # Normalize to preserve brightness

        # Apply the filter
        sharpened = cv2.filter2D(image, -1, kernel)
        return sharpened

    '''
    @staticmethod
    def adjust_brightness_contrast(frame, brightness=0, contrast=0):
        """
        Adjust brightness and contrast of an image
        :param frame: Input frame
        :param brightness: Brightness adjustment (-100 to 100)
        :param contrast: Contrast adjustment (-100 to 100)
        """
        brightness = float(brightness) / 100  # Convert to -1 to 1
        contrast = float(contrast) / 100  # Convert to -1 to 1

        # Apply brightness
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow) / 255
            gamma_b = shadow

            frame = cv2.addWeighted(frame, alpha_b, frame, 0, gamma_b)

        # Apply contrast
        if contrast != 0:
            f = 131 * (contrast + 127) / (127 * (131 - contrast))
            alpha_c = f
            gamma_c = 127 * (1 - f)

            frame = cv2.addWeighted(frame, alpha_c, frame, 0, gamma_c)

        # Ensure output is valid
        return np.clip(frame, 0, 255).astype(np.uint8)
        '''

    def update_video_effects(self):
        """Call this when you need to update the video effects"""
        if hasattr(self, 'vid') and self.vid:
            # Rebuild video with new effects chain
            effects_processor = self.build_effects_chain(self.opts)
            self.vid.post_process = effects_processor

    def build_effects_chain(self, opts):
        effects = []
        # Add effects based on command line arguments
        if opts.sharpen:
            effects.append(PostProcessing.sharpen)
            #effects.append(PlayVideo.sharpen)
        if opts.greyscale:
            effects.append(PostProcessing.greyscale)
        if opts.blur:
            effects.append(PostProcessing.blur)
        if opts.cel_shading:
            effects.append(PostProcessing.cel_shading)
        if opts.noise:
            effects.append(PostProcessing.noise)
        if opts.fliplr:
            effects.append(PostProcessing.fliplr)
        if opts.flipup:
            effects.append(PostProcessing.flipup)
        if opts.sepia:
            effects.append(PlayVideo.sepia)
        if opts.edge_detect:
            effects.append(PlayVideo.edge_detect)
        if opts.vignette:
            effects.append(PlayVideo.vignette)
        if opts.saturation:
            # You might want to make the factor configurable
            effects.append(lambda frame: PlayVideo.adjust_saturation(frame, factor=1.5))
        if opts.gaussian_blur:
            effects.append(PlayVideo.gaussian_blur)
        if opts.median_blur:
            effects.append(PlayVideo.median_blur)
        if opts.comic:
            self.comic_effect_enabled = True
            effects.append(self.process_frames)
        else:
            self.comic_effect_enabled = False
        if opts.comic_sharp:
            effects.append(PlayVideo.comic_sharp_effect)
        if opts.thermal:
            effects.append(lambda frame: cv2.applyColorMap(frame, cv2.COLORMAP_JET))
        if opts.emboss:
            def emboss(frame):
                kernel = np.array([[-2, -1, 0],
                                   [-1, 1, 1],
                                   [0, 1, 2]])
                return cv2.filter2D(frame, -1, kernel) + 128
            effects.append(emboss)
        if opts.dream:
            def dream_effect(frame):
                blur = cv2.GaussianBlur(frame, (0, 0), 2.0)
                return cv2.addWeighted(frame, 1.5, blur, -0.5, 0)
            effects.append(dream_effect)
        if opts.pixelate:
            def pixelate(frame, block_size=20):
                h, w = frame.shape[:2]
                temp = cv2.resize(frame, (w // block_size, h // block_size))
                return cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)
            effects.append(pixelate)
        if opts.neon:
            def neon_effect(frame):
                edges = cv2.Canny(frame, 100, 200)
                edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                blur = cv2.GaussianBlur(edges, (0, 0), 3)
                return cv2.addWeighted(frame, 0.8, blur, 0.2, 0)
            effects.append(neon_effect)
        if opts.pencil_sketch:
            def pencil_effect(frame):
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                inverted = 255 - gray

                # Use sketch-detail for Gaussian blur
                kernel_size = opts.sketch_detail if hasattr(opts, 'sketch_detail') else 21
                blurred = cv2.GaussianBlur(inverted, (kernel_size, kernel_size), 0)

                # Create regular sketch
                sketch = cv2.divide(gray, 255 - blurred, scale=256.0)

                # Create edges using adaptive thresholding with configurable parameters
                block_size = opts.sketch_block_size if hasattr(opts, 'sketch_block_size') else 9
                c_value = opts.sketch_c_value if hasattr(opts, 'sketch_c_value') else 2
                edges = cv2.adaptiveThreshold(gray, 255,
                                              cv2.ADAPTIVE_THRESH_MEAN_C,
                                              cv2.THRESH_BINARY,
                                              blockSize=block_size,
                                              C=c_value)

                # Combine sketch with edges using configurable weights
                edges = 255 - edges  # Invert edges
                sketch_intensity = opts.sketch_intensity if hasattr(opts, 'sketch_intensity') else 0.7
                edge_weight = opts.edge_weight if hasattr(opts, 'edge_weight') else 0.3

                # Convert both to float32 for consistent types
                sketch = sketch.astype(np.float32)
                edges = edges.astype(np.float32) / 255.0

                sketch = cv2.multiply(sketch, sketch_intensity)
                combined = cv2.addWeighted(sketch, sketch_intensity, edges, edge_weight, 0)

                # Convert back to uint8 for display
                combined = np.clip(combined, 0, 255).astype(np.uint8)
                return cv2.cvtColor(combined, cv2.COLOR_GRAY2BGR)
            effects.append(pencil_effect)
        if opts.oil_painting:
            def oil_painting_effect(frame):
                # Parameters: size of neighborhood and dynamic ratio
                # size: larger = more abstract (try 5-15)
                # dyna: smaller = more abstract (try 1-5)
                return cv2.xphoto.oilPainting(frame, size=7, dynRatio=1)
            effects.append(oil_painting_effect)
        if opts.watercolor:
            from concurrent.futures import ThreadPoolExecutor
            executor = ThreadPoolExecutor(max_workers=2)

            def process_channel(channel, d, sigma):
                return cv2.bilateralFilter(channel, d, sigma, sigma)

            def watercolor_effect(frame):
                scale = opts.watercolor_scale if hasattr(opts, 'watercolor_scale') else 0.5
                small = cv2.resize(frame, None, fx=scale, fy=scale)

                # Process color channels in parallel
                b, g, r = cv2.split(small)
                with ThreadPoolExecutor(max_workers=3) as executor:
                    b_filtered = executor.submit(process_channel, b, 7, 75)
                    g_filtered = executor.submit(process_channel, g, 7, 75)
                    r_filtered = executor.submit(process_channel, r, 7, 75)

                    filtered = cv2.merge([
                        b_filtered.result(),
                        g_filtered.result(),
                        r_filtered.result()
                    ])

                median = cv2.medianBlur(filtered, 5)

                edges = cv2.Laplacian(cv2.cvtColor(median, cv2.COLOR_BGR2GRAY), cv2.CV_8U, ksize=3)
                edges = cv2.threshold(edges, 30, 255, cv2.THRESH_BINARY_INV)[1]
                edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

                result = cv2.addWeighted(median, 0.7, edges, 0.3, 0)
                return cv2.resize(result, (frame.shape[1], frame.shape[0]))

            effects.append(watercolor_effect)
        if opts.adjust_video:
            def adjust_effect(frame):
                brightness = opts.brightness if hasattr(opts, 'brightness') else 0
                contrast = opts.contrast if hasattr(opts, 'contrast') else 0
                # Pass the original contrast and brightness values
                return PlayVideo.adjust_brightness_contrast(frame, brightness, contrast)
            effects.append(adjust_effect)
        if opts.apply_contrast_enhancement:
            effects.append(PlayVideo.apply_contrast_enhancement)
        if opts.apply_sharpening:
            effects.append(PlayVideo.apply_sharpening)
        if opts.apply_edges_sobel:
            effects.append(PlayVideo.apply_edges_sobel)
        if opts.apply_inverted:
            effects.append(PlayVideo.apply_inverted)
        # Add bilateral filter to the effects chain
        if hasattr(opts, 'apply_bilateral_filter') and opts.apply_bilateral_filter:
            effects.append(lambda frame: self.apply_bilateral_filter_effect(frame))

        # ... add other effects as needed
        # If no effects are specified, return None or PostProcessing.none
        if not effects:
            return PostProcessing.none
        # If only one effect, return it directly
        if len(effects) == 1:
            return effects[0]
        # For multiple effects, create a chain
        def process_frame(frame):
            for effect in effects:
                frame = effect(frame)
            return frame
        return process_frame

    def FrameCapture(self, count):
        frameCount = count
        path = self.frameSaveDir
        #path = f"/home/nikki/FrameData/{self.vid.name}/"
        file = path + "/frame-%04d.jpg" % frameCount
        # Saves the frames with frame-count
        print(f"Saving: {file}")
        self.save_frame_surf(file)
        frameCount += 1
        return frameCount

    def apply_bilateral_filter_effect(self, frame):
        """Apply bilateral filter effect using the dedicated panel"""
        if frame is None:
            return frame

        # Check if bilateral filter should be applied
        if not self.opts.apply_bilateral_filter or not self.bilateral_filter_enabled:
            return frame

        return self.bilateral_panel.apply_bilateral_filter(frame)

    '''
    def apply_bilateral_filter_effect(self, frame):
        """Apply bilateral filter effect - integrates with your effects pipeline"""
        if hasattr(self, 'bilateral_panel'):
            return self.bilateral_panel.apply_bilateral_filter(frame)
        return frame
    '''

    def process_frame(self, frame):
        """Process video frame with bilateral filter if enabled"""
        if self.bilateral_filter_enabled and frame is not None:
            # Apply CUDA-accelerated bilateral filter
            frame = self.bilateral_panel.apply_bilateral_filter(frame)

        return frame

    def update_video_frame(self):
        """Your existing frame update method - modify this"""
        # ... your existing frame reading code ...

        # Get the current frame (however you're doing this)
        frame = self.vid.frame_surf  # Replace with your actual method

        if frame is not None:
            # Process the frame with filters
            frame = self.process_frame(frame)

            # Convert and display (your existing code)
            # ... your existing frame conversion and display code ...

        return frame

    def playVideo(self, video):
        """
        Plays a video file using the specified options and settings.

        The method initializes the video playback using the provided video path, sets up
        parameters such as audio, resolution, and playback speed, and returns the video
        object. If an error occurs during setup, it handles the exception and returns None.

        Parameters
        ----------
        video: str
            The path to the video file that will be played.

        Returns
        -------
        VideoPygame or None
            Returns a VideoPygame object initialized with the video file and settings, or
            None if an error occurs during the setup.

        Raises
        ------
        ValueError
            If the video path is invalid or empty
        ResolutionChangeError
            If changing video resolution fails
        """

        effects_processor = self.build_effects_chain(self.opts)

        # First, define a custom exception for resolution changes
        class ResolutionChangeError(Exception):
            pass

        # Reset progress tracking attributes
        self.progress_active = False
        self.progress_value = 0
        self.progress_percentage = 0

        # Input validation
        if not video or not isinstance(video, str):
            print("Error: Invalid video path")
            return None

        if not os.path.exists(video):
            print(f"Error: Video file not found at path: {video}")
            return None

        try:
            # Initialize video object
            self.vid: VideoPygame = Video(video,
                                          post_process=effects_processor,
                                          use_pygame_audio=self.opts.usePygameAudio,
                                          interp=self.opts.interp,
                                          audio_track=self.opts.aTrack,
                                          speed=self.opts.playSpeed,
                                          #no_audio=self.opts.noAudio,
                                          subs=None,
                                          reader=self.opts.reader_val_int
                                          )

            # FFprobe handling
            if self.opts.enableFFprobe:
                try:
                    self.vid.probe()
                except Exception as probe_error:
                    print(f"Warning: FFprobe failed: {probe_error}")

            # Resolution change with detailed error handling
            try:
                original_resolution = None
                if hasattr(self.vid, 'get_resolution'):  # Assuming such a method exists
                    original_resolution = self.vid.get_resolution()

                self.vid.change_resolution(self.displayHeight)

                # Verify resolution change was successful (assuming get_resolution method exists)
                if hasattr(self.vid, 'get_resolution'):
                    new_resolution = self.vid.get_resolution()
                    if new_resolution == original_resolution:
                        raise ResolutionChangeError(
                            f"Resolution change failed: Resolution remained at {original_resolution}"
                        )

            except ResolutionChangeError as res_error:
                print(f"CRITICAL ERROR - Resolution Change Failed: {res_error}")
                print(f"Original resolution: {original_resolution}")
                print(f"Attempted display height: {self.displayHeight}")
                print("This error must be fixed for proper presentation playback.")
                # Clean up
                if hasattr(self, 'vid') and self.vid is not None:
                    try:
                        self.vid.close()
                    except:
                        pass
                raise  # Re-raise the exception to halt execution

            except Exception as e:
                print(f"CRITICAL ERROR - Unexpected resolution change error:")
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                print(f"Attempted display height: {self.displayHeight}")
                if original_resolution:
                    print(f"Original resolution: {original_resolution}")
                print("Stack trace:")
                import traceback
                traceback.print_exc()
                # Clean up
                if hasattr(self, 'vid') and self.vid is not None:
                    try:
                        self.vid.close()
                    except:
                        pass
                return None

            # Set duration if the resolution change was successful
            if self.opts.enableFFprobe:
                self.opts.actualDuration = int(self.vid.duration / self.opts.playSpeed)

             # Set volume
            self.vid.set_volume(self.volume)
            return self.vid

        except Exception as e:
            print(f"Critical error during video initialization: {str(e)}")
            # Cleanup
            if hasattr(self, 'vid') and self.vid is not None:
                try:
                    self.vid.close()
                except:
                    pass
            return None

    '''
    def playVideo(self, video):
        """
        Plays a video file using the specified options and settings.

        The method initializes the video playback using the provided video path, sets up
        parameters such as audio, resolution, and playback speed, and returns the video
        object. If an error occurs during setup, it handles the exception and returns None.

        Attributes
        ----------
        progress_active: bool
            Tracks whether the video progress is active.
        progress_value: int
            Current value of the progress indicator.
        progress_percentage: int
            Percentage of the video progress.

        Parameters
        ----------
        video: str
            The path to the video file that will be played.

        Returns
        -------
        VideoPygame or None
            Returns a VideoPygame object initialized with the video file and settings, or
            None if an error occurs during the setup.
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
                                          subs=None,
                                          reader=self.opts.reader_val_int
                                          )

            """
            Uses FFprobe to find information about the video.  When using cv2 to read videos,
            information such as frame count or frame rate are read through the file headers,
            which is sometimes incorrect. For more accuracy, call this method to start a probe
            and update the video information.
            """
            if self.opts.enableFFprobe:
                self.vid.probe()

            self.vid.change_resolution(self.displayHeight)
            # Global variable needed to show the actual duration of the video in seconds.
            self.opts.actualDuration = int(self.vid.duration / self.opts.playSpeed)
        except Exception as e:
            print(f"An Error occurred: {e}")
            return None
        self.vid.set_volume(self.volume)
        return self.vid
    '''

    def play(self, eventHandler):
        """
        Plays a sequence of videos in a custom player with specific playback controls and options.

        The `play` method executes the main loop for the video playback, iterating through a list of videos.
        It handles both forward and backward playback navigation, looping options, splash screens, GIF
        animations, real-time event handling, on-screen display (OSD), and audio muting. The method ensures
        that each video is played according to user-specified settings and updates the graphical interface
        accordingly. It also manages resources for video playback, such as closing video objects after
        completion and accommodating video-specific metadata like titles. The process continues until the
        end of the video list, or based on looping and stop-button conditions.

        Parameters:
        eventHandler : EventHandler
            Object responsible for managing events such as keyboard inputs or user interactions during
            video playback.
        """

        while True:
            self.currVidIndx = -1
            while self.currVidIndx < len(self.videoList):
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

                # .gif animation requires that we do not display the video splash.
                if self.videoList[self.currVidIndx].lower().endswith(".gif"):
                    self.disableSplash = True
                else:
                    self.disableSplash = False

                self.reset_OSD_tracking()
                self.reset_video_info_splash()

                '''Play the video'''
                self.vid = self.playVideo(self.videoList[self.currVidIndx])
                if self.vid is None:
                    continue

                if self.opts.dispTitles is not None:
                    self.video_title = self.get_video_title(self.videoList[self.currVidIndx])
                    #print(self.video_title)

                print(f"Playing {self.currVidIndx+1} of {len(self.videoList  )}: {self.vid.name}{self.vid.ext}")
                # Setup video splash.
                if not self.disableSplash:
                    self.draw_video_splash()

                '''
                self.frameSaveDir = self.check_SSHOT_dir(noImgType=True)
                self.frameCount = 0
                self.counter = 0
                '''

                 # The event handler loop
                while self.vid.active:
                    eventHandler.handle_events()

                    if self.opts.enableOSDcurpos:
                        self.opts.enableOSDcurpos = False
                        self.OSD_curPos_flag = not self.OSD_curPos_flag
                        self.draw_OSD_active = (not self.draw_OSD_active if not self.OSD_curPos_flag else True)

                    if self.vid.no_audio:
                        self.mute_flag = True
                        self.key_mute_flag = True

                    if self.mute_flag or self.key_mute_flag or self.vid.no_audio:
                        self.vid.mute()

                    pos_w, pos_h = self.getResolutions()
                    if self.vid.draw(self.win, (pos_w, pos_h),
                            force_draw=(False if not self.vid.paused else True)) or self.vid.paused:


                        self.render_frame()
                        self.draw(self.win)


                        '''
                        self.frameCount = self.counter
                        self.counter = self.FrameCapture(self.frameCount)
                        '''

                        self.handle_queued_screenshot()
                        self.update_GUI_components()
                        pygame.display.update()

                    pygame.time.wait(int(1000 / (self.vid.frame_rate * self.vid.speed)))
                # End of while vid.active
                # Close the object to free up resources.
                self.vid.close()
                if self.forwardsFlag is not True and self.backwardsFlag is not True:
                    # The length of time delay between each video
                    pass
            # End of videoList playback loop
            if self.stopButtonClicked:
                continue
            elif not self.opts.loop:
                break
        # End of the main loop
        self.quit()
