#   DrawHelpInfo.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Pygame Help window class

import pygame
import upScale as up_scale
import help_text as  _help_
# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DODGERBLUE = (30, 144, 255)
DODGERBLUE4 = (16, 78, 139)
HEADING_COLOR = (255, 200, 0)  # Yellow for headings
FALSE_COLOR = HEADING_COLOR
TRUE_COLOR = (50, 200, 0)
TEXT_COLOR = WHITE

class DrawHelpInfo:
    """
    The DrawHelpInfo class provides functionality to draw a help overlay and manage its visibility state.

    This class is designed to render and display a help overlay on a Pygame display surface. It includes
    mechanisms for controlling the visibility of the overlay, scaling graphics based on the display
    resolution, and rendering styled text and buttons with hover effects. Additionally, it provides
    methods to manage and apply gradient rendering for smooth visual effects.

    Attributes:
        display: Reference to the Pygame display surface.
        display_width: The width of the display in pixels.
        display_height: The height of the display in pixels.
        resolution: Tuple containing the display width and height.
        displayType: Type of display based on resolution, used for scaling purposes.
        play_video: Reference to the PlayVideo instance to synchronize help visibility.
        USER_HOME: Path to the user's home directory.
        FONT_DIR: Directory path for fonts used in the overlay.
        RESOURCES_DIR: Directory path for graphical resources used in the overlay.
        font_help_text: Font object for rendering regular help text.
        font_help_heading: Font object for rendering headings in the help overlay.
        font_button: Font object for rendering button text.
        check_icon: Scaled Pygame surface containing the checkmark icon image.
        BOX_WIDTH: Width of the help overlay box in pixels, scaled to display resolution.
        BOX_HEIGHT: Height of the help overlay box in pixels, scaled to display resolution.
        BOX_X: X-coordinate of the top-left corner of the overlay box.
        BOX_Y: Y-coordinate of the top-left corner of the overlay box.
        y_offset_heading: Vertical offset for headings in the help overlay, scaled to display resolution.
        y_offset_text: Vertical offset for text in the help overlay, scaled to resolution.
        help_button_rect: Pygame rectangle for the help overlay's "OK" button.
        help_visible: Boolean flag indicating whether the help overlay is visible.
        is_hovered: Boolean flag indicating whether the "OK" button is currently hovered.

    Methods:
        is_visible(): Determine if the help overlay is currently visible.
        toggle_visibility(): Toggle the visibility state of the help overlay and synchronize it with the PlayVideo instance.
        set_visibility(visible): Set the visibility state of the help overlay and synchronize it with the PlayVideo instance.
        draw_help_overlay(is_hovered): Render the help overlay on the display, including background, gradient, text,
                                       and button, with hover effects.
        draw_help(is_hovered): Display the help overlay and update the hover state of the "OK" button.
        apply_gradient(surface, color_start, color_end, width, height, alpha_start=50, alpha_end=200):
                        Static method to apply a vertical gradient to a Pygame surface, blending colors and alpha values.
    """
    def __init__(self, play_video):
        """
        Initializes the graphical interface and resources necessary for displaying
        content, managing scaling, fonts, icons, and other configurations based
        on the display resolution and user settings.

        Attributes:
            display: The display object used for rendering.
            display_width: The width of the display in pixels.
            display_height: The height of the display in pixels.
            resolution: A tuple representing the width and height of the display.
            displayType: The type of the display based on resolution scaling.
            play_video: Optional instance of the PlayVideo class for video
                playback handling.
            USER_HOME: The user's home directory path.
            FONT_DIR: Directory path for fonts.
            RESOURCES_DIR: Directory path for resource files like icons.
            font_help_text: Scaled font used for displaying help text.
            font_help_heading: Scaled font used for displaying headings.
            font_button: Scaled font used for buttons.
            check_icon: Scaled checkmark icon.
            BOX_WIDTH: The scaled width of the main box area.
            BOX_HEIGHT: The scaled height of the main box area.
            BOX_X: The x-coordinate of the top-left corner of the main box
                area after centering it relative to the display.
            BOX_Y: The y-coordinate of the top-left corner of the main box
                area after centering it relative to the display.
            y_offset_heading: The vertical offset used for positioning headings
                relative to the display scaling.
            y_offset_text: The vertical offset used for positioning text
                relative to the display scaling.
            help_button_rect: Placeholder for the rectangle area of the help
                button.
            help_visible: A flag indicating if the help overlay is currently
                displayed.
            is_hovered: A flag indicating if the mouse is currently hovering
                over a specific element.
        """
        self.play_video = play_video
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

        self.help_button_rect = None
        self.help_visible = False
        self.is_hovered = False

    def is_visible(self):
        return self.help_visible

    def toggle_visibility(self):
        self.help_visible = not self.help_visible
        self.play_video.help_visible = self.help_visible

    def set_visibility(self, visible):
        self.help_visible = visible
        self.play_video.help_visible = self.help_visible

    def draw_help_overlay(self, is_hovered):
        self.is_hovered = is_hovered
        if not self.help_visible:
            return

        # Create and draw the gradient background
        gradient_surface = pygame.Surface((self.BOX_WIDTH, self.BOX_HEIGHT), pygame.SRCALPHA)
        gradient_surface.set_colorkey((0, 255, 0))
        DrawHelpInfo.apply_gradient(
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
        y_constant_end = round(0.875 /self.h_mult, 3)
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
        for line in _help_.HELP_TEXT_LEFT.split("\n"):
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
        for line in _help_.HELP_TEXT_RIGHT.split("\n"):
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
        self.help_button_rect = button_rect
        return button_rect

    def draw_help(self, is_hovered):
        self.is_hovered = is_hovered
        self.set_visibility(True)
        #self.help_visible = True
        self.help_button_rect =  self.draw_help_overlay(is_hovered)
        return self.help_button_rect

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
