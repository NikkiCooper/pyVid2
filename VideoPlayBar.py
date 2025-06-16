#   VideoPlayBar.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Video play bar class
#
import pygame
import upScale as up_scale

DODGERBLUE = (30, 144, 255)
DODGERBLUE4 = (16, 78, 139)

class VideoPlayBar:
    """
    Represents the playback bar for a video player application.

    This class is responsible for handling the visual display and interactions with
    the video player's playback bar, including controls such as play, pause, volume
    adjustment, and navigation within the video. It leverages pygame for rendering
    and interacts with resolution scaling utilities to ensure compatibility across
    different screen sizes.

    Attributes:
        loop_flag: Indicates whether the video is in playback loop mode.
        volume: The current volume level of the video playback.
        muted: Whether the video playback is muted.
        playbackSpeed: The current playback speed of the video.
        vid_paused: A boolean indicating whether the video is paused.
        vid_duration: The total duration of the video (in seconds or an appropriate time unit).
        vid_curpos: Current position in the video playback timeline.
        display: The display surface where the playback bar will be rendered.
        barWidth: The width of the playback bar, derived from the display dimensions.
        barHeightBase: Base height value of the playback bar for scaling operations.
        IconHeightBase: Base height of the control icons.
        IconWidthBase: Base width of the control icons.
        displayWidth: The width of the display surface.
        displayHeight: The height of the display surface.
        resolution: Tuple containing the display's width and height.
        displayType: The type of display configuration, based on resolution scaling.
        barHeight: The scaled height of the playback bar.
        icon_scaled_width: The scaled width of icons based on display resolution.
        icon_scaled_height: The scaled height of icons based on display resolution.
        IconHeight: Final scaled icon height.
        IconWidth: Final scaled icon width.
        IconYcord: Vertical coordinate reference for icon placement on the bar.
        barHeight_Offset: Offset value for positioning the bar at the bottom of the display.
        width_multiplier: Multiplier for scaling widths based on resolution.
        height_multiplier: Multiplier for scaling heights based on resolution.
        IconSpacing: Spacing value between icons in the playback bar.
        bar_top: Vertical offset for the top boundary of the playback bar.
        MOUSE_X: Horizontal position of the mouse cursor.
        MOUSE_Y: Vertical position of the mouse cursor.
        ttx: Tooltip X-coordinate.
        tty: Tooltip Y-coordinate.
        drawToolTipFlag: Flag indicating whether to draw a tooltip.
        mouseEventFlag: Flag for ongoing mouse interactions with the bar.
        text: Text content displayed within the tooltip.
        barRow: Row position of the playback bar.
        barColumn: Column position of the playback bar.
        USER_HOME: User's home directory path.
        FONT_DIR: Path to the directory containing font resources.
        font_italic_18: Italic font with size 18.
        font_bold_italic_18: Bold italic font with size 18.
        font_regular_18: Regular font with size 18.
        font_bold_regular_18: Bold font with size 18.
        font_regular_28: Regular font with size 28.
        font_regular_32: Regular font with size 32.
        font_regular_36: Regular font with size 36.
        RESOURCES_DIR: Path to the directory containing icon resource files.
        playIcon: Surface object representing the play icon.
        stopIcon: Surface object representing the stop icon.
        previousIcon: Surface object representing the previous icon.
        nextIcon: Surface object representing the next icon.
        plusIcon: Surface object representing the volume-increase icon.
        minusIcon: Surface object representing the volume-decrease icon.
        repeatIcon: Surface object representing the loop mode icon when inactive.
        speakerIcon: Surface object representing the active volume speaker icon.
        pauseIcon: Surface object representing the pause icon.
        forwardIcon: Surface object for the 10-second forward navigation icon.
        rewindIcon: Surface object for the 10-second backward navigation icon.
        repeatWhiteIcon: Surface object for the loop mode icon when active.
        muteIcon: Surface object representing the mute icon.
        IconList: List of all icons used in the playback bar.
        IconRects: Dictionary pairing icon names to their respective Rect objects.
        IconNames: Predefined list of icon variable names used in the playback bar.
        speakerRect: Rect object representing the bounds of the speaker icon.
        barSurface: Surface object representing the playback bar.
        barRect: Rect object for the bounds of the playback bar.
        volumeRect: Rect object representing the bounds of the volume slider.
        volumeLevel: The current volume level based on user interaction.
        local_mouse: Tuple for storing mouse position relative to the playback bar.
    """
    def __init__(self, DISPLAY, USER_HOME, loop_flag, volume, muted, playbackSpeed, vid_paused, vid_duration, vid_curpos):
        """
        Initializes an instance of a class responsible for managing the graphical and interactive components of a media player,
        including display scaling, resource loading, and user interaction handling.

        Attributes:
            loop_flag (bool): Playback loop flag to indicate whether the video should loop.
            volume (int): Current volume level of the media player.
            muted (bool): Mute state of the media player.
            playbackSpeed (float): Speed at which the video is playing.
            vid_paused (bool): Indicates whether the video is paused.
            vid_duration (float): Total duration of the video.
            vid_curpos (float): Current position in the video.
            display (pygame.Surface): The display surface where graphical components are rendered.
            barWidth (int): Width of the bar representing the media controls.
            barHeightBase (int): Base height for the media control bar.
            IconHeightBase (int): Base height for the control icons.
            IconWidthBase (int): Base width for the control icons.
            displayWidth (int): Width of the display surface.
            displayHeight (int): Height of the display surface.
            resolution (tuple[int, int]): Resolution of the display surface as (width, height).
            displayType (str): Type of display resolution category.
            barHeight (int): Scaled height of the media bar after adjustments.
            icon_scaled_width (int): Scaled width for icons based on display height.
            icon_scaled_height (int): Scaled height for icons based on display height.
            IconHeight (int): Scaled height of icons for UI elements.
            IconWidth (int): Scaled width of icons for UI elements.
            IconYcord (float): Vertical offset for positioning the icons within the bar.
            barHeight_Offset (float): Vertical offset for positioning the bar within the display.
            width_multiplier (float): Scaling multiplier for width adjustments.
            height_multiplier (float): Scaling multiplier for height adjustments.
            IconSpacing (int): Spacing between icons in the media control bar.
            bar_top (int): Top position of the media control bar.
            MOUSE_X (int): X-coordinate of the mouse pointer for interaction tracking.
            MOUSE_Y (int): Y-coordinate of the mouse pointer for interaction tracking.
            ttx (int): Tooltip x-coordinate.
            tty (int): Tooltip y-coordinate.
            drawToolTipFlag (bool): Flag indicating whether to draw a tooltip.
            mouseEventFlag (bool): Flag for tracking mouse events.
            text (str): Text related to tooltip or specific UI elements.
            barRow (int): Row-coordinate for placing the control bar in the display.
            barColumn (int): Column-coordinate for placing the control bar in the display.
            USER_HOME (str): Home directory of the current user.
            FONT_DIR (str): Directory location for font resources.
            font_italic_18 (pygame.font.Font): Font resource with size 18 and italic style.
            font_bold_italic_18 (pygame.font.Font): Font resource with size 18, bold and italic style.
            font_regular_18 (pygame.font.Font): Font resource with size 18 and regular style.
            font_bold_regular_18 (pygame.font.Font): Font resource with size 18, bold and regular style.
            font_regular_28 (pygame.font.Font): Font resource with size 28 and regular style.
            font_regular_32 (pygame.font.Font): Font resource with size 32 and regular style.
            font_regular_36 (pygame.font.Font): Font resource with size 36 and regular style.
            RESOURCES_DIR (str): Directory folder location for resource files such as icons.
            playIcon (pygame.Surface): Play button icon resource.
            stopIcon (pygame.Surface): Stop button icon resource.
            previousIcon (pygame.Surface): Previous button icon resource.
            nextIcon (pygame.Surface): Next button icon resource.
            plusIcon (pygame.Surface): Plus button/icon to increase volume.
            minusIcon (pygame.Surface): Minus button/icon to decrease volume.
            repeatIcon (pygame.Surface): Repeat button/icon for toggling looping playback.
            speakerIcon (pygame.Surface): Speaker icon for sound-related UI.
            pauseIcon (pygame.Surface): Pause button/icon resource.
            forwardIcon (pygame.Surface): Forward button/icon skipping the video forward by 10s.
            rewindIcon (pygame.Surface): Rewind button/icon skipping the video backward by 10s.
            repeatWhiteIcon (pygame.Surface): Alternate repeat icon with a white theme.
            muteIcon (pygame.Surface): Mute button/icon resource.
            IconList (list): List containing all loaded icon resources for UI.
            IconRects (dict): Dictionary for storing the rectangular coordinates of icons in UI.
            IconNames (list): List of icon names associated with media controls.
            speakerRect (pygame.Rect or None): Rectangle for the speaker icon.
            barSurface (pygame.Surface or None): Surface object for rendering the media bar.
            barRect (pygame.Rect or None): Rectangle for defining the media bar's position.
            volumeRect (pygame.Rect or None): Rectangle representing the volume bar.
            volumeLevel (int): Current volume level of the media bar.
            local_mouse (tuple[int, int] or None): Local mouse coordinates for interaction tracking or None.
        """
        self.loop_flag = loop_flag
        self.volume = volume
        self.muted = muted
        self.playbackSpeed = playbackSpeed
        self.vid_paused = vid_paused
        self.vid_duration = vid_duration
        self.vid_curpos = vid_curpos
        self.display = DISPLAY
        self.barWidth = self.display.get_width()
        self.barHeightBase =  62
        self.IconHeightBase = 48
        self.IconWidthBase =  48

        self.displayWidth = self.display.get_width()
        self.displayHeight = self.display.get_height()
        self.resolution = self.displayWidth, self.displayHeight
        # Scaling
        self.displayType = up_scale.get_display_type(self.resolution)
        x_multi, y_multi = up_scale.scale_resolution(self.displayType) \
            if self.displayType in up_scale.resolution_multipliers else (1, 1)
        self.barHeight = int(y_multi * self.barHeightBase)

        self.icon_scaled_width = up_scale.scale_font(self.IconWidthBase, self.displayHeight)
        self.icon_scaled_height = self.icon_scaled_width
        self.IconHeight = self.icon_scaled_height
        self.IconWidth = self.icon_scaled_width
        self.IconYcord = (self.barHeight - self.icon_scaled_height) / 2  # IconYcord is 7
        self.barHeight_Offset = (self.displayHeight - self.barHeight + self.IconYcord)

        self.width_multiplier = x_multi
        self.height_multiplier = y_multi
        self.IconSpacing = 15

        self.bar_top = 0

        self.MOUSE_X = 0
        self.MOUSE_Y = 0
        self.ttx = 0
        self.tty = 0
        self.drawToolTipFlag = False
        self.mouseEventFlag = False
        self.text = ""

        # x, y coordinates of where to put the play bar
        # coordinates start at (0, 1138)
        self.barRow = 0
        self.barColumn =  self.displayHeight - self.barHeight

        self.USER_HOME = USER_HOME
        # Fonts location
        self.FONT_DIR = self.USER_HOME + "/.local/share/pyVid/fonts/"
        # Fonts
        self.font_italic_18 = pygame.font.Font(self.FONT_DIR + 'RobotoCondensed-Italic.ttf', 18)
        self.font_bold_italic_18 = pygame.font.Font(self.FONT_DIR + 'Roboto-BoldItalic.ttf', 18)
        self.font_regular_18 = pygame.font.Font(self.FONT_DIR + 'RobotoCondensed-Regular.ttf', 18)
        self.font_bold_regular_18 = pygame.font.Font( self.FONT_DIR + 'Roboto-Bold.ttf', 18)
        self.font_regular_28 = pygame.font.Font(self.FONT_DIR + 'RobotoCondensed-Regular.ttf', 28)
        self.font_regular_32 = pygame.font.Font( self.FONT_DIR + 'RobotoCondensed-Regular.ttf', 32)
        self.font_regular_36 = pygame.font.Font( self.FONT_DIR + 'RobotoCondensed-Regular.ttf', 36)

        # Resources location
        self.RESOURCES_DIR = self.USER_HOME + "/.local/share/pyVid/Resources/"
        # Icons.  All icons are 48x48 with transparent backgrounds
        self.playIcon = pygame.image.load(self.RESOURCES_DIR + "play.png").convert_alpha()
        self.stopIcon = pygame.image.load(self.RESOURCES_DIR + "exit.png").convert_alpha()
        self.previousIcon = pygame.image.load(self.RESOURCES_DIR + "previous.png").convert_alpha()
        self.nextIcon = pygame.image.load(self.RESOURCES_DIR + "next.png").convert_alpha()
        self.plusIcon = pygame.image.load(self.RESOURCES_DIR + "plus.png").convert_alpha()
        self.minusIcon = pygame.image.load(self.RESOURCES_DIR + "minus.png").convert_alpha()
        self.repeatIcon = pygame.image.load(self.RESOURCES_DIR + "repeat.png").convert_alpha()
        self.screenShotIcon = pygame.image.load(self.RESOURCES_DIR + "screenshots.png").convert_alpha()
        self.speakerIcon = pygame.image.load(self.RESOURCES_DIR + "volume.png").convert_alpha()

        self.pauseIcon = pygame.image.load(self.RESOURCES_DIR + "pause.png").convert_alpha()
        self.forwardIcon = pygame.image.load(self.RESOURCES_DIR + "forward10s.png").convert_alpha()
        self.rewindIcon = pygame.image.load(self.RESOURCES_DIR + "rewind10s.png").convert_alpha()
        self.repeatWhiteIcon = pygame.image.load(self.RESOURCES_DIR + "repeat_white.png").convert_alpha()
        self.muteIcon = pygame.image.load(self.RESOURCES_DIR + "mute.png").convert_alpha()

        self.IconList = []
        self.IconRects = {}
        self.IconNames = [
            "playIcon", "stopIcon", "previousIcon", "nextIcon",
            "plusIcon", "minusIcon", "repeatIcon", "screenShotIcon", "speakerIcon"
        ]

        self.speakerRect = None
        self.barSurface = None
        self.barRect = None
        self.volumeRect = None
        self.volumeLevel = self.volume

        self.local_mouse = None

    def placeIcons(self):
        """
        Places and displays interactive icons on a user interface bar, including
        media control buttons and a speaker mute/unmute icon. Icons are scaled
        appropriately based on the current display resolution, and hover effects
        are applied when the mouse cursor is positioned over an icon. The method
        also maintains updated information about the positioning and bounding
        rectangles of each icon for user interaction.

        Parameters:
            None

        Returns:
            None
        """
        # ─── 1) get your multipliers & sizing ────────────────────────────────
        disp_type = up_scale.get_display_type((self.displayWidth, self.displayHeight))
        width_mul, _ = up_scale.scale_resolution(disp_type) \
            if disp_type in up_scale.resolution_multipliers else (1, 1)
        icon_sz = int(48 * width_mul)
        hov_sz = int(56 * width_mul)
        spacing = max(4, int(icon_sz * 0.25))
        y = int(self.IconYcord)
        # ─── 2) build & draw your non-speaker icons ──────────────────────────
        buttons = [
            ("playIcon", self.playIcon if not self.vid_paused else self.pauseIcon),
            ("stopIcon", self.stopIcon),
            ("previousIcon", self.previousIcon),
            ("nextIcon", self.nextIcon),
            ("plusIcon", self.plusIcon),
            ("minusIcon", self.minusIcon),
            ("repeatIcon", self.repeatIcon if not self.loop_flag else self.repeatWhiteIcon),
            ("screenShotIcon", self.screenShotIcon),
        ]
        x = spacing
        mx, my = pygame.mouse.get_pos()
        bar_top = self.displayHeight - self.barHeight
        self.bar_top = bar_top
        local_mouse = (mx, my - bar_top)
        for name, surf in buttons:
            scaled = pygame.transform.smoothscale(surf, (icon_sz, icon_sz))
            rect = scaled.get_rect(topleft=(x, y))
            self.IconRects[name] = rect
            if rect.collidepoint(*local_mouse):
                hov = pygame.transform.smoothscale(surf, (hov_sz, hov_sz))
                off_x = (hov.get_width() - rect.w) // 2
                off_y = (hov.get_height() - rect.h) // 2
                self.barSurface.blit(hov, (rect.x - off_x, rect.y - off_y))
            else:
                self.barSurface.blit(scaled, rect.topleft)
            x += icon_sz + spacing
        # ─── 3) draw & stash the speaker icon ─────────────────────────────────
        sp_surf = self.speakerIcon if not self.muted else self.muteIcon
        scaled_sp = pygame.transform.smoothscale(sp_surf, (icon_sz, icon_sz))
        # pin it at the far right, with one ‘spacing’ margin
        x = self.barWidth - spacing - icon_sz
        # Had to set this to x-125 to get the speaker icon over to the left so the volume slider could appear.
        rect = scaled_sp.get_rect(topleft=(x-125, y))
        #rect = scaled_sp.get_rect(topleft=(x, y))
        self.IconRects["speakerIcon"] = rect
        self.barSurface.blit(scaled_sp, rect.topleft)
        # optional: hover on speaker
        if rect.collidepoint(*local_mouse):
            hov = pygame.transform.smoothscale(sp_surf, (hov_sz, hov_sz))
            off_x = (hov.get_width() - rect.w) // 2
            off_y = (hov.get_height() - rect.h) // 2
            self.barSurface.blit(hov, (rect.x - off_x, rect.y - off_y))

    def drawVideoPlayBar(self):
        """
        Draws and renders a video play bar on the display surface. The method manages
        various components required for visualizing the play bar, including the gradient
        background, volume controls, and overall bar structure. It ensures proper layering
        and blending by utilizing surfaces, color keys, and blending options.

        Raises
        ------
        No explicit exceptions are raised. Error handling depends on external calls
        and pygame library methods.
        """
        # ─── A) build the barSurface ────────────────────────────────────────────
        self.barSurface = pygame.Surface((self.barWidth, self.barHeight), pygame.SRCALPHA)
        self.barSurface.set_alpha(175)
        self.barSurface.set_colorkey((0, 255, 0))
        VideoPlayBar.apply_gradient(
            self.barSurface, (0, 0, 255), (0, 0, 100),
            self.barWidth, self.barHeight,
            alpha_start=80, alpha_end=180
        )
        self.barRect = self.barSurface.get_rect()
        pygame.draw.rect(
            self.barSurface,
            pygame.color.THECOLORS['dodgerblue4'],
            (0, 0, self.barWidth, self.barHeight), 1
        )
        # ─── B) draw icons (including speakerIcon) ─────────────────────────────
        self.placeIcons()
        # ─── C) now it’s safe to draw the slider & knob ───────────────────────
        self.drawVolumeBar()
        self.drawVolumeKnob()
        # ─── D) blit to the main display ───────────────────────────────────────
        self.display.blit(self.barSurface, (self.barRow, self.barColumn))

    def print_IconRects(self):
        """
        Prints the names and rectangle definitions from the IconRects dictionary attribute.

        This method iterates over the items in the IconRects attribute, which is expected
        to be a dictionary. Each key-value pair, where the key is a name and the value is
        a rectangle definition, is printed to the console. After completing the iteration,
        an empty line is printed.

        Args:
            None

        Returns:
            None
        """
        for name, rect in self.IconRects.items():
            print(f"{name}, {rect}")
        print()

    @staticmethod
    def apply_gradient(surface, color_start, color_end, width, height, alpha_start=50, alpha_end=200):
        """
        Applies a vertical gradient color effect on the given surface object. The function uses a linear
        interpolation of the start and end colors and their alpha values to create a smooth transition
        from the top (color_start and alpha_start) to the bottom (color_end and alpha_end) over the
        specified height. This gradient is drawn line by line horizontally.

        Args:
            surface (pygame.Surface): The target surface on which the gradient will be applied.
            color_start (tuple[int, int, int]): RGB color tuple representing the start color of
                the gradient at the top (0, height).
            color_end (tuple[int, int, int]): RGB color tuple representing the end color of the
                gradient at the bottom (height, height).
            width (int): The width of the surface, or the region affected by the gradient.
            height (int): The height of the surface, or the region over which the gradient is created.
            alpha_start (int, optional): The starting alpha value for the gradient, defining the transparency
                of the top color. Default is 50.
            alpha_end (int, optional): The ending alpha value for the gradient, defining the transparency
                of the bottom color. Default is 200.

        Returns:
            None
        """
        for y in range(height):
            ratio = y / height
            new_color = (
                int(color_start[0] * (1 - ratio) + color_end[0] * ratio),   # Red
                int(color_start[1] * (1 - ratio) + color_end[1] * ratio),   # Green
                int(color_start[2] * (1 - ratio) + color_end[2] * ratio),   # Blue
                int(alpha_start * (1 - ratio) + alpha_end * ratio)          # Alpha blending
            )
            pygame.draw.line(surface, new_color, (0, y), (width, y))

    def drawVolumeBar(self):
        """
        Draws a volume bar on the surface provided in the `barSurface` attribute.

        The method calculates and creates a rectangle representing the volume bar
        based on the position of the speaker icon (`speakerIcon`) and other
        attributes of the class. It then draws the volume bar rectangle on the
        given surface.

        Attributes
        ----------
        volumeRect : pygame.Rect
            Represents the rectangle of the volume bar to be drawn on the surface.

        Parameters
        ----------
        self
            Represents the instance of the class.
        """
        sp = self.IconRects["speakerIcon"]
        spacing  = int(self.IconRects["speakerIcon"].width * 0.25)
        x = sp.right + spacing
        w = self.barWidth - spacing - x
        h = 10
        y = sp.centery - (h // 2)
        self.volumeRect = pygame.Rect(x, y, w, h)
        #print(f"self.volumeRect: {self.volumeRect}")

        pygame.draw.rect(self.barSurface, (200, 200, 200), self.volumeRect)

    def drawVolumeKnob(self):
        """
        Draws the volume knob on the volume control bar.

        This method creates a circular knob representing the current
        volume level. The position of the knob is calculated based on
        the volume level and the dimensions of the volume control area,
        and it is drawn onto the bar surface.

        Parameters:
            None

        Returns:
            None
        """
        knob_r = int(6 * self.width_multiplier)
        kx = self.volumeRect.x + int(self.volumeLevel/100 * self.volumeRect.width)
        ky = self.volumeRect.y + self.volumeRect.h//2
        pygame.draw.circle(self.barSurface, (255,255,255), (kx, ky), knob_r)

    # Tooltip function
    def draw_tooltip(self, text, x, y, alpha=150):
        """
        Renders a tooltip with provided text at a specific screen position. The tooltip
        has a semi-transparent background and slightly rounded corners for a visually
        appealing appearance.

        Attributes:
        - FONT_DIR (str): The directory path where fonts are stored, used to load the
          tooltip font.
        - display: The surface or screen onto which the tooltip will be drawn.

        Args:
            text (str): The text content to display in the tooltip.
            x (float): The x-coordinate on the display where the tooltip will be drawn.
            y (float): The y-coordinate on the display where the tooltip will be drawn.
            alpha (int, optional): The transparency value for the tooltip background,
                ranging from 0 (fully transparent) to 255 (fully opaque). Defaults to
                150.
        """
        BLACK = (0, 0, 0)
        tooltip_font = pygame.font.Font(self.FONT_DIR + "Montserrat-Regular.ttf", 18)
        tooltip_text_surface = tooltip_font.render(text, True, BLACK)
        tooltip_width, tooltip_height = tooltip_text_surface.get_size()
        # Create a transparent surface
        toolTipSurface = pygame.Surface((tooltip_width + 10, tooltip_height + 6), pygame.SRCALPHA)
        # Fill with semi-transparent background
        toolTipSurface.fill((50, 50, 50, alpha))  # Dark gray, semi-transparent
        # Draw rounded rectangle (border radius for smoother edges)
        pygame.draw.rect(toolTipSurface,
                         pygame.color.THECOLORS['green'],
                         (0, 0, tooltip_width + 10, tooltip_height + 6),
                         border_radius=5
        )
        # Blit text onto tooltip surface
        toolTipSurface.blit(tooltip_text_surface, (5, 3))
        # Blit tooltip onto display
        self.display.blit(toolTipSurface, (x, y))

