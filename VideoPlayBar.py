#   VideoPlayBar.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Video play bar class
#
import pygame

class VideoPlayBar:
    def __init__(self, DISPLAY,USER_HOME):
        self.display = DISPLAY
        self.barWidth = self.display.get_width()
        self.barHeight = 62
        self.IconHeight = 48
        self.IconWidth = 48
        self.IconYcord = (self.barHeight - self.IconHeight) / 2  #  IconYcord is 7
        self.IconSpacing = 15

        self.MOUSE_X = 0
        self.MOUSE_Y = 0
        self.mouseEventFlag = False

        # x, y coordinates of where to put the play bar
        # coordinates start at (0, 1135)
        self.barRow = 0
        self.barColumn =  self.display.get_height() - self.barHeight

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
        self.stopIcon = pygame.image.load(self.RESOURCES_DIR + "stop.png").convert_alpha()
        self.previousIcon = pygame.image.load(self.RESOURCES_DIR + "previous.png").convert_alpha()
        self.nextIcon = pygame.image.load(self.RESOURCES_DIR + "next.png").convert_alpha()
        self.plusIcon = pygame.image.load(self.RESOURCES_DIR + "plus.png").convert_alpha()
        self.minusIcon = pygame.image.load(self.RESOURCES_DIR + "minus.png").convert_alpha()
        self.repeatIcon = pygame.image.load(self.RESOURCES_DIR + "repeat.png").convert_alpha()
        self.speakerIcon = pygame.image.load(self.RESOURCES_DIR + "volume.png").convert_alpha()

        self.pauseIcon = pygame.image.load(self.RESOURCES_DIR + "pause.png").convert_alpha()
        self.forwardIcon = pygame.image.load(self.RESOURCES_DIR + "forward10s.png").convert_alpha()
        self.rewindIcon = pygame.image.load(self.RESOURCES_DIR + "rewind10s.png").convert_alpha()
        self.muteIcon = pygame.image.load(self.RESOURCES_DIR + "mute.png").convert_alpha()

        self.IconList = [
                         self.playIcon,
                         self.stopIcon,
                         self.previousIcon,
                         self.nextIcon,
                         self.plusIcon,
                         self.minusIcon,
                         self.repeatIcon,
                         self.speakerIcon
                         ]

        self.barSurface = None
        self.barRect = None
        self.volumeRect = None
        self.volumeLevel = 0.0

    def drawVideoPlayBar(self):
        DodgerBlue = pygame.color.THECOLORS['dodgerblue']
        barBorderColor = (0, 0, 0)
        barColor = DodgerBlue
        color_start = (0, 120, 255)  # DodgerBlue
        color_end = (0, 50, 150)  # Darker Blue

        self.barSurface = pygame.Surface((self.barWidth, self.barHeight), pygame.SRCALPHA)
        self.barSurface.set_alpha(175)
        self.barSurface.set_colorkey((0, 255, 0))
        #self.barSurface.fill(barColor)  # Semi-transparent background
        #VideoPlayBar.apply_gradient(self.barSurface, color_start, color_end, self.barWidth, self.barHeight)
        VideoPlayBar.apply_gradient(self.barSurface, (0, 120, 255), (0, 50, 150), self.barWidth, self.barHeight)
        self.barRect = self.barSurface.get_rect()
        pygame.draw.rect(self.barSurface, barBorderColor, (0, 0, self.barWidth, self.barHeight), 1)
        self.placeIcons()
        self.display.blit(self.barSurface, (self.barRow, self.barColumn))

    def placeIcons(self):
        spacing = 15
        #mouse_x, mouse_y = pygame.mouse.get_pos()
        #print(f"self.MOUSE_X: {self.MOUSE_X}, self.MOUSE_Y: {self.MOUSE_Y}")
        for icon in self.IconList:
            # Default placement for most icons
            x_pos = spacing
            if icon == self.speakerIcon:
                x_pos = self.barWidth - 135  # Ensure correct placement for speaker

            rect = icon.get_rect(topleft=(x_pos, self.IconYcord))  # Ensure rect position

                # Apply hover effect if needed
            if rect.collidepoint(self.MOUSE_X, self.MOUSE_Y):
                print("transformed_icon")
                transformed_icon = pygame.transform.smoothscale(icon, (56, 56))  # Slightly larger
                self.barSurface.blit(transformed_icon, (rect.x - 4, rect.y - 4))
                #self.display.update(rect.x -4, rect.y -4)
            else:
               self.barSurface.blit(icon, (rect.x, rect.y))

            #self.barSurface.blit(icon, (rect.x, rect.y))

            spacing += (15 + self.IconWidth) if icon != self.speakerIcon else 0  # Prevent unwanted shifting

        self.drawVolumeBar()
        self.drawVolumeKnob()

    @staticmethod
    def apply_gradient(surface, color_start, color_end, width, height, alpha_start=50, alpha_end=200):
        for y in range(height):
            ratio = y / height
            new_color = (
                int(color_start[0] * (1 - ratio) + color_end[0] * ratio),  # Red
                int(color_start[1] * (1 - ratio) + color_end[1] * ratio),  # Green
                int(color_start[2] * (1 - ratio) + color_end[2] * ratio),  # Blue
                int(alpha_start * (1 - ratio) + alpha_end * ratio)  # Alpha blending
            )
            pygame.draw.line(surface, new_color, (0, y), (width, y))


    def drawVolumeBar(self):
        volumeBarX = self.barWidth - 135 + self.IconWidth + 10  # Shift right of speaker icon
        volumeBarWidth = (self.barWidth - 10) - volumeBarX  # Extend to 10 pixels from the right edge
        volumeBarHeight = 10   # Thin slider for aesthetics
        volumeBarY = self.IconYcord + (self.IconHeight // 2) - (volumeBarHeight // 2)  # Center vertically

        self.volumeRect = pygame.Rect(volumeBarX, volumeBarY, volumeBarWidth, volumeBarHeight)
        #print(f"self.volumeRect: {self.volumeRect}")
        pygame.draw.rect(self.barSurface, (200, 200, 200), self.volumeRect)  # Light gray slider

    def drawVolumeKnob(self):
        knob_radius = 6
        knob_x = self.volumeRect.x + int(self.volumeLevel / 100 * self.volumeRect.width)
        knob_y = self.volumeRect.y + self.volumeRect.height // 2

        pygame.draw.circle(self.barSurface, (255, 255, 255), (knob_x, knob_y), knob_radius)  # White knob
