#   DrawFilterHelpInfo.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Pygame Filter Help Window class

import pygame
import upScale as up_scale
import help_filter_text as _help_filter_

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DODGERBLUE = (30, 144, 255)
DODGERBLUE4 = (16, 78, 139)
HEADING_COLOR = (255, 200, 0)  # Yellow for headings
FALSE_COLOR = HEADING_COLOR
TRUE_COLOR = (50, 200, 0)
TEXT_COLOR = WHITE

class DrawFilterHelpInfo:
    """
    Manages the display and interactivity of a filter help overlay.

    This class manages the rendering and behavior of a help overlay that provides information
    about filters. It includes text rendering, scaling for display dimensions, and interactivity
    for visibility toggling and hover effects. The overlay scales its components, including fonts,
    icons, and boxes, based on the current display resolution.

    Attributes:
    display : The primary display surface used for rendering.
    display_width : The width of the display surface in pixels.
    display_height : The height of the display surface in pixels.
    resolution : A tuple containing the width and height of the display.
    displayType : The type of display configuration based on resolution.
    USER_HOME : The user's home directory path.
    FONT_DIR : The directory path to fonts used for rendering.
    RESOURCES_DIR : The directory path to resource files, such as images.
    w_mult : A multiplier for width scaling based on the display type.
    h_mult : A multiplier for height scaling based on the display type.
    BOX_WIDTH : The width of the help overlay box in pixels, scaled based on resolution.
    BOX_HEIGHT : The height of the help overlay box in pixels, scaled based on resolution.
    BOX_X : The x-coordinate of the top-left corner of the help overlay box.
    BOX_Y : The y-coordinate of the top-left corner of the help overlay box.
    font_help_text : A pygame.Font instance for the text used in the help overlay.
    font_help_heading : A pygame.Font instance for the heading text used in the help overlay.
    font_button : A pygame.Font instance for the button text used in the help overlay.
    check_icon : A pygame.Surface instance containing the checkmark icon for the button.
    y_offset_heading : Vertical offset for headings in the help overlay, scaled based on resolution.
    y_offset_text : Vertical offset for regular text in the help overlay, scaled based on resolution.
    filter_help_button_rect : A pygame.Rect defining the bounds of the "OK" button in the help overlay.
    filter_help_visible : A boolean indicating whether the help overlay is currently visible.
    is_hovered : A boolean indicating whether the mouse is currently over the "OK" button.

    Methods:
    is_visible():
        Checks if the filter help overlay is currently visible.

    toggle_visibility():
        Toggles the visibility state of the filter help overlay.

    set_visibility(visible: bool):
        Sets the visibility state of the filter help overlay.

    draw_filter_help(is_hovered: bool):
        Renders the filter help overlay and returns the rectangle of the "OK" button.

    draw_filter_help_overlay(is_hovered: bool):
        Renders the help overlay's background and content, including gradients, text, headings,
        icons, and the "OK" button. Returns the rectangle of the "OK" button.

    apply_gradient(surface: pygame.Surface, color_start: tuple[int, int, int],
        color_end: tuple[int, int, int], width: int, height: int, alpha_start: int,
        alpha_end: int):
        Static method for applying a vertical gradient to a surface.
    """
    def __init__(self, play_video):
        """
        Initializes and configures display settings, font scaling, and resource
        loading for a given display. The configuration allows adapting the
        application’s interfaces and elements to fit different resolutions
        and display types. It also supports resource scaling and dynamic
        positioning.

        Attributes:
            display: Display surface used for rendering graphics.
            display_width: Width of the display in pixels.
            display_height: Height of the display in pixels.
            resolution: Tuple containing the display width and height.
            displayType: Type of the display, derived from its resolution.
            play_video: Reference to an optional PlayVideo instance, if provided.
            USER_HOME: Home directory path of the user.
            FONT_DIR: Directory path used for storing font resources.
            RESOURCES_DIR: Directory path used for storing other resources.
            font_help_text: Scaled font object for displaying help text.
            font_help_heading: Scaled font object for displaying help headings.
            font_button: Scaled font object for displaying button text.
            check_icon: Scaled checkmark icon image.
            BOX_WIDTH: Width of a box element, adjusted for display scaling.
            BOX_HEIGHT: Height of a box element, adjusted for display scaling.
            BOX_X: X-coordinate of the top-left corner of the box.
            BOX_Y: Y-coordinate of the top-left corner of the box.
            w_mult: Width multiplier for scaling elements according to display type.
            h_mult: Height multiplier for scaling elements according to display type.
            y_offset_heading: Vertical offset for headings, based on scaled font height.
            y_offset_text: Vertical offset for text, based on scaled font height.
        """
        self.play_video = play_video
        #
        self.display = self.play_video.win
        self.display_width = self.display.get_width()
        self.display_height = self.display.get_height()
        self.resolution = self.display_width, self.display_height
        self.displayType = up_scale.get_display_type(self.resolution)

        self.USER_HOME = self.play_video.USER_HOME
        self.FONT_DIR = self.play_video.FONT_DIR
        self.RESOURCES_DIR = self.play_video.RESOURCES_DIR

        # Scale fonts
        originalFontSizes = [18, 17, 24]
        scaled_font_size = up_scale.get_scaled_fonts(originalFontSizes, self.display_height)
        self.font_help_text = pygame.font.Font(self.FONT_DIR + 'Arial.ttf', scaled_font_size[0])
        self.font_help_heading = pygame.font.Font(self.FONT_DIR + 'Arial_Bold.ttf', scaled_font_size[1])
        self.font_button = pygame.font.Font(self.FONT_DIR + 'Montserrat-Bold.ttf', scaled_font_size[2])

        self.check_icon = pygame.image.load(self.RESOURCES_DIR + 'checkmark.png').convert_alpha()
        self.check_icon = pygame.transform.scale(self.check_icon, (32, 32))

        # Scale box dimensions using display type multipliers
        baseBoxWidth = 600
        baseBoxHeight = 600
        self.w_mult, self.h_mult = up_scale.resolution_multipliers[self.displayType]
        self.BOX_WIDTH = int(baseBoxWidth * self.w_mult)
        self.BOX_HEIGHT = int(baseBoxHeight * self.h_mult)
        self.BOX_X = (self.display_width - self.BOX_WIDTH) // 2
        self.BOX_Y = (self.display_height - self.BOX_HEIGHT) // 2

        self.y_offset_heading = int(self.font_help_heading.get_height() * (self.h_mult + 0.1))
        self.y_offset_text = int(self.font_help_text.get_height() * (self.h_mult - 0.6))

        self.filter_help_button_rect = None
        self.filter_help_visible = False
        self.is_hovered = False

    def is_visible(self):
        return self.filter_help_visible

    def toggle_visibility(self):
        self.filter_help_visible = not self.filter_help_visible
        self.play_video.filter_help_visible = self.filter_help_visible

    def set_visibility(self, visible):
        self.filter_help_visible = visible
        self.play_video.filter_help_visible = self.filter_help_visible

    def draw_filter_help(self, is_hovered):
        self.is_hovered = is_hovered
        self.set_visibility(True)
        self.filter_help_button_rect =  self.draw_filter_help_overlay(is_hovered)
        return self.filter_help_button_rect

    def draw_filter_help_overlay(self, is_hovered):
        self.is_hovered = is_hovered
        if not self.filter_help_visible:
            return
        # Create and draw the gradient background
        gradient_surface = pygame.Surface((self.BOX_WIDTH, self.BOX_HEIGHT), pygame.SRCALPHA)
        gradient_surface.set_colorkey((0, 255, 0))
        DrawFilterHelpInfo.apply_gradient(
            gradient_surface,
            (0, 0, 255),
            (0, 0, 100),
            self.BOX_WIDTH,
            self.BOX_HEIGHT,
            alpha_start=100,
            alpha_end=200
        )

        pygame.draw.rect(
            self.display,
            DODGERBLUE,
            (self.BOX_X, self.BOX_Y, self.BOX_WIDTH, self.BOX_HEIGHT),
            4,
            border_radius=8
        )
        y_constant_start = 20 / self.BOX_HEIGHT
        y_constant_end = round((0.875 /self.h_mult), 3)
        # Draw a vertical separator line (this will always be drawn)
        pygame.draw.line(
            gradient_surface,
            WHITE,
            (self.BOX_WIDTH // 2, int(self.BOX_HEIGHT * y_constant_start)),
            (self.BOX_WIDTH // 2, int(self.BOX_HEIGHT * self.h_mult * y_constant_end)),
            2
        )

        pygame.draw.rect(
            self.display,
            DODGERBLUE,
            (self.BOX_X, self.BOX_Y, self.BOX_WIDTH, self.BOX_HEIGHT),
            4,
            border_radius=8
        )
        # The rest of the drawing code remains the same until button dimensions...
        LEFT_MARGIN = int(self.BOX_WIDTH * 0.05)     # 5% of box width
        RIGHT_COLUMN_X = int(self.BOX_WIDTH * 0.55)  # Slightly right of center line

        # Render left column text
        y_start = 25
        line_offset = self.font_help_text.get_height() + 5
        y_offset = y_start
        for line in _help_filter_.HELP_TEXT_LEFT.split("\n"):
            color = HEADING_COLOR if line.isupper() else TEXT_COLOR
            text_surface = (
                self.font_help_text.render(line.strip(), True, color)) \
                if not line.isupper() \
                else \
                self.font_help_heading.render(line.strip() ,True, color)

            gradient_surface.blit(text_surface, (LEFT_MARGIN, y_offset))    # left column
            if line.isupper():
                text_width, _ = self.font_help_heading.size(line.strip())
                pygame.draw.aaline(
                    gradient_surface,
                    HEADING_COLOR,
                    (LEFT_MARGIN, y_offset + line_offset),
                    (LEFT_MARGIN + text_width, y_offset + line_offset)
                )
                y_offset += self.y_offset_heading
            else:
                y_offset += self.y_offset_text

        # Render right column text
        y_offset = y_start
        for line in _help_filter_.HELP_TEXT_RIGHT.split("\n"):
            color = HEADING_COLOR if line.isupper() else TEXT_COLOR
            text_surface = (
                self.font_help_text.render(line.strip(), True, color)) \
                if not line.isupper() \
                else self.font_help_heading.render(line.strip(), True, color)

            gradient_surface.blit(text_surface, (RIGHT_COLUMN_X, y_offset))       # Right column
            if line.isupper():
                text_width, _ = self.font_help_heading.size(line.strip())
                pygame.draw.aaline(
                    gradient_surface,
                    HEADING_COLOR,
                    (RIGHT_COLUMN_X, y_offset + line_offset),
                    (RIGHT_COLUMN_X + text_width, y_offset + line_offset)
                )
                y_offset += self.y_offset_heading
            else:
                y_offset += self.y_offset_text

        self.display.blit(gradient_surface, (self.BOX_X, self.BOX_Y))

        # Scale button dimensions
        buttonWidthBase = 120
        buttonHeightBase = 40
        button_width = int(buttonWidthBase * self.w_mult)
        button_height = int(buttonHeightBase * self.h_mult)

        # Scale button position
        button_x = self.BOX_X + self.BOX_WIDTH // 2 - button_width // 2
        button_y = self.BOX_Y + self.BOX_HEIGHT - int(61 * self.h_mult)  # Scale the offset too
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # Draw the OK button with the hover effect
        button_color = DODGERBLUE if is_hovered else DODGERBLUE4
        pygame.draw.rect(self.display, button_color, button_rect, border_radius=8)
        pygame.draw.rect(self.display, BLACK, button_rect, 1, border_radius=8)

        # Scale icon position
        icon_x_offset = int(20 * self.w_mult)
        icon_y_offset = int(9 * self.h_mult)
        text_x_offset = int(45 * self.w_mult)
        text_y_offset = int(4 * self.h_mult)

        # Draw check icon and button text
        self.display.blit(self.check_icon, (button_x + icon_x_offset, button_y + icon_y_offset))
        ok_surface = self.font_button.render("OK", True, HEADING_COLOR if is_hovered else WHITE)
        self.display.blit(ok_surface, (button_x + text_x_offset, button_y + text_y_offset))

        self.filter_help_button_rect = button_rect
        return button_rect

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