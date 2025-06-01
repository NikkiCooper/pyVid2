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
    def __init__(self, PlayVideoInstance):
        """
        A class which setups a pygame event handler.
        :param PlayVideoInstance:
        :type PlayVideoInstance:
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
        #pygame.time.set_timer(self.timer_event, 1000)      # Our timer_event occurs every 1000 ms.
        self.elapsed_time = None
        self.previous_speed = 0
        self.mouse_press_times = {}
        self.short_click_threshold = 0.50
        self.long_click_threshold = 1.0
        #
        # Adjust as needed.  0.15 means 15% of the screen height
        #self.threshold_ratio = 0.15
        self.threshold_ratio = 0.052
        self.threshold = int(self.PlayVideoInstance.displayHeight * self.threshold_ratio)
        self.current_video = -1

    def handle_events(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                    self.PlayVideoInstance.quit_video()
                case pygame.MOUSEMOTION:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.handle_mouse_motion(mouse_x, mouse_y)
                case pygame.MOUSEBUTTONDOWN:
                    self.mouse_press_times[event.button] = pygame.time.get_ticks()
                case pygame.MOUSEBUTTONUP:
                    self.handle_mouse_button_up(event)
                case pygame.KEYDOWN:
                    self.handle_keydown(event)
                case pygame.MOUSEWHEEL:
                    self.PlayVideoInstance.progress_timeout = 50
                    if event.x == 0 and event.y != 0:
                        # handle_mouse_wheel determines whether the pygame.MOUSEWHEEL event is
                        # a mousewheel up or mousewheel down.  It will automatially adjust the
                        # seek time to negative on a mousewheel down event.
                        self.handle_mouse_wheel(5, event)
                case self.FWD_SEEK_EVENT:
                    self.handle_fwd_seek_event()
                case self.REWIND_SEEK_EVENT:
                    self.handle_rewind_seek_event()

    def handle_mouse_button_up(self, event):
        if event.button in self.mouse_press_times:
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
        # Help dialog
        '''
        if self.PlayVideoInstance.help_visible:
            mouse_pos = (mouse_x, mouse_y)
            self.PlayVideoInstance.help_button_rect = self.PlayVideoInstance.draw_help(self.PlayVideoInstance.is_hovered)
            self.PlayVideoInstance.is_hovered = self.PlayVideoInstance.help_button_rect.collidepoint(mouse_pos)
            self.PlayVideoInstance.help_button_rect = self.PlayVideoInstance.draw_help(self.PlayVideoInstance.is_hovered)
        '''

        if self.PlayVideoInstance.video_info_box:
            # render the tooltip
            self.update_video_info(mouse_x, mouse_y)
            #self.update_video_path_info(mouse_x, mouse_y)
        # Tottle new status bar visibility
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

    def handle_mouse_wheel(self, seek, event):
        """
        if event.y > 0, this is a MOUSEWHEEL UP EVENT
        if event.y < 0, this as a MOUSEWHEEL DOWN event
        event.y == 0 is not possible here because we filter it out prior to calling this method.
        """
        seek_fwd  = True if event.y > 0 else False
        seek_time = seek if seek_fwd else -seek
        #print(f"seek_time: {seek_time},  seek_fwd: {('True' if seek_fwd is True else 'False')}")
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
        match event.key:
            case const.KEY_PRINT_CLI:
                self.PlayVideoInstance.print_cli_options()
            case const.KEY_SHUFFLE:
                self.PlayVideoInstance.shuffleVideoList()
                self.PlayVideoInstance.shuffleSplashFlag = True
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
            case (const.KEY_PAUSE):
                self.PlayVideoInstance.vid.toggle_pause()
                self.PlayVideoInstance.pause = True if self.PlayVideoInstance.vid.paused else False
            case (const.KEY_SPACE):
                self.PlayVideoInstance.vid.toggle_pause()
                self.PlayVideoInstance.pause = True if self.PlayVideoInstance.vid.paused else False
            case (const.KEY_QUIT):
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            case (const.KEY_ESCAPE):
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
                msg = self.PlayVideoInstance.check_SSHOT_dir()
                if msg is None:
                    self.PlayVideoInstance.saveScreenShotFlag = True
                    self.PlayVideoInstance.vid.pause()
                    sshot_name = f"{self.PlayVideoInstance.SCREEN_SHOT_DIR}/{self.PlayVideoInstance.generate_screenshot_name()}"
                    self.PlayVideoInstance.save_sshot_error = sshot_name
                    self.PlayVideoInstance.save_screenshot(sshot_name)
            case const.KEY_PRINT_RECTS:
                self.PlayVideoInstance.videoPlayBar.print_IconRects()
            case const.KEY_SAVE_PLAYLIST:
                self.PlayVideoInstance.savePlayListFlag = True
                fileName = 'VideoPlayList-' + str(len(self.PlayVideoInstance.videoList)) + '.txt'
                self.PlayVideoInstance.savePlayList(fileName)
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

    def handle_key_seek(self, seek):
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
        A helper method which determines if the handle_events() method is running
        :return:
        :rtype:
        """
        return self.running

    def update_video_speed(self, mouse_x, mouse_y):
        currFrame = 0
        videoFile = self.PlayVideoInstance.videoList[self.PlayVideoInstance.currVidIndx]

        if self.PlayVideoInstance.play_speed_rect and self.PlayVideoInstance.play_speed_rect.collidepoint(mouse_x, mouse_y):
            center_x = self.PlayVideoInstance.play_speed_rect.x + (self.PlayVideoInstance.play_speed_rect.width // 2)
            if mouse_x < center_x:
                new_speed = max(0.50, round(self.PlayVideoInstance.opts.playSpeed - 0.50, 1))
            else:
                new_speed = min(5.0, round(self.PlayVideoInstance.opts.playSpeed + 0.50, 1))

            #
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

    def update_video_path_info(self, mouse_x, mouse_y):
        if self.PlayVideoInstance.drawVidInfo.path_rect.collidepoint(mouse_x, mouse_y):
            #print(f"self.PlayVideoInstance.filePath: {self.PlayVideoInstance.filePath}")
            self.PlayVideoInstance.video_info_box_path_tooltip = True
            self.PlayVideoInstance.video_info_box_path_tooltip_mouse_x = mouse_x + 15
            self.PlayVideoInstance.video_info_box_path_tooltip_mouse_y = mouse_y + 5
            self.PlayVideoInstance.drawVidInfo.draw_path_tooltip(
                                            self.PlayVideoInstance.win,
                                            self.PlayVideoInstance.filePath,
                                            mouse_x + 15,
                                            mouse_y + 5
                                            )
        else:
            self.PlayVideoInstance.video_info_box_path_tooltip = False

    def update_videoPlayBarVolume(self, Event, mouse_x, mouse_y):
        if self.PlayVideoInstance.drawVideoPlayBarFlag:
            # Update the VideoPlayBar instance with the current mouse coordinates
            self.PlayVideoInstance.videoPlayBar.MOUSE_X = mouse_x
            self.PlayVideoInstance.videoPlayBar.MOUSE_Y = mouse_y

            # Convert the global mouse_y to local coordinates on the playback bar
            # (1139 is your determined offset)
            #local_mouse_y = mouse_y - 1139
            iconYcord = mouse_y - 1139
            #iconYcord = int((self.PlayVideoInstance.videoPlayBar.displayHeight - self.PlayVideoInstance.videoPlayBar.barHeight_Offset) - 48)
            print(f"iconYcord: {iconYcord}")

            #print(f"mouse x,y: ({mouse_x}, {local_mouse_y}), self.PlayVideoInstance.videoPlayBar.volumeRect: {self.PlayVideoInstance.videoPlayBar.volumeRect}")

            # Check if the local mouse position collides with the volume slider rectangle
            if self.PlayVideoInstance.videoPlayBar.volumeRect.collidepoint(mouse_x, iconYcord):
                # Adjust volume: Increase if left click, decrease if right click
                if Event.button == 1:  # Left click
                    self.PlayVideoInstance.videoPlayBar.volumeLevel = min(
                        self.PlayVideoInstance.videoPlayBar.volumeLevel + 5, 100)
                    new_volume = max(0.0, round(self.PlayVideoInstance.volume + 0.10, 1))
                    print("Incremented Volume")
                elif Event.button == 3:  # Right click
                    new_volume = max(0.0, round(self.PlayVideoInstance.volume - 0.10, 1))
                    self.PlayVideoInstance.videoPlayBar.volumeLevel = max(
                        self.PlayVideoInstance.videoPlayBar.volumeLevel - 5, 0)
                    print("Decremented Volume")

                #self.PlayVideoInstance.videoPlayBar.volumeLevel = new_volume
                self.PlayVideoInstance.muted = new_volume == 0.0  # If at 0, consider muted
                self.PlayVideoInstance.volume = new_volume
                self.PlayVideoInstance.vol = self.PlayVideoInstance.volume
                self.PlayVideoInstance.vid.set_volume(self.PlayVideoInstance.volume)
                print(f"Volume Level: {int(round(self.PlayVideoInstance.videoPlayBar.volumeLevel, 1) * 100)}%")  # Debug Output
                
                if self.PlayVideoInstance.muted:
                    self.PlayVideoInstance.vid.mute()
                    self.PlayVideoInstance.videoPlayBar.muted = True
                else:
                    self.PlayVideoInstance.vid.unmute()
                    self.PlayVideoInstance.videoPlayBar.muted = False

    def videoPlayBarIconPress(self, event, mouse_x, mouse_y):

        iconYcord = (self.PlayVideoInstance.videoPlayBar.displayHeight - self.PlayVideoInstance.videoPlayBar.barHeight_Offset) - 48
        for name, rect in self.PlayVideoInstance.videoPlayBar.IconRects.items():
            if rect.collidepoint(mouse_x, iconYcord):

                if name =='playIcon':
                    self.PlayVideoInstance.vid.toggle_pause()
                    if self.PlayVideoInstance.vid.paused:
                        self.PlayVideoInstance.pause = True
                    else:
                        self.PlayVideoInstance.pause = False
                        self.PlayVideoInstance.stopButtonClicked = False
                        self.PlayVideoInstance.currVidIndx = -1
                    self.PlayVideoInstance.videoPlayBar.vid_paused = self.PlayVideoInstance.pause

                elif name == 'stopIcon':
                    #self.PlayVideoInstance.vid.stop()
                    #self.PlayVideoInstance.vid.close()
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                    #return

                elif name == 'nextIcon':
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

                elif name == 'previousIcon':
                    self.PlayVideoInstance.opts.loop_flag = False
                    # Disable video loop for current video before going back to the previous one.f
                    if self.PlayVideoInstance.opts.loop_flag:
                        self.PlayVideoInstance.opts.loop_flag = False
                    if self.PlayVideoInstance.currVidIndx != 0:
                        self.PlayVideoInstance.backwardsFlag = True
                        self.PlayVideoInstance.vid.stop()
                        self.PlayVideoInstance.vid.close()
                        if self.PlayVideoInstance.disableSplash:
                            self.PlayVideoInstance.opts.loop_flag = True

                elif name == 'speakerIcon':
                    if self.PlayVideoInstance.mute_flag:
                        self.PlayVideoInstance.vid.toggle_mute()
                        self.PlayVideoInstance.mute_flag = False
                        self.PlayVideoInstance.key_mute_flag = True if self.PlayVideoInstance.vid.muted is True else False

                    else:
                        self.PlayVideoInstance.key_mute_flag = not self.PlayVideoInstance.key_mute_flag
                        self.PlayVideoInstance.vid.mute() if self.PlayVideoInstance.key_mute_flag is True else self.PlayVideoInstance.vid.unmute()

                    self.PlayVideoInstance.videoPlayBar.muted =  self.PlayVideoInstance.key_mute_flag

                    '''
                    self.PlayVideoInstance.vid.toggle_mute()
                    self.PlayVideoInstance.muted = self.PlayVideoInstance.vid.muted
                    self.PlayVideoInstance.videoPlayBar.muted = self.PlayVideoInstance.muted
                    print(f"toggle_mute() mute is now: {('True' if self.PlayVideoInstance.muted else 'False')}")
                    '''

                elif name == 'plusIcon':
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
                            # Seek to the last frame played prior to changing the playback speed
                            self.PlayVideoInstance.vid.seek_frame(currFrame)
                            # Update vid internals
                            self.PlayVideoInstance.vid.update()

                        except Exception as e:
                            pass

                elif name == "minusIcon":
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
                            # Seek to the last frame played prior to changing the playback speed
                            self.PlayVideoInstance.vid.seek_frame(currFrame)
                            # Update vid internals
                            self.PlayVideoInstance.vid.update()

                        except Exception as e:
                            pass

                elif name == 'repeatIcon':
                    self.PlayVideoInstance.opts.loop_flag = not self.PlayVideoInstance.opts.loop_flag
                    self.PlayVideoInstance.videoPlayBar.loop_flag = self.PlayVideoInstance.opts.loop_flag

                print(f"{name} icon clicked!")

    def videoPlayBarIconHover(self, event, mouse_x, mouse_y):
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
