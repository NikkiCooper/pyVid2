#  DrawFilterInfo.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
#  Class to display a post-processing filter status information box.

import pygame
import upScale as up_scale

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DODGERBLUE = (30, 144, 255)
DODGERBLUE4 = (16, 78, 139)
HEADING_COLOR = (255, 200, 0)  # Yellow for headings
FALSE_COLOR = HEADING_COLOR
TRUE_COLOR = (50, 200, 0)


class DrawFilterInfo:
    """
    Manages the creation of an interactive and dynamic graphical interface to display
    filter-related information and settings in a Pygame application.

    This class is responsible for rendering an information box that consists of a
    gradient background, filter data organized in columns, a title, and a customizable
    interactive OK button. It includes methods for determining filter data and dynamically
    adjusts visuals based on screen resolution or user-defined settings.

    Attributes
    ----------
    display : pygame.Surface
        The Pygame surface where graphical elements are drawn.
    opts : Any
        Configuration object containing filter options and settings.
    display_width : int
        Width of the current display in pixels.
    display_height : int
        Height of the current display in pixels.
    resolution : tuple[int, int]
        A tuple (width, height) representing the display resolution.
    displayType : str
        Classification of the current display based on resolution.
    USER_HOME : str
        Path to the user's home directory.
    FONT_DIR : str
        Path to the directory containing the application font files.
    RESOURCES_DIR : str
        Path to the directory containing resource files like images.
    font_title : pygame.font.Font
        Pygame font object used for drawing the title text.
    font_button : pygame.font.Font
        Pygame font object used for drawing button text.
    font_info : pygame.font.Font
        Pygame font object used for drawing informational text.
    font_info_bold : pygame.font.Font
        Pygame font object used for drawing bold informational text.
    check_icon : pygame.Surface
        Scaled icon loaded for the OK button, typically a checkmark.
    temp_hide : bool
        Temporary flag indicating whether visibility should be toggled.
    BOX_WIDTH_BASE : int
        Base width of the info box in pixels, used for scaling.
    keyCount : int
        Total number of filter map keys available.
    num_filter_data_lines : int
        Lines of filter data, one line per filter in the display.
    BOX_HEIGHT_BASE : int
        Base height of the info box in pixels, reduced dynamically.
    BOX_WIDTH : int
        Actual scaled width of the info box.
    BOX_HEIGHT : int
        Actual scaled height of the info box.
    BOX_X : int
        X-coordinate for the top-left corner of the info box.
    BOX_Y : int
        Y-coordinate for the top-left corner of the info box.
    button_rect : pygame.Rect
        Rectangle defining position and size of the interactive button.
    is_hovered : bool
        Indicates whether the mouse is hovering over the button.
    """
    def __init__(self, play_video):
        """
        Initializes the user interface configuration and resource loading.

        This method configures various display settings, font loading, resource management, and
        positions UI elements like buttons and dialog boxes. It is responsible for dynamically
        scaling and laying out components based on the display resolution and other parameters.

        Parameters:
            Display: Provides the display interface, including resolution and dimensions.
            opts: Options or settings applicable for the user interface.
            USER_HOME: The path to the user's home directory for locating resources and fonts.
        """
        self.play_video = play_video
        self.opts = play_video.opts
        self.display = self.play_video.win
        #
        self.display_width = self.display.get_width()
        self.display_height = self.display.get_height()
        self.resolution = self.display_width, self.display_height
        self.displayType = up_scale.get_display_type(self.resolution)
        #
        # Generate path to the application fonts
        self.USER_HOME = self.play_video.USER_HOME
        self.FONT_DIR = self.play_video.FONT_DIR
        # Resources
        self.RESOURCES_DIR = self.play_video.RESOURCES_DIR
        #
        original_font_sizes = [36, 18, 24, 20, 26]
        scaled_font_size = up_scale.get_scaled_fonts(original_font_sizes, self.display_height)
        # Load Fonts
        self.font_title = pygame.font.Font(self.FONT_DIR + 'Montserrat-Bold.ttf', scaled_font_size[1])
        self.font_button = pygame.font.Font(self.FONT_DIR + 'Montserrat-Bold.ttf', scaled_font_size[2])
        self.font_info = pygame.font.Font(self.FONT_DIR + 'Arial.ttf', scaled_font_size[3])
        self.font_info_bold = pygame.font.Font(self.FONT_DIR + 'Arial_Black.ttf', scaled_font_size[4])
        #
        # Load and scale checkmark icon
        self.check_icon = pygame.image.load(self.RESOURCES_DIR + 'checkmark.png').convert_alpha()
        self.check_icon = pygame.transform.scale(self.check_icon, (32, 32))
        self.temp_hide = False
        self.BOX_WIDTH_BASE = 800
        self.keyCount = len(self.get_filter_map())
        self.num_filter_data_lines = self.keyCount
        #
        # Calculate items per column for 2 columns
        items_per_column = (self.num_filter_data_lines + 1) // 2
        #
        # Calculate total height needed with reduced values:
        title_height = 40  # Reduced from 60
        content_start = 60  # Reduced from 85
        row_spacing = 45  # Keep current row spacing as it works well
        button_height = 40
        bottom_padding = 20  # Reduced from 30

        # Calculate actual height needed
        content_height = (items_per_column * row_spacing)
        total_height = title_height + content_height + button_height + bottom_padding

        # Apply 35% reduction to the total height instead of 45%
        self.BOX_HEIGHT_BASE = int(total_height * 0.65)  # Reduces height by 35%

        width_multiplier, height_multiplier = up_scale.scale_resolution(self.displayType) \
            if self.displayType in up_scale.resolution_multipliers else (1, 1)

        # Dialog box positioning
        self.BOX_WIDTH = int(width_multiplier * self.BOX_WIDTH_BASE)
        self.BOX_HEIGHT = int(height_multiplier * self.BOX_HEIGHT_BASE)

        self.BOX_X = (self.display_width - self.BOX_WIDTH) // 2
        self.BOX_Y = (self.display_height - self.BOX_HEIGHT) // 2 - 50

        # Position OK button with more space from bottom
        button_width_base = 120
        button_height_base = 40

        w_mult, h_mult = up_scale.resolution_multipliers[self.displayType]
        button_width = int(button_width_base * w_mult)
        button_height = int(button_height_base * h_mult)

        button_x = self.BOX_X + (self.BOX_WIDTH // 2) - (button_width // 2)
        button_y = self.BOX_Y + self.BOX_HEIGHT - (button_height + 20)  # Slightly more padding

        self.button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        self.is_hovered = False
        self.title_surface = None
        self.title_rect = None

    def draw_info_box(self):
        """
        Renders an information box onto a Pygame surface, displaying a gradient background,
        filter data in two columns, and an interactive OK button.
        """
        is_hovered = self.is_hovered

        # Create and apply gradient surface
        gradient_surface = pygame.Surface((self.BOX_WIDTH, self.BOX_HEIGHT), pygame.SRCALPHA)
        self.play_video.apply_gradient(
            gradient_surface,
            (0, 0, 255),
            (0, 0, 100),
            self.BOX_WIDTH,
            self.BOX_HEIGHT,
            alpha_start=80,
            alpha_end=180
        )

        # Blit gradient and draw border
        self.display.blit(gradient_surface, (self.BOX_X, self.BOX_Y))
        pygame.draw.rect(self.display,
                         DODGERBLUE,
                         (self.BOX_X, self.BOX_Y, self.BOX_WIDTH, self.BOX_HEIGHT),
                         4,
                         border_radius=8
                         )

        # Render title
        box_title = "Post-Processing Filters"
        self.title_surface = self.font_title.render(box_title, True, HEADING_COLOR)
        self.title_rect = self.title_surface.get_rect(center=(self.BOX_X + self.BOX_WIDTH // 2, self.BOX_Y + 40))
        self.display.blit(self.title_surface, self.title_rect.topleft)

        # Calculate column layout
        num_columns = 2
        filter_map = self.get_filter_map()
        filters_list = list(filter_map.items())
        items_per_column = (len(filters_list) + num_columns - 1) // num_columns

        # Column dimensions and spacing
        padding = 60  # Padding from box edges
        column_width = (self.BOX_WIDTH - (padding * 2)) // num_columns
        start_y = self.BOX_Y + 85  # Starting Y position after title
        row_spacing = 45  # Reduced space between rows

        # Calculate fixed position for status text (centered in each column)
        status_offset = column_width - 200  # Fixed distance for status text

        # Draw filters in columns
        for col in range(num_columns):
            start_idx = col * items_per_column
            end_idx = min((col + 1) * items_per_column, len(filters_list))

            # Calculate column x position with padding
            col_x = self.BOX_X + padding + (col * column_width)

            # Draw filters for this column
            for idx in range(start_idx, end_idx):
                filter_name, settings = filters_list[idx]
                y_pos = start_y + ((idx - start_idx) * row_spacing)

                # Render filter name and status
                status = 'Enabled' if settings.get('enabled') else 'Disabled'
                name_surface = self.font_info.render(filter_name, True, WHITE)
                status_surface = self.font_info.render(status, True,
                                                       TRUE_COLOR if status == 'Enabled' else FALSE_COLOR)

                # Position status text at fixed offset
                status_x = col_x + status_offset

                # Draw text
                self.display.blit(name_surface, (col_x, y_pos))
                self.display.blit(status_surface, (status_x, y_pos))

        # Render OK Button with centered content
        button_color = DODGERBLUE if is_hovered else DODGERBLUE4
        pygame.draw.rect(self.display, button_color, self.button_rect, border_radius=8)
        pygame.draw.rect(self.display, BLACK, self.button_rect, 1, border_radius=8)

        # Center checkmark icon and OK text in button
        icon_x = self.button_rect.x + (self.button_rect.width - self.check_icon.get_width()) // 2 - 20
        icon_y = self.button_rect.y + (self.button_rect.height - self.check_icon.get_height()) // 2
        self.display.blit(self.check_icon, (icon_x, icon_y))

        ok_surface = self.font_button.render("OK", True, HEADING_COLOR if is_hovered else WHITE)
        ok_x = icon_x + self.check_icon.get_width() + 10
        ok_y = self.button_rect.y + (self.button_rect.height - ok_surface.get_height()) // 2
        self.display.blit(ok_surface, (ok_x, ok_y))

    def get_filter_map(self):
        """
        Constructs a mapping of various image and video filters, indicating their activation status
        and additional configurations.

        Returns
        -------
        dict
            A dictionary where the keys are filter names as strings and values are dictionaries
            containing the 'enabled' status as well as optionally other key-value pairs such
            as 'preset' if applicable.
        """
        filter_map = {
            'Laplacian Boost': {
                'enabled': getattr(self.opts, 'laplacian')
            },
            'U-Sharp': {
                'enabled': getattr(self.opts, 'apply_sharpening')
            },
            'Blur': {
                'enabled': getattr(self.opts, 'blur')
            },
            'Median-Blur': {
                'enabled': getattr(self.opts, 'median_blur')
            },
            'Gaussian-Blur': {
                'enabled': getattr(self.opts, 'gaussian_blur')
            },
            'Noise': {
                'enabled': getattr(self.opts, 'noise')
            },
            'Denoise': {
                'enabled': getattr(self.opts, 'apply_denoising')
            },
            'Greyscale': {
                'enabled': getattr(self.opts, 'greyscale')
            },
            'Sepia': {
                'enabled': getattr(self.opts, 'sepia')
            },
            'Cel-Shading': {
                'enabled': getattr(self.opts, 'cel_shading')
            },
            'Saturation': {
                'enabled': getattr(self.opts, 'saturation')
            },
            'Contrast Enhancement': {
                'enabled': getattr(self.opts, 'apply_contrast_enhancement')
            },
            'Brightness/Contrast': {
                'enabled': getattr(self.opts, 'apply_adjust_video')
            },
            'Vignette': {
                'enabled': getattr(self.opts, 'vignette')
            },
            'Thermal': {
                'enabled': getattr(self.opts, 'thermal')
            },
            'Emboss': {
                'enabled': getattr(self.opts, 'emboss')
            },
            'Dream': {
                'enabled': getattr(self.opts, 'dream')
            },
            'Neon': {
                'enabled': getattr(self.opts, 'neon')
            },
            'Pixelate': {
                'enabled': getattr(self.opts, 'pixelate')
            },
            'Invert': {
                'enabled': getattr(self.opts, 'apply_inverted')
            },
            'Flip-Left-Right': {
                'enabled': getattr(self.opts, 'fliplr')
            },
            'Flip-Up-Down': {
                'enabled': getattr(self.opts, 'flipup')
            },
            'Comic': {
                'enabled': getattr(self.opts, 'comic')
            },
            'Comic-Sharp': {
                'enabled': getattr(self.opts, 'comic_sharp')
            },
            'Oil Painting': {
                'enabled': getattr(self.opts, 'oil_painting')
            },
            'watercolor': {
                'enabled': getattr(self.opts, 'watercolor')
            },
            'Pencil Sketch': {
                'enabled': getattr(self.opts, 'pencil_sketch')
            },
            'Edges-Sobel': {
                'enabled': getattr(self.opts, 'apply_edges_sobel')
            },
            'Edge Detect': {
                'enabled': getattr(self.opts, 'apply_edge_detect')
            },
            'Artistic-Filters': {
                'enabled': getattr(self.opts, 'apply_artistic_filters')
            },
            'CUDA Bilateral Filter': {
                'enabled': getattr(self.opts, 'apply_bilateral_filter')
            }
        }
        return filter_map


