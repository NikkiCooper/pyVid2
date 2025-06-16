#   EventHandler.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Pygame event handler class
import os
import pygame
import time

from psutil import net_connections

import constants as const

# Mouse constants used in the pygame event loop.
LEFT = 0
MIDDLE = 1
RIGHT = 2

LEFT_BUTTON_LONG =  1
RIGHT_BUTTON_LONG = 3

LEFT_BUTTON_SHORT = 1
MIDDLE_BUTTON_SHORT = 2
RIGHT_BUTTON_SHORT = 3

WHEEL_UP = 1
WHEEL_DOWN = -1


class EventHandler:
    """
    Handles the setup and management of pygame events for video playback functionality.

    The EventHandler class is responsible for handling various pygame events such as mouse
    motion, clicks, button presses, key presses, and custom-defined user events.
    It interacts with the PlayVideoInstance class to provide functionalities like pausing,
    navigation through videos, adjusting video speed and volume, or toggling visibility of
    help and status bar features during video playback. The class also facilitates handling
    short and long mouse clicks, mouse wheel scrolling, and video seek features.
    Custom events for fast-forward and rewind are implemented using pygame timers.

    Attributes:
        running (bool): Controls whether the video loop continues running or stops.
        PlayVideoInstance: The instance of the PlayVideo class that manages video playback.
        REWIND_SEEK_EVENT: Custom pygame user event for rewind functionality.
        FWD_SEEK_EVENT: Custom pygame user event for fast-forward functionality.
        FwdSeekCounter (int): Counter for fast-forward seek events.
        RewindSeekCounter (int): Counter for rewind seek events.
        elapsed_time (float): Duration of the mouse button press.
        previous_speed (int): Stores the previously set playback speed.
        mouse_press_times (dict): Dictionary to track mouse button press timestamps.
        short_click_threshold (float): Threshold in seconds to differentiate short and long clicks.
        long_click_threshold (float): Threshold in seconds for a long click.
        threshold_ratio (float): Ratio used to determine the threshold for status bar visibility.
        threshold (int): Height threshold, calculated using displayHeight and threshold_ratio.
        current_video (int): Index of the currently playing video.
    """
    def __init__(self, PlayVideoInstance):
        """
        Handles initialization and configuration of a video playback controller, which manages playback
        operations such as rewinding, forwarding, and click interpretation. This class sets up custom pygame
        events, defines thresholds for detecting user input, and initializes other playback-related variables.

        Attributes:
            running (bool): Indicates whether the video loop is active or not.
            PlayVideoInstance: Instance of an external `PlayVideo` class managing video playback.
            REWIND_SEEK_EVENT: Custom pygame user event for rewinding video playback.
            FWD_SEEK_EVENT: Custom pygame user event for forwarding video playback.
            FwdSeekCounter (int): Counter to track the number of forward seek operations.
            RewindSeekCounter (int): Counter to track the number of rewind seek operations.
            elapsed_time: Tracks elapsed time during video playback.
            previous_speed (int): Stores the previous speed of video playback.
            mouse_press_times (dict): Dictionary to track the timestamps of mouse press events.
            short_click_threshold (float): Time threshold in seconds for detecting short clicks.
            long_click_threshold (float): Time threshold in seconds for detecting long clicks.
            threshold_ratio (float): Ratio of screen height used to calculate threshold for gesture detection.
            threshold (int): Absolute threshold value derived from the display height and threshold ratio.
            current_video (int): Index of the currently loaded video in a playlist or collection.

        Parameters:
            PlayVideoInstance: Instance of an external `PlayVideo` class that needs to be controlled.
        """
        self.running = True                                     # Control whether the video loop runs
        self.PlayVideoInstance = PlayVideoInstance              # Create a PlayVideo Instance.
        self.REWIND_SEEK_EVENT = pygame.USEREVENT + 10          # User defined pygame timer event
        self.FWD_SEEK_EVENT = pygame.USEREVENT + 15
        pygame.time.set_timer(self.FWD_SEEK_EVENT, 20)
        pygame.time.set_timer(self.FWD_SEEK_EVENT, 0)
        pygame.time.set_timer(self.REWIND_SEEK_EVENT, 20)
        pygame.time.set_timer(self.REWIND_SEEK_EVENT, 0)
        self.FwdSeekCounter = 0
        self.RewindSeekCounter = 0
        self.elapsed_time = None
        self.previous_speed = 0
        self.mouse_press_times = {}
        self.short_click_threshold = 0.250
        self.long_click_threshold = 0.750
        #
        # Adjust as needed.  0.15 means 15% of the screen height
        # self.threshold_ratio = 0.15
        self.threshold_ratio = 0.052
        self.threshold = int(self.PlayVideoInstance.displayHeight * self.threshold_ratio)
        self.current_video = -1

        # initialization code for the cb control panel sliders
        self.slider_dragging = None  # Track which slider is being dragged
        self.slider_start_pos = None  # Track the starting position for drag operations

        # initialization code for the various single argument post-processing functions.
        self.pp_args = None

    @property
    def opts(self):
        return self.PlayVideoInstance.opts

    def handle_events(self):
        """
        Processes and handles various pygame events, determining appropriate application behavior and
        responses to user input.

        This method continuously loops through pygame-generated events, interpreting them based on their
        type and delegating specific actions to corresponding methods or operations. It manages tasks
        such as quitting the application, handling mouse movements, button inputs, key presses, and custom
        events like forward and rewind seek functionalities.

        Returns
        -------
        None
        """
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                    self.PlayVideoInstance.quit_video()
                case pygame.MOUSEMOTION:
                    if self.PlayVideoInstance.control_panel.handle_mouse_motion(event.pos):
                        continue
                    elif self.PlayVideoInstance.edge_panel.handle_mouse_motion(event.pos):
                        continue
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.handle_mouse_motion(mouse_x, mouse_y)
                case pygame.MOUSEBUTTONDOWN:
                    if self.PlayVideoInstance.control_panel.handle_mouse_button_down(event.pos):
                        continue
                    elif self.PlayVideoInstance.edge_panel.handle_mouse_button_down(event.pos):
                        continue
                    self.mouse_press_times[event.button] = pygame.time.get_ticks()
                case pygame.MOUSEBUTTONUP:
                    self.PlayVideoInstance.control_panel.handle_mouse_button_up()
                    self.PlayVideoInstance.edge_panel.handle_mouse_button_up()
                    self.handle_mouse_button_up(event)
                case pygame.KEYDOWN:
                    self.handle_keydown(event)
                case pygame.MOUSEWHEEL:
                    self.PlayVideoInstance.progress_timeout = 50
                    if event.x == 0 and event.y != 0:
                        # Handle_mouse_wheel determines whether the pygame.MOUSEWHEEL event is
                        # a mousewheel up or mousewheel down.  It will automatically adjust the
                        # seek time to negative on a mousewheel down event.
                        self.handle_mouse_wheel(4, event)
                case self.FWD_SEEK_EVENT:
                    self.handle_fwd_seek_event()
                case self.REWIND_SEEK_EVENT:
                    self.handle_rewind_seek_event()

    def handle_mouse_button_up(self, event):
        """
        Handles the actions triggered by releasing a mouse button, performing specific actions based on the button pressed
        and the duration of the press.

        The behavior includes determining whether the button press qualifies as a short or long click and executing
        corresponding actions such as navigating through videos, toggling video playback, displaying help information,
        updating volumes, speed, or interacting with on-screen elements like video play bars and icons.

        Attributes:
            mouse_press_times (dict): A dictionary mapping mouse buttons to their respective press timestamps.
            elapsed_time (float): The calculated time in seconds for which the button was held down.
            long_click_threshold (float): The time threshold to classify a button press as a long click.
            short_click_threshold (float): The time threshold to classify a button press as a short click.
            PlayVideoInstance: Instance of a class managing video playback functions such as pausing, resuming, navigating,
                and displaying help or metadata windows.

        Parameters:
            event: pygame.event.Event
                The mouse event object containing data about the mouse button action and position.

        Raises:
            KeyError: In case the mouse button event action is missing in the `mouse_press_times` dictionary.
        """
        if event.button in self.mouse_press_times:
            if event.button in self.mouse_press_times:
                # Don't process long clicks if we're interacting with the control panel
                if self.PlayVideoInstance.cb_panel_is_visible:
                    mouse_pos = pygame.mouse.get_pos()
                    panel_rect = self.PlayVideoInstance.control_panel_rect
                    if panel_rect.collidepoint(mouse_pos):
                        self.mouse_press_times.pop(event.button, None)
                        return

            self.elapsed_time = (pygame.time.get_ticks() - self.mouse_press_times[event.button]) / 1000.0
            if self.elapsed_time >= self.long_click_threshold:
                if event.button == LEFT_BUTTON_LONG:
                    # Disable Long click if the Help or the Video metadata windows are displayed
                    if not (self.PlayVideoInstance.video_info_box or self.PlayVideoInstance.help_visible):
                        self.PlayVideoInstance.next_video()
                elif event.button == RIGHT_BUTTON_LONG:
                    if not (self.PlayVideoInstance.video_info_box or self.PlayVideoInstance.help_visible):
                        self.PlayVideoInstance.previous_video()
            else:
                if self.elapsed_time <= self.short_click_threshold:
                    if event.button == MIDDLE_BUTTON_SHORT:
                        self.PlayVideoInstance.vid.toggle_pause()
                        if self.PlayVideoInstance.vid.paused:
                            self.PlayVideoInstance.pause = True
                        else:
                            self.PlayVideoInstance.pause = False
                    elif event.button in (LEFT_BUTTON_SHORT, RIGHT_BUTTON_SHORT):
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        mouse_pos = (mouse_x, mouse_y)
                        # Help
                        if self.PlayVideoInstance.help_button_rect is not None:
                            if self.PlayVideoInstance.help_button_rect.collidepoint(mouse_pos):
                                self.PlayVideoInstance.help_visible = False
                        # volume
                        self.update_volume(mouse_x, mouse_y)
                        self.update_video_speed(mouse_x, mouse_y)
                        #
                        self.PlayVideoInstance.videoPlayBar.MOUSE_X = mouse_x
                        self.PlayVideoInstance.videoPlayBar.MOUSE_Y = mouse_y
                        self.update_videoPlayBarVolume(event, mouse_x, mouse_y)
                        self.videoPlayBarIconPress(event, mouse_x, mouse_y)
                        if self.PlayVideoInstance.video_info_box:
                            # self.update_video_info(mouse_x, mouse_y)
                            if self.PlayVideoInstance.drawVidInfo.button_rect.collidepoint(
                                    event.pos):  # process the OK button
                                self.PlayVideoInstance.video_info_box = False
                                # self.PlayVideoInstance.vid.play()
                    if self.mouse_press_times.get(LEFT_BUTTON_SHORT) and self.mouse_press_times.get(RIGHT_BUTTON_SHORT):
                        self.PlayVideoInstance.quit_video()
            self.mouse_press_times.pop(event.button, None)

    def handle_mouse_motion(self, mouse_x, mouse_y):
        """
        Handles mouse motion events and updates UI components such as help dialogs, video info boxes,
        and the visibility state of the video play bar based on the mouse position within the application.

        Parameters:
            mouse_x (int): The current x-coordinate of the mouse cursor.
            mouse_y (int): The current y-coordinate of the mouse cursor.

        Raises:
            None

        Returns:
            None
        """
        # Help dialog

        if self.PlayVideoInstance.help_visible:
            mouse_pos = (mouse_x, mouse_y)
            if hasattr(self.PlayVideoInstance, 'help_button_rect') and self.PlayVideoInstance.help_button_rect is not None:
                self.PlayVideoInstance.is_hovered = self.PlayVideoInstance.help_button_rect.collidepoint(mouse_pos)
            else:
                self.PlayVideoInstance.is_hovered = False  # default value

        if self.PlayVideoInstance.video_info_box:
            # render the tooltip
            self.update_video_info(mouse_x, mouse_y)
        # Throttle new status bar visibility
        if mouse_y >= (self.PlayVideoInstance.displayHeight - self.threshold):
            self.PlayVideoInstance.drawVideoPlayBarFlag = True
            self.PlayVideoInstance.status_bar_visible = self.PlayVideoInstance.drawVideoPlayBarFlag
            if self.PlayVideoInstance.status_bar_visible:
                self.PlayVideoInstance.videoPlayBar.MOUSE_X = mouse_x
                self.PlayVideoInstance.videoPlayBar.MOUSE_Y = mouse_y
                self.PlayVideoInstance.videoPlayBar.drawVideoPlayBar()
                # self.videoPlayBarIconHover(event, mouse_x, mouse_y)
        else:
            self.PlayVideoInstance.drawVideoPlayBarFlag = False
            self.PlayVideoInstance.status_bar_visible = self.PlayVideoInstance.drawVideoPlayBarFlag
            if self.PlayVideoInstance.drawVideoPlayBarToolTip:
                self.PlayVideoInstance.drawVideoPlayBarToolTip = False

    def handle_slider_events(self, event, mouse_pos):
        """
        Handles events specific to the brightness/contrast sliders
        """
        if not self.PlayVideoInstance.cb_panel_is_visible:
            return False

        # Adjust mouse position relative to control panel
        relative_pos = (
            mouse_pos[0] - self.PlayVideoInstance.control_panel_rect.x,
            mouse_pos[1] - self.PlayVideoInstance.control_panel_rect.y
        )

        # Check for clicks on the brightness slider
        if self.PlayVideoInstance.brightness_slider['knob'].collidepoint(*relative_pos):
            self.slider_dragging = 'brightness'
            self.slider_start_pos = mouse_pos[0]
            return True

        # Check for clicks on the contrast slider
        elif self.PlayVideoInstance.contrast_slider['knob'].collidepoint(*relative_pos):
            self.slider_dragging = 'contrast'
            self.slider_start_pos = mouse_pos[0]
            return True

        return False

    def handle_mouse_wheel(self, seek, event):
        """
        if event.y > 0, this is a MOUSEWHEEL UP EVENT.
        if event.y < 0, this as a MOUSEWHEEL DOWN EVENT.
        event.y == 0 is not possible here because we filter it out before calling this method.
        """
        seek_fwd  = True if event.y > 0 else False
        seek_time = seek if seek_fwd else -seek
        if self.PlayVideoInstance.vid.active:
            self.PlayVideoInstance.vid.seek(seek_time)
            if seek_fwd:
                pygame.time.set_timer(self.FWD_SEEK_EVENT, 20)
                pygame.time.set_timer(self.REWIND_SEEK_EVENT, 0)
                self.PlayVideoInstance.seekFwd_flag = True
                self.PlayVideoInstance.seekRewind_flag = False
            else:
                pygame.time.set_timer(self.REWIND_SEEK_EVENT, 20)
                pygame.time.set_timer(self.FWD_SEEK_EVENT, 0)
                self.PlayVideoInstance.seekFwd_flag = False
                self.PlayVideoInstance.seekRewind_flag = True

            self.PlayVideoInstance.seek_flag = True
            self.PlayVideoInstance.seek_flag2 = True
            self.PlayVideoInstance.total_duration = self.PlayVideoInstance.vid.duration
            self.PlayVideoInstance.current_pos = self.PlayVideoInstance.vid.get_pos()
            self.PlayVideoInstance.progress_value = (
                self.PlayVideoInstance.current_pos / self.PlayVideoInstance.total_duration) * 100
            self.PlayVideoInstance.progress_percentage = (
                self.PlayVideoInstance.current_pos / self.PlayVideoInstance.total_duration) * 100
            self.PlayVideoInstance.progress_active = True
        else:
            self.PlayVideoInstance.total_duration = 0
            self.PlayVideoInstance.current_pos = 0
            self.PlayVideoInstance.progress_value = 0
            self.PlayVideoInstance.progress_percentage = 0
            self.PlayVideoInstance.progress_active = False

    def handle_keydown(self, event):
        """
        Handles specific key-down events and triggers associated functionalities in the video player.

        This method processes keyboard input events and performs specific actions based on the key pressed.
        Actions include toggling settings such as looping, muting, or displaying metadata, as well as other
        operations such as saving frames, controlling playback, and interacting with on-screen displays (OSD).
        It is designed to enhance user interaction and control over the video playback features.

        Parameters:
        event (pygame.event.Event): The event object containing the key-down event details.

        Raises:
        None

        Returns:
        None
        """
        if self.isKeyCombo(event, *const.KEY_SAVE):
            """
            saveMode temporarly remaps the "spacebar" key to the 'save screenshot' function
            The 's' key still saves a screenshot, however, by temporarily remapping the 'spacebar' key
            to this function, then it just makes it easier to press the spacebar instead of the 's' key.
            ALT+S turns the mode on, ALT+S again turns it off.  Another advantage is the routine is not
            really a screen shot at all.  It is is a pygame surface that is the last rendered frame which
            has been updated to the display device.  This is better, because none of the GUI controls or
            windows in pyVid2 will interfere with the resulting image.
            """
            self.PlayVideoInstance.saveMode = not self.PlayVideoInstance.saveMode
            if self.PlayVideoInstance.saveMode:
                self.PlayVideoInstance.saveModeVisible = True
                self.PlayVideoInstance.message = "Entering into saveMode"
                self.PlayVideoInstance.saveModeDialogBox(self.PlayVideoInstance.message)
                print(f"Entered into saveMode.")
            else:
                self.PlayVideoInstance.saveModeVisible = True
                self.PlayVideoInstance.message = "Leaving saveMode"
                self.PlayVideoInstance.saveModeDialogBox(self.PlayVideoInstance.message)
                print("Leaving saveMode.")
        else:
            match event.key:
                case const.KEY_PRINT_CLI:
                    self.PlayVideoInstance.print_cli_options()
                case const.KEY_CB_PANEL:
                    self.PlayVideoInstance.control_panel.toggle_visibility()
                case const.KEY_EDGE_DETECT:
                    print("Pressed Edge Detect key")
                    self.PlayVideoInstance.edge_panel.toggle_visibility()
                case const.KEY_SHUFFLE:
                    self.PlayVideoInstance.shuffleVideoList()
                    self.PlayVideoInstance.shuffleSplashFlag = True
                case const.KEY_APPLY_CONTRAST_ENH:
                    print("Pressed f key")
                    self.reInitVideo('apply_contrast_enhancement', self.PlayVideoInstance.vid.frame)
                case const.KEY_HELP:
                    if self.PlayVideoInstance.video_info_box:
                        self.PlayVideoInstance.video_info_box = False
                    self.PlayVideoInstance.help_visible = not self.PlayVideoInstance.help_visible
                case const.KEY_META_DATA:
                    # If the help box is visible, turn it off
                    if self.PlayVideoInstance.help_visible:
                        self.PlayVideoInstance.help_visible = False
                    self.PlayVideoInstance.video_info_box = True
                    filename = self.PlayVideoInstance.vid.name + self.PlayVideoInstance.vid.ext
                    path = os.path.dirname(self.PlayVideoInstance.videoList[self.PlayVideoInstance.currVidIndx])
                    filepath = os.path.join(path, "")
                    self.PlayVideoInstance.filePath = filepath
                    self.PlayVideoInstance.DrawVideoInfoBox(filepath, filename)
                case const.KEY_APPLY_EDGES_SOBEL:
                    print("Pressed k key")
                    self.reInitVideo('apply_edges_sobel', self.PlayVideoInstance.vid.frame)
                case const.KEY_GREY_SCALE:
                    print("Pressed greyscale key")
                    self.reInitVideo('greyscale', self.PlayVideoInstance.vid.frame)
                case const.KEY_LOOP:
                    self.PlayVideoInstance.opts.loop_flag = not self.PlayVideoInstance.opts.loop_flag
                case const.KEY_MUTE:
                    if self.PlayVideoInstance.mute_flag:
                        self.PlayVideoInstance.vid.toggle_mute()
                        self.PlayVideoInstance.mute_flag = False
                        self.PlayVideoInstance.key_mute_flag = True \
                            if self.PlayVideoInstance.vid.muted is True else False
                    else:
                        self.PlayVideoInstance.key_mute_flag = not self.PlayVideoInstance.key_mute_flag
                        self.PlayVideoInstance.vid.mute() \
                            if self.PlayVideoInstance.key_mute_flag is True else self.PlayVideoInstance.vid.unmute()
                case const.KEY_NEXT_VID:
                    self.PlayVideoInstance.forwardsFlag = True
                    # Disable video loop for current video before advancing to the next one.
                    if self.PlayVideoInstance.opts.loop_flag:
                        self.PlayVideoInstance.opts.loop_flag = False
                    self.PlayVideoInstance.vid.stop()
                    self.PlayVideoInstance.vid.close()
                    if self.PlayVideoInstance.disableSplash:
                        self.PlayVideoInstance.opts.loop_flag = True
                        if self.PlayVideoInstance.currVidIndx < len(self.PlayVideoInstance.videoList):
                            self.PlayVideoInstance.currVidIndx += 1
                case const.KEY_OSD:
                    self.PlayVideoInstance.opts.enableOSDcurpos = False
                    if self.PlayVideoInstance.draw_OSD_active:
                        self.PlayVideoInstance.OSD_icon_clear(self.PlayVideoInstance.OSD_ICON_X,
                                                              self.PlayVideoInstance.OSD_ICON_Y)
                        self.PlayVideoInstance.OSD_clear(self.PlayVideoInstance.OSD_TEXT_X,
                                                         self.PlayVideoInstance.OSD_TEXT_Y)
                        self.PlayVideoInstance.OSD_curPos_flag = not self.PlayVideoInstance.OSD_curPos_flag
                    self.PlayVideoInstance.draw_OSD_active = (not self.PlayVideoInstance.draw_OSD_active
                                                              if not self.PlayVideoInstance.OSD_curPos_flag else True)
                    if not self.PlayVideoInstance.draw_OSD_active:
                        pygame.time.set_timer(self.FWD_SEEK_EVENT, 0)
                        pygame.time.set_timer(self.REWIND_SEEK_EVENT, 0)
                        self.PlayVideoInstance.seekRewind_flag = False
                        self.PlayVideoInstance.seekFwd_flag = False
                case const.KEY_PAUSE:
                    self.PlayVideoInstance.vid.toggle_pause()
                    self.PlayVideoInstance.pause = True if self.PlayVideoInstance.vid.paused else False
                case const.KEY_SPACE:
                    if self.PlayVideoInstance.saveMode:
                        self.saveFrameShot()
                    else:
                        self.PlayVideoInstance.vid.toggle_pause()
                        self.PlayVideoInstance.pause = True if self.PlayVideoInstance.vid.paused else False
                case const.KEY_SHOW_TITLES:
                    # Toggle sequence is 'all' -> 'portrait' -> 'landscape' -> None
                    match self.PlayVideoInstance.opts.dispTitles:
                        case 'all':
                            self.PlayVideoInstance.opts.dispTitles = 'portrait'
                        case 'portrait':
                            self.PlayVideoInstance.opts.dispTitles = 'landscape'
                        case 'landscape':
                            self.PlayVideoInstance.opts.dispTitles = None
                        case None:
                            self.PlayVideoInstance.opts.dispTitles = 'all'
                    if self.PlayVideoInstance.opts.dispTitles is not None:
                        self.PlayVideoInstance.video_title = self.PlayVideoInstance.get_video_title(self.PlayVideoInstance.videoList[self.PlayVideoInstance.currVidIndx])
                        #print(self.PlayVideoInstance.video_title)
                    self.PlayVideoInstance.message = f"Display Titles set to: {self.PlayVideoInstance.opts.dispTitles}"
                    self.PlayVideoInstance.saveModeDialogBox(self.PlayVideoInstance.message)
                case const.KEY_QUIT:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                case const.KEY_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                case const.KEY_RESTART:
                    self.PlayVideoInstance.vid.restart()
                    self.PlayVideoInstance.progress_value = 0
                    self.PlayVideoInstance.progress_percentage = 0
                    self.PlayVideoInstance.current_pos = 0
                    pygame.time.wait(50)                            # Small delay to allow state reset
                    # **Step 1: Force OSD reset**
                    self.PlayVideoInstance.last_osd_position = 0.0  # Reset position tracking
                    self.PlayVideoInstance.seek_flag = False        # Reset seek state
                    self.PlayVideoInstance.seek_flag2 = False
                    self.PlayVideoInstance.last_vid_info_pos = 0.0
                    # **Step 2: Force a seek to 0 immediately after restart**
                    self.PlayVideoInstance.vid.seek(0)
                    # **Step 3: Immediately refresh the display**
                    self.PlayVideoInstance.draw_OSD()
                case const.KEY_SCRNSHOT:
                    self.saveFrameShot()
                case const.KEY_PRINT_RECTS:
                    self.PlayVideoInstance.videoPlayBar.print_IconRects()
                case const.KEY_SAVE_PLAYLIST:
                    self.PlayVideoInstance.savePlayListFlag = True
                    fileName = 'VideoPlayList-' + str(len(self.PlayVideoInstance.videoList)) + '.txt'
                    self.PlayVideoInstance.savePlayList(fileName)
                case const.KEY_APPLY_SHARPENING:
                    print("Pressed u key")
                    self.reInitVideo('apply_sharpening', self.PlayVideoInstance.vid.frame)
                case const.KEY_APPLY_DENOISING:
                    print("Pressed v key")
                    self.reInitVideo('apply_denoising', self.PlayVideoInstance.vid.frame)
                case const.KEY_PRT_META_CONSOLE:
                    self.PlayVideoInstance.printMetaData()
                case const.KEY_SEEK_FWD:
                    self.handle_key_seek(20)
                case const.KEY_SEEK_BACK:
                    self.handle_key_seek(-20)
                case const.KEY_PREV_VID:
                    # Disable video loop for current video before going back to the previous one.
                    if self.PlayVideoInstance.opts.loop_flag:
                        self.PlayVideoInstance.opts.loop_flag = False
                    if self.PlayVideoInstance.currVidIndx != 0:
                        self.PlayVideoInstance.backwardsFlag = True
                        self.PlayVideoInstance.vid.stop()
                        self.PlayVideoInstance.vid.close()
                        if self.PlayVideoInstance.disableSplash:
                            self.PlayVideoInstance.opts.loop_flag = True
                case const.KEY_VOL_UP:
                    # Only update the volume if the opts['key_mute_flag'] isn't set
                    if not self.PlayVideoInstance.opts.key_mute_flag:
                        self.PlayVideoInstance.vol = min(1.0, self.PlayVideoInstance.vol + 0.1)
                        self.PlayVideoInstance.vid.set_volume(self.PlayVideoInstance.vol)
                case const.KEY_VOL_DOWN:
                    # Only update the volume if the opts['key_mute_flag'] isn't set
                    if not self.PlayVideoInstance.opts.key_mute_flag:
                        self.PlayVideoInstance.vol = max(0.0, self.PlayVideoInstance.vol - 0.1)
                        self.PlayVideoInstance.vid.set_volume(self.PlayVideoInstance.vol)
                case const.KEY_PLAY_SPEED_UP:
                    self.PlayVideoInstance.opts.playSpeed  = min(5.0, self.PlayVideoInstance.opts.playSpeed + 0.50)
                    # Get the current frame that is playing before stoping and closing the video
                    currFrame = self.PlayVideoInstance.vid.frame
                    self.PlayVideoInstance.vid.stop()
                    self.PlayVideoInstance.vid.close()
                    # Start a new instance of the video
                    try:
                        self.PlayVideoInstance.vid = self.PlayVideoInstance.playVideo(
                            self.PlayVideoInstance.videoList[self.PlayVideoInstance.currVidIndx]
                        )
                        # Seek to the last frame played prior to changing the playback speed
                        self.PlayVideoInstance.vid.seek_frame(currFrame)
                        # Update vid internals
                        self.PlayVideoInstance.vid.update()
                    except Exception as e:
                        pass
                case const.KEY_PLAY_SPEED_DOWN:
                    self.PlayVideoInstance.opts.playSpeed = max(0.50, self.PlayVideoInstance.opts.playSpeed - 0.50)
                    currFrame = self.PlayVideoInstance.vid.frame
                    self.PlayVideoInstance.vid.stop()
                    self.PlayVideoInstance.vid.close()
                    try:
                        self.PlayVideoInstance.vid = self.PlayVideoInstance.playVideo(
                            self.PlayVideoInstance.videoList[self.PlayVideoInstance.currVidIndx]
                        )
                        self.PlayVideoInstance.vid.seek_frame(currFrame)
                        self.PlayVideoInstance.vid.update()
                    except Exception as e:
                        pass
                case const.KEY_F2:
                    self.PlayVideoInstance.print_frame_surf()
                case pygame.K_1 if event.mod & pygame.KMOD_SHIFT:       # ! = sharpen
                    print("Pressed Sharpen key")
                    self.reInitVideo('sharpen', self.PlayVideoInstance.vid.frame)
                case pygame.K_2 if event.mod & pygame.KMOD_SHIFT:       # @ = blur
                    print("Pressed blur key")
                    self.reInitVideo('blur', self.PlayVideoInstance.vid.frame)
                case pygame.K_3 if event.mod & pygame.KMOD_SHIFT:       # # = edge_detect
                    print("Pressed edge_detect key")
                    if self.opts.emboss or self.opts.greyscale or self.opts.sepia:
                        return
                    else:
                        self.reInitVideo('edge_detect', self.PlayVideoInstance.vid.frame)
                case pygame.K_4 if event.mod & pygame.KMOD_SHIFT:       # $ = emboss
                    print("Pressed emboss key")
                    self.reInitVideo('emboss', self.PlayVideoInstance.vid.frame)
                case pygame.K_5 if event.mod & pygame.KMOD_SHIFT:       # % = thermal
                    print("Pressed thermal key")
                    if self.opts.sepia or self.opts.greyscale:
                        return
                    else:
                        self.reInitVideo('thermal', self.PlayVideoInstance.vid.frame)
                case pygame.K_6 if event.mod & pygame.KMOD_SHIFT:       # ^ = dream
                    print("Pressed dream key")
                    if self.opts.sepia or self.opts.greyscale:
                        return
                    else:
                        self.reInitVideo('dream', self.PlayVideoInstance.vid.frame)
                case pygame.K_7 if event.mod & pygame.KMOD_SHIFT:       # & = comic
                    print("Pressed comic key")
                    if self.opts.sepia or self.opts.greyscale:
                        return
                    else:
                        self.reInitVideo('comic', self.PlayVideoInstance.vid.frame)
                case pygame.K_8 if event.mod & pygame.KMOD_SHIFT:       # * = sepia
                    print("Pressed sepia key")
                    if self.opts.sepia:
                        self.reInitVideo('sepia', self.PlayVideoInstance.vid.frame)

                    if self.opts.greyscale:
                        self.opts.greyscale = False

                    self.reInitVideo('sepia', self.PlayVideoInstance.vid.frame)
                case pygame .K_9 if event.mod & pygame.KMOD_SHIFT:      # ( = None
                    print("Pressed None")
                    self.reInitVideo('None', self.PlayVideoInstance.vid.frame)
                case pygame.K_0 if event.mod & pygame.KMOD_SHIFT:       # ) = gaussian_blur
                    print("Pressed gaussian_blur key")
                    self.reInitVideo('gaussian_blur', self.PlayVideoInstance.vid.frame)

    def handle_key_seek(self, seek):
        """
        Handles the key seek functionality for video playback. It updates the seek direction, toggles
        specific timer events, and recalculates progress metrics based on the seek action. If a video
        is active, it adjusts the playback accordingly and computes related duration and progress values.
        If no video is active, it resets all progress-related attributes.

        Parameters:
            seek (int): The amount of time to seek. Positive values indicate forward seeking,
                        and negative values indicate backward seeking.
        """
        seek_fwd = True if seek > 0 else False
        if self.PlayVideoInstance.vid.active:
            self.PlayVideoInstance.progress_timeout = 50
            self.PlayVideoInstance.vid.seek(seek)
            if seek_fwd:
                pygame.time.set_timer(self.FWD_SEEK_EVENT, 20)
                pygame.time.set_timer(self.REWIND_SEEK_EVENT, 0)
                self.PlayVideoInstance.seekFwd_flag = True
                self.PlayVideoInstance.seekRewind_flag = False
            else:
                pygame.time.set_timer(self.REWIND_SEEK_EVENT, 20)
                pygame.time.set_timer(self.FWD_SEEK_EVENT, 0)
                self.PlayVideoInstance.seekRewind_flag = True
                self.PlayVideoInstance.seekFwd_flag = False
            self.PlayVideoInstance.seek_flag = True
            self.PlayVideoInstance.seek_flag2 = True
            self.PlayVideoInstance.total_duration = self.PlayVideoInstance.vid.duration
            self.PlayVideoInstance.current_pos = self.PlayVideoInstance.vid.get_pos()
            self.PlayVideoInstance.progress_value = (
                self.PlayVideoInstance.current_pos / self.PlayVideoInstance.total_duration) * 100
            self.PlayVideoInstance.progress_percentage = (
                self.PlayVideoInstance.current_pos / self.PlayVideoInstance.total_duration) * 100
            self.PlayVideoInstance.progress_active = True
        else:
            self.PlayVideoInstance.total_duration = 0
            self.PlayVideoInstance.current_pos = 0
            self.PlayVideoInstance.progress_value = 0
            self.PlayVideoInstance.progress_percentage = 0
            self.PlayVideoInstance.progress_active = False

    def handle_fwd_seek_event(self):
        """
        Handles the forward seek event triggered in the video player while the
        On-Screen Display (OSD) is active. This function increments a forward
        seek counter and shows a forward icon on the screen at the provided location
        for a limited number of times. When the counter exceeds a defined limit,
        it resets the counter, disables the seek forward flag, and stops the associated
        timer event.

        Raises:
            - This function does not raise any exceptions.

        Parameters:
            - self: Represents the instance of the class that this function belongs
                    to, allowing access to class attributes and other methods.

        """
        if self.PlayVideoInstance.draw_OSD_active:
            self.FwdSeekCounter += 1
            if self.FwdSeekCounter <= 5:
                self.PlayVideoInstance.foward_icon(self.PlayVideoInstance.OSD_ICON_X, self.PlayVideoInstance.OSD_ICON_Y)
                pygame.display.update(
                            self.PlayVideoInstance.OSD_ICON_X,
                            self.PlayVideoInstance.OSD_ICON_Y,
                            self.PlayVideoInstance.OSD_ICON_WIDTH,
                            self.PlayVideoInstance.OSD_ICON_HEIGHT
                            )
            else:
                self.FwdSeekCounter = 0
                self.PlayVideoInstance.seekFwd_flag = False
                pygame.time.set_timer(self.FWD_SEEK_EVENT, 0)

    def handle_rewind_seek_event(self):
        """
        Handles the event for rewind seek in a video player by managing the display of the rewind icon
        and updating the corresponding states and flags. This method is linked to the
        REWIND_SEEK_EVENT, controlling its behavior.

        Raises:
            No explicit errors are raised, but this method depends on pygame and proper attribute
            states within the PlayVideoInstance.

        Attributes:
            PlayVideoInstance: Instance of the video player controlling the OSD (On-Screen Display),
                rewind behavior, and state variables.
            RewindSeekCounter: Counter tracking the number of times the rewind seek icon is displayed.
            REWIND_SEEK_EVENT: Event ID managed by pygame to trigger this specific behavior.
        """
        if self.PlayVideoInstance.draw_OSD_active and self.PlayVideoInstance.seekRewind_flag:
            self.RewindSeekCounter += 1
            if self.RewindSeekCounter <= 5:
                self.PlayVideoInstance.rewind_icon(self.PlayVideoInstance.OSD_ICON_X, self.PlayVideoInstance.OSD_ICON_Y)
                pygame.display.update(
                            self.PlayVideoInstance.OSD_ICON_X,
                            self.PlayVideoInstance.OSD_ICON_Y,
                            self.PlayVideoInstance.OSD_ICON_WIDTH,
                            self.PlayVideoInstance.OSD_ICON_HEIGHT
                            )
            else:
                self.RewindSeekCounter = 0
                self.PlayVideoInstance.seekRewind_flag = False
                pygame.time.set_timer(self.REWIND_SEEK_EVENT, 0)

    def is_running(self):
        """
        Determines if the object is currently running.

        This method checks the state of the 'running' attribute and returns its
        value to indicate whether the object is in a running state.

        Returns
        -------
        bool
            True if the 'running' attribute is set to True, otherwise False.
        """
        return self.running

    @staticmethod
    def isKeyCombo(event, key, mods):
        """
        Determines whether a specific key and modifier keys combination has been
        pressed.

        This utility method evaluates an event and matches it against the given
        key and modifier keys, checking if they coincide.

        Parameters:
        event (Event): The event object containing key press data.
        key (int): The key code to match.
        mods (int): The modifier keys bitmask to match.

        Returns:
        bool: True if the given key and modifiers match the event; False otherwise.
        """
        return event.key == key and pygame.key.get_mods() & mods

    def saveFrameShot(self):
        """
        Queues a screenshot operation to be performed during the next frame render.
        """
        # Early exit if no frame available
        if self.PlayVideoInstance.vid.frame_surf is None:
            return

        saveDir = self.PlayVideoInstance.check_SSHOT_dir()
        msg = self.PlayVideoInstance.save_sshot_error
        if msg is not None or saveDir is None:
            return

        # Instead of doing file operations here, just prepare the filename
        base_sshot_name = self.PlayVideoInstance.generate_screenshot_name(saveDir)
        sshot_name = base_sshot_name
        counter = 1

        # Do filename generation but limit iterations
        MAX_ATTEMPTS = 1000
        while counter < MAX_ATTEMPTS and os.path.exists(sshot_name):
            name, ext = os.path.splitext(base_sshot_name)
            sshot_name = f"{name}_{counter}{ext}"
            counter += 1

        if counter >= MAX_ATTEMPTS:
            self.PlayVideoInstance.message = "Could not generate unique filename"
            self.PlayVideoInstance.saveModeDialogBox(self.PlayVideoInstance.message, sleep=True)
            return

        self.PlayVideoInstance.vid.pause()
        print("self.PlayVideoInstance.vid.pause()")
        # Queue the screenshot operation instead of doing it immediately
        self.PlayVideoInstance.save_sshot_filename = sshot_name
        self.PlayVideoInstance.saveScreenShotFlag = True
        self.PlayVideoInstance.saveCount += 1

    def update_video_speed(self, mouse_x, mouse_y):
        """
        Updates the playback speed of the current video based on mouse click position.

        This method adjusts the playback speed of a video depending on whether the user
        clicks on the left or right side of the playback speed control. If the speed is
        changed, the method stops the current video, adjusts its speed, and resumes the
        video from the same frame.

        Params:
            mouse_x (float): The x-coordinate of the mouse click.
            mouse_y (float): The y-coordinate of the mouse click.
        """
        currFrame = 0
        videoFile = self.PlayVideoInstance.videoList[self.PlayVideoInstance.currVidIndx]
        if self.PlayVideoInstance.play_speed_rect and self.PlayVideoInstance.play_speed_rect.collidepoint(mouse_x, mouse_y):
            center_x = self.PlayVideoInstance.play_speed_rect.x + (self.PlayVideoInstance.play_speed_rect.width // 2)
            if mouse_x < center_x:
                new_speed = max(0.50, round(self.PlayVideoInstance.opts.playSpeed - 0.50, 1))
            else:
                new_speed = min(5.0, round(self.PlayVideoInstance.opts.playSpeed + 0.50, 1))

            if new_speed != self.PlayVideoInstance.opts.playSpeed:
                self.PlayVideoInstance.opts.playSpeed = new_speed
                # Get the current frame that is playing before stoping and closing the video
                currFrame = self.PlayVideoInstance.vid.frame
                self.PlayVideoInstance.vid.stop()
                self.PlayVideoInstance.vid.close()
                # Start a new instance of the video
            try:
                self.PlayVideoInstance.vid = self.PlayVideoInstance.playVideo( videoFile )
                # Seek to the last frame played prior to changing the playback speed
                self.PlayVideoInstance.vid.seek_frame(currFrame)
                # Update vid internals
                self.PlayVideoInstance.vid.update()

            except Exception as e:
                pass

    def update_volume(self, mouse_x, mouse_y):
        """
        Updates the volume level of a video player based on mouse interaction.
        The method adjusts the volume either up or down depending on the position
        of the mouse relative to the center of the volume control rectangle.
        It also handles muting and unmuting of the player and reflects the updated
        volume on both the visual interface and the internal video playback settings.

        Args:
            mouse_x (int): The x-coordinate of the mouse position.
            mouse_y (int): The y-coordinate of the mouse position.
        """
        # This statement fist checks if vol_rect is properly initialized or is set to None
        if self.PlayVideoInstance.vol_rect and self.PlayVideoInstance.vol_rect.collidepoint(mouse_x, mouse_y):
            center_x = self.PlayVideoInstance.vol_rect.x + (self.PlayVideoInstance.vol_rect.width // 2)
            if mouse_x < center_x:
                new_volume = max(0.0, round(self.PlayVideoInstance.volume - 0.10, 1))
            else:
                new_volume = min(1.0, round(self.PlayVideoInstance.volume + 0.10, 1))
            # Mute handling
            self.PlayVideoInstance.muted = new_volume == 0.0  # If at 0, consider muted
            self.PlayVideoInstance.volume = new_volume
            self.PlayVideoInstance.vol = self.PlayVideoInstance.volume
            self.PlayVideoInstance.vid.set_volume(self.PlayVideoInstance.volume)

            if self.PlayVideoInstance.opts.verbose:
                print(f"Volume: {int(self.PlayVideoInstance.volume * 100)}% {'(Muted)' if self.PlayVideoInstance.muted else ''}")
                print(f"vid.get_volume(): {self.PlayVideoInstance.vid.get_volume()}")

            if self.PlayVideoInstance.muted:
                self.PlayVideoInstance.vid.mute()
            else:
                self.PlayVideoInstance.vid.unmute()

    def update_video_info(self, mouse_x, mouse_y):
        """
        Updates the state of the video-related information box tooltip based on mouse position
        and manages hover state for the video information button.

        Parameters:
        mouse_x : int
            The x-coordinate of the mouse pointer.
        mouse_y : int
            The y-coordinate of the mouse pointer.
        """
        if self.PlayVideoInstance.drawVidInfo.filename_rect.collidepoint(mouse_x, mouse_y):
            self.PlayVideoInstance.video_info_box_tooltip = True
            self.PlayVideoInstance.video_info_box_tooltip_mouse_x = mouse_x + 15
            self.PlayVideoInstance.video_info_box_tooltip_mouse_y = mouse_y + 5
            self.PlayVideoInstance.drawVidInfo.draw_tooltip(
                                            self.PlayVideoInstance.win,
                                            self.PlayVideoInstance.vid.name + self.PlayVideoInstance.vid.ext,
                                            mouse_x + 15,
                                            mouse_y + 5
                                            )
        else:
            self.PlayVideoInstance.video_info_box_tooltip = False

        self.PlayVideoInstance.drawVidInfo.is_hovered = self.PlayVideoInstance.drawVidInfo.button_rect.collidepoint(mouse_x, mouse_y)

    def update_videoPlayBarVolume(self, Event, mouse_x, mouse_y):
        """
        Updates the volume of the video play bar based on user interaction.

        This function handles the event of adjusting the volume of the video play bar
        when the user interacts with it using the mouse and buttons. It updates the
        volume level by detecting mouse position and button clicks and modifies the
        corresponding attributes in the video player instance. Additionally, it handles
        muting when the volume is set to zero, and updates the muted status
        appropriately.

        Parameters:
            Event (Event): The event object containing information about the mouse
            button interaction.
            mouse_x (int): The x-coordinate of the mouse cursor during the event.
            mouse_y (int): The y-coordinate of the mouse cursor during the event.

        """
        new_volume = 0
        if self.PlayVideoInstance.drawVideoPlayBarFlag:
            # Update the VideoPlayBar instance with the current mouse coordinates
            self.PlayVideoInstance.videoPlayBar.MOUSE_X = mouse_x
            self.PlayVideoInstance.videoPlayBar.MOUSE_Y = mouse_y
            iconYcord = mouse_y - 2040
            # Check if the local mouse position collides with the volume slider rectangle
            if self.PlayVideoInstance.videoPlayBar.volumeRect.collidepoint(mouse_x, iconYcord):
                # Adjust volume: Increase if left-clicked, decrease if right-clicked
                if Event.button == 1:       # Left-click  Increase Volume
                    new_volume = min(1.0, round(self.PlayVideoInstance.volume + 0.10, 1))
                    print(f"Vol(+): {new_volume}")
                elif Event.button == 3:     # Right-click Decrease Volume
                    new_volume = max(0.0, round(self.PlayVideoInstance.volume - 0.10, 1))
                    print(f"Vol(-): {new_volume}")
                # Mute handling
                self.PlayVideoInstance.muted = new_volume == 0.0  # If at 0, consider muted
                self.PlayVideoInstance.volume = new_volume
                self.PlayVideoInstance.vol = self.PlayVideoInstance.volume
                self.PlayVideoInstance.vid.set_volume(self.PlayVideoInstance.volume)
                print(f"Volume: {int(self.PlayVideoInstance.volume * 100)}% {'(Muted)' if self.PlayVideoInstance.muted else ''}")
                print(f"vid.get_volume(): {self.PlayVideoInstance.vid.get_volume()}")
                
                if self.PlayVideoInstance.muted:
                    self.PlayVideoInstance.vid.mute()
                    self.PlayVideoInstance.videoPlayBar.muted = True
                else:
                    self.PlayVideoInstance.vid.unmute()
                    self.PlayVideoInstance.videoPlayBar.muted = False

    def videoPlayBarIconPress(self, event, mouse_x, mouse_y):
        """
        Handles interaction with video play bar icons such as play, stop, next, previous, speaker,
        speed adjustment, and repeat icons. This method maps mouse click events over specific icon
        areas and executes the corresponding functionalities. For example, toggles play/pause, stops
        the video, advances to the next video, adjusts playback speed, toggles mute, or enables/disables
        video repeat mode. The operations are applied directly to the PlayVideoInstance object and may
        modify playback behavior.

        Parameters:
            event: pygame.event.Event
                The mouse event captured when interacting with the play bar.
            mouse_x: int
                The horizontal coordinate of the mouse pointer during the event.
            mouse_y: int
                The vertical coordinate of the mouse pointer during the event.
        """
        for name, rect in self.PlayVideoInstance.videoPlayBar.IconRects.items():
            if rect.collidepoint(mouse_x, mouse_y - self.PlayVideoInstance.videoPlayBar.bar_top):
                match name:
                    case 'playIcon':
                        self.PlayVideoInstance.vid.toggle_pause()
                        if self.PlayVideoInstance.vid.paused:
                            self.PlayVideoInstance.pause = True
                        else:
                            self.PlayVideoInstance.pause = False
                            self.PlayVideoInstance.stopButtonClicked = False
                            self.PlayVideoInstance.currVidIndx = -1
                        self.PlayVideoInstance.videoPlayBar.vid_paused = self.PlayVideoInstance.pause
                    case 'stopIcon':
                        pygame.event.post(pygame.event.Event(pygame.QUIT))
                    case 'nextIcon':
                        self.PlayVideoInstance.opts.loop_flag = False
                        self.PlayVideoInstance.forwardsFlag = True
                        # Disable video loop for current video before advancing to the next one.
                        if self.PlayVideoInstance.opts.loop_flag:
                            self.PlayVideoInstance.opts.loop_flag = False
                        self.PlayVideoInstance.vid.stop()
                        self.PlayVideoInstance.vid.close()
                        if self.PlayVideoInstance.disableSplash:
                            self.PlayVideoInstance.opts.loop_flag = True
                            if self.PlayVideoInstance.currVidIndx < len(self.PlayVideoInstance.videoList) - 1:
                                self.PlayVideoInstance.currVidIndx += 1
                    case 'previousIcon':
                        self.PlayVideoInstance.opts.loop_flag = False
                        # Disable video loop for the current video before going back to the previous one.f
                        if self.PlayVideoInstance.opts.loop_flag:
                            self.PlayVideoInstance.opts.loop_flag = False
                        if self.PlayVideoInstance.currVidIndx != 0:
                            self.PlayVideoInstance.backwardsFlag = True
                            self.PlayVideoInstance.vid.stop()
                            self.PlayVideoInstance.vid.close()
                            if self.PlayVideoInstance.disableSplash:
                                self.PlayVideoInstance.opts.loop_flag = True
                    case 'speakerIcon':
                        if self.PlayVideoInstance.mute_flag:
                            self.PlayVideoInstance.vid.toggle_mute()
                            self.PlayVideoInstance.mute_flag = False
                            self.PlayVideoInstance.key_mute_flag = True if self.PlayVideoInstance.vid.muted is True else False
                        else:
                            self.PlayVideoInstance.key_mute_flag = not self.PlayVideoInstance.key_mute_flag
                            self.PlayVideoInstance.vid.mute() if self.PlayVideoInstance.key_mute_flag is True else self.PlayVideoInstance.vid.unmute()
                        self.PlayVideoInstance.videoPlayBar.muted =  self.PlayVideoInstance.key_mute_flag
                    case 'plusIcon':
                        currFrame = 0
                        videoFile = self.PlayVideoInstance.videoList[self.PlayVideoInstance.currVidIndx]
                        new_speed = max(0.50, round(self.PlayVideoInstance.opts.playSpeed + 0.50, 1))
                        if new_speed != self.PlayVideoInstance.opts.playSpeed:
                            self.PlayVideoInstance.opts.playSpeed = new_speed
                            # Get the current frame that is playing before stoping and closing the video
                            currFrame = self.PlayVideoInstance.vid.frame
                            self.PlayVideoInstance.vid.stop()
                            self.PlayVideoInstance.vid.close()
                            # Start a new instance of the video
                            try:
                                self.PlayVideoInstance.vid = self.PlayVideoInstance.playVideo(videoFile)
                                # Seek to the last frame played before changing the playback speed
                                self.PlayVideoInstance.vid.seek_frame(currFrame)
                                # Update vid internals
                                self.PlayVideoInstance.vid.update()
                            except Exception as e:
                                pass
                    case 'minusIcon':
                        currFrame = 0
                        videoFile = self.PlayVideoInstance.videoList[self.PlayVideoInstance.currVidIndx]
                        new_speed = max(0.50, round(self.PlayVideoInstance.opts.playSpeed - 0.50, 1))
                        if new_speed != self.PlayVideoInstance.opts.playSpeed:
                            self.PlayVideoInstance.opts.playSpeed = new_speed
                            # Get the current frame that is playing before stoping and closing the video
                            currFrame = self.PlayVideoInstance.vid.frame
                            self.PlayVideoInstance.vid.stop()
                            self.PlayVideoInstance.vid.close()
                            # Start a new instance of the video
                            try:
                                self.PlayVideoInstance.vid = self.PlayVideoInstance.playVideo(videoFile)
                                # Seek to the last frame played before changing the playback speed
                                self.PlayVideoInstance.vid.seek_frame(currFrame)
                                # Update vid internals
                                self.PlayVideoInstance.vid.update()
                            except Exception as e:
                                pass
                    case 'repeatIcon':
                        self.PlayVideoInstance.opts.loop_flag = not self.PlayVideoInstance.opts.loop_flag
                        self.PlayVideoInstance.videoPlayBar.loop_flag = self.PlayVideoInstance.opts.loop_flag
                    case 'screenShotIcon':
                        self.saveFrameShot()
               #print(f"{name} clicked")

    def videoPlayBarIconHover(self, event, mouse_x, mouse_y):
        """
        Handles the hover events over the video play bar icons and dynamically displays tooltips for the "next" and
        "previous" icons, indicating associated file names. Ensures that only one tooltip is displayed at a time and
        updates the tooltip's position and content based on the hovered icon.

        Arguments:
            event: A pygame event object containing the event data.
            mouse_x: int. The current x-coordinate of the mouse cursor.
            mouse_y: int. The current y-coordinate of the mouse cursor.
        """
        iconYcord = (self.PlayVideoInstance.videoPlayBar.displayHeight - self.PlayVideoInstance.videoPlayBar.barHeight_Offset) - 48
        for name, rect in self.PlayVideoInstance.videoPlayBar.IconRects.items():
            if rect.collidepoint(mouse_x, iconYcord):
                if name =='nextIcon':
                    # no previous Icon tooltip
                    if self.PlayVideoInstance.drawVideoPlayBarToolTipLastIcon is None:
                        # save the current state
                        self.PlayVideoInstance.drawVideoPlayBarToolTipLastIcon = name
                    else:
                        # make the previous tooltip disappear
                        self.PlayVideoInstance.drawVideoPlayBarToolTip = True
                        self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_x = self.PlayVideoInstance.VideoPlayBarToolTipMouseLast_x
                        self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_y = self.PlayVideoInstance.VideoPlayBarToolTipMouseLast_y
                        self.PlayVideoInstance.videoPlayBar.draw_tooltip(
                                                                    self.PlayVideoInstance.drawVideoPlayBarToolTipTextLast,
                                                                    self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_x,
                                                                    self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_y,
                                                                     0
                                                                     )

                    self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_x = mouse_x
                    self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_y = mouse_y
                    nextFileName =  os.path.basename(self.PlayVideoInstance.videoList[self.PlayVideoInstance.currVidIndx+1])
                    self.PlayVideoInstance.drawVideoPlayBarToolTipTextLast = nextFileName
                    self.PlayVideoInstance.drawVideoPlayBarToolTipText = nextFileName
                    self.PlayVideoInstance.drawVideoPlayBarToolTip = True
                    self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_x = mouse_x
                    self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_y = mouse_y
                    self.PlayVideoInstance.videoPlayBar.draw_tooltip(
                                                                     nextFileName,
                                                                     self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_x,
                                                                     self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_y,
                                                                     150
                                                                     )
                if name =='previousIcon':
                    # no previous Icon tooltip
                    if self.PlayVideoInstance.drawVideoPlayBarToolTipLastIcon is None:
                        # save the current state
                        self.PlayVideoInstance.drawVideoPlayBarToolTipLastIcon = name
                    else:
                        # make the previous tooltip disappear
                        self.PlayVideoInstance.drawVideoPlayBarToolTip = True
                        self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_x = self.PlayVideoInstance.VideoPlayBarToolTipMouseLast_x
                        self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_y = self.PlayVideoInstance.VideoPlayBarToolTipMouseLast_y
                        self.PlayVideoInstance.videoPlayBar.draw_tooltip(
                                                                    self.PlayVideoInstance.drawVideoPlayBarToolTipTextLast,
                                                                    self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_x,
                                                                    self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_y,
                                                                     0
                                                                     )

                    self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_x = mouse_x
                    self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_y = mouse_y
                    if self.PlayVideoInstance.currVidIndx > 0:
                        previousFileName = os.path.basename(self.PlayVideoInstance.videoList[self.PlayVideoInstance.currVidIndx - 1])
                        self.PlayVideoInstance.drawVideoPlayBarToolTipTextLast = previousFileName
                        self.PlayVideoInstance.drawVideoPlayBarToolTipText = previousFileName
                        self.PlayVideoInstance.drawVideoPlayBarToolTip = True
                        self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_x = mouse_x
                        self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_y = mouse_y
                        self.PlayVideoInstance.videoPlayBar.draw_tooltip(
                                                                         previousFileName,
                                                                         self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_x,
                                                                         self.PlayVideoInstance.drawVideoPlayBarToolTipMouse_y,
                                                                         150
                                                                         )
                    else:
                        self.PlayVideoInstance.drawVideoPlayBarToolTip = False

    def reInitVideo(self, flag, frame_num):
        pp_flag = None
        last_frame = frame_num

        match(flag):
            case 'apply_denoising':
                self.opts.apply_denoising = not self.opts.apply_denoising
                print(f"apply_denoising: {'True' if self.opts.apply_denoising else 'False'}")
                pp_flag = self.opts.apply_denoising
            case 'apply_sharpening':
                self.opts.apply_sharpening = not self.opts.apply_sharpening
                print(f"apply_sharpening: {'True' if self.opts.apply_sharpening else 'False'}")
                pp_flag = self.opts.apply_sharpening
            case 'apply_edges_sobel':
                self.opts.apply_edges_sobel =  not self.opts.apply_edges_sobel
                print(f"apply_edges_sobel {'True' if self.opts.apply_edges_sobel else 'False'}")
                pp_flag = self.opts.apply_edges_sobel
            case 'apply_inverted':
                self.opts.apply_inverted = not self.opts.apply_inverted
                print(f"apply_inverted: {'True' if self.opts.apply_inverted else 'False'}")
            case 'apply_contrast_enhancement':
                self.opts.apply_contrast_enhancement = not self.opts.apply_contrast_enhancement
                print(f"apply_contrast_enhancement: {'True' if self.opts.apply_contrast_enhancement else 'False'}")
                pp_flag = self.opts.apply_contrast_enhancement
            case 'greyscale':
                self.opts.greyscale = not self.opts.greyscale
                print(f"greyscale: {'True' if self.opts.greyscale else 'False'}")
                pp_flag = self.opts.greyscale
            case 'sharpen':
                self.opts.sharpen = not self.opts.sharpen
                print(f"sharpen: {'True' if self.opts.sharpen else 'False'}")
                pp_flag = self.opts.sharpen
                print(f"sharpen: {'True' if pp_flag else 'False'}")
            case 'blur':
                self.opts.blur = not self.opts.blur
                print(f"blur: {'True' if self.opts.blur else 'False'}")
                pp_flag = self.opts.blur
            case 'gaussian_blur':
                self.opts.gaussian_blur = not self.opts.gaussian_blur
                print(f"gaussian_blur: {'True' if self.opts.gaussian_blur else 'False'}")
                pp_flag = self.opts.gaussian_blur
            case 'sepia':
                self.opts.sepia = not self.opts.sepia
                print(f"sepia: {'True' if self.opts.sepia else 'False'}")
                pp_flag = self.opts.sepia
            case 'edge_detect':
                self.opts.edge_detect = not self.opts.edge_detect
                print(f"edge_detect: {'True' if self.opts.edge_detect else 'False'}")
                pp_flag = self.opts.edge_detect
            case 'emboss':
                self.opts.emboss = not self.opts.emboss
                print(f"emboss: {'True' if self.opts.emboss else 'False'}")
                pp_flag = self.opts.emboss
            case 'neon':
                self.opts.neon = not self.opts.neon
                print(f"neon: {'True' if self.opts.neon else 'False'}")
                pp_flag = self.opts.neon
            case 'dream':
                self.opts.dream = not self.opts.dream
                print(f"dream: {'True' if self.opts.dream else 'False'}")
                pp_flag = self.opts.dream
            case 'thermal':
                self.opts.thermal = not self.opts.thermal
                print(f"thermal: {'True' if self.opts.thermal else 'False'}")
                pp_flag = self.opts.thermal
            case 'comic':
                self.opts.comic = not self.opts.comic
                print(f"comic: {'True' if self.opts.comic else 'False'}")
                pp_flag = self.opts.comic
            case 'None':
                self.opts.comic = False
                self.opts.thermal = False
                self.opts.emboss = False
                self.opts.sharpen = False
                self.opts.greyscale = False
                self.opts.sepia = False
                self.opts.edge_detect = False
                self.opts.blur = False
                self.opts.neon = False
                self.opts.dream = False
                self.opts.sharpen = False
                self.opts.adjust_video = False
                self.opts.brightness  = 0
                self.opts.contrast    = 0
                self.opts.gaussian_blur = False
                self.opts.apply_inverted = False
                self.opts.apply_denoising = False
                self.opts.apply_edges_sobel = False
                self.opts.apply_sharpening = False
                self.opts.apply_contrast_enhancement = False
                print("None")


        if pp_flag is not None:
            self.reinit_video(last_frame)

    def reinit_video(self, lastFrame):
        self.PlayVideoInstance.update_video_effects()
        self.PlayVideoInstance.vid.stop()
        self.PlayVideoInstance.vid.close()
        self.PlayVideoInstance.vid = self.PlayVideoInstance.playVideo(self.PlayVideoInstance.videoList[self.PlayVideoInstance.currVidIndx])
        self.PlayVideoInstance.vid.seek_frame(lastFrame)

