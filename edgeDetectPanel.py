#  edgeDetectPanel.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Class to display a control panel for adjusting --edge-Upper and edge-Lower-- values for use with --edge-detect.
#
import pygame
import cv2

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DODGERBLUE = (30, 144, 255)
DODGERBLUE4 = (16, 78, 139)
HEADING_COLOR = (255, 200, 0)  # Yellow for headings
FALSE_COLOR = HEADING_COLOR
TRUE_COLOR = (50, 200, 0)
TEXT_COLOR = WHITE


class edgeDetectPanel:
    """
    Class for creating and managing a panel for edge detection settings in a video application.

    This class is responsible for rendering a control panel that contains sliders for adjusting
    edge detection thresholds, as well as buttons for resetting the settings. It interacts with
    a provided video player instance to apply the selected effects in real-time.

    Attributes
    ----------
    screen_width : int
        The width of the application screen in pixels.
    screen_height : int
        The height of the application screen in pixels.
    panel_height : int
        The height of the control panel, computed as a percentage of the screen height.
    panel_width : int
        The width of the control panel, computed as a percentage of the screen width.
    panel_x : int
        The x-coordinate of the panel's position, offset from the right screen edge.
    panel_y : int
        The y-coordinate of the panel's position, offset from the top of the screen.
    play_video : PlayVideo, optional
        Reference to an optional video player instance for managing video effects.
    surface : pygame.Surface
        The Pygame surface representing the visual appearance of the panel.
    rect : pygame.Rect
        The rectangle defining the position and bounds of the panel.
    edge_upper_slider : dict
        A dictionary containing properties for the upper edge detection slider, such
        as its rectangle, knob, value, and state.
    edge_lower_slider : dict
        A dictionary containing properties for the lower edge detection slider, such
        as its rectangle, knob, value, and state.
    reset_button_rect : None or pygame.Rect
        The rectangle of the reset button, initialized to None by default and set
        during the drawing process.
    edge_upper_level : int
        The default value for the upper edge detection threshold.
    edge_lower_level : int
        The default value for the lower edge detection threshold.
    is_visible : bool
        Tracks whether the panel is currently visible on the screen.
    active_slider : None or str
        Stores the identifier of the slider currently being interacted with, if any.

    Methods
    -------
    __init__(screen_width: int, screen_height: int, play_video: PlayVideo = None):
        Initializes the EdgeDetectPanel with dimensions, positions, and optional
        video functionalities.

    draw(screen: pygame.Surface):
        Renders the visual elements of the edge detection control panel onto the
        provided Pygame surface.

    handle_mouse_button_down(pos: (int, int)):
        Handles mouse button down events to determine if sliders or buttons within the
        panel are being interacted with.
    """
    def __init__(self, play_video):
        """
        Initializes a panel with sliders and graphical elements for a video application.

        This class constructor sets up a graphical panel and its components, such as sliders
        and buttons, for interacting with video effects in a pygame application. It also
        applies specific visual properties (like gradients and borders) to enhance the
        components' appearance.

        Attributes:
            panel_height (int): Height of the panel as a percentage of the screen height.
            panel_width (int): Width of the panel as a percentage of the screen width.
            panel_x (int): X coordinate of the panel, positioned with padding from the right edge.
            panel_y (int): Y coordinate of the panel, positioned with padding from the top edge.
            play_video (PlayVideo or None): A reference to the video instance managing effects and
                gradient application. Defaults to None.
            surface (pygame.Surface): The graphical surface for the panel with alpha channel support.
            rect (pygame.Rect): A rectangle defining the panel's position and dimensions.
            edge_upper_slider (dict): A dictionary storing information for the upper slider,
                including its rectangle, knob, value, and dragging state.
            edge_lower_slider (dict): A dictionary storing information for the lower slider,
                including its rectangle, knob, value, and dragging state.
            reset_button_rect (pygame.Rect or None): A rectangle for the reset button. Defaults
                to None.
            edge_upper_level (int): Initial value for the upper edge level effect.
            edge_lower_level (int): Initial value for the lower edge level effect.
            is_visible (bool): State indicating whether the panel is visible. Defaults to False.
            active_slider (None or dict): The currently active slider being adjusted. Defaults to None.

        Args:
            screen_width (int): Width of the application screen in pixels.
            screen_height (int): Height of the application screen in pixels.
            play_video (PlayVideo, optional): An instance linking to the video processing object
                managing effects. Defaults to None.
        """
        self.play_video = play_video
        Screen = self.play_video.win
        screen_width = Screen.get_width()
        screen_height = Screen.get_height()

        # Panel dimensions and position
        self.panel_height = int(screen_height * 0.15)  # 15% of screen height
        self.panel_width = int(screen_width * 0.3)  # 30% of screen width
        self.panel_x = screen_width - self.panel_width - 20  # 20px padding from right
        self.panel_y = 50  # 50px from top

        # Create the panel surface with an alpha channel
        self.surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        self.rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        self.surface.set_colorkey((0, 255, 0))

        pygame.draw.rect(
            self.surface,
            DODGERBLUE,
            (0, 0, self.panel_width, self.panel_height),
            1,
            border_radius=8
        )

        self.play_video.apply_gradient(self.surface,
                                 (0, 0, 200),
                                 (0, 0, 100),
                                 self.panel_width,
                                 self.panel_height,
                                 alpha_start=100,
                                 alpha_end=200
        )

        pygame.draw.rect(
            self.surface,
            DODGERBLUE,
            (0, 0, self.panel_width, self.panel_height),
            1,
            border_radius=8
        )

        # Initialize font for title
        self.title_font = pygame.font.Font(None, 48)

        # Initalize Effect values
        if self.play_video and hasattr(self.play_video, 'opts'):
            self.is_disabled = True if self.play_video.opts.apply_edge_detect is False else False
            self.edge_upper_level = self.play_video.opts.edge_upper
            self.edge_lower_level = self.play_video.opts.edge_lower
        else:
            self.is_disabled = None
            self.edge_upper_level = 200
            self.edge_lower_level = 100

        # Slider dimensions
        slider_width = int(self.panel_width * 0.8)
        slider_height = 10
        slider_x = int((self.panel_width - slider_width) / 2)

        # Initialize sliders
        self.edge_upper_slider = {
            'rect': pygame.Rect(slider_x, 60, slider_width, slider_height),
            'knob': pygame.Rect(slider_x + slider_width // 2, 55, 20, 20),
            'value': self.edge_upper_level,
            'dragging': False
        }

        self.edge_lower_slider = {
            'rect': pygame.Rect(slider_x, 120, slider_width, slider_height),
            'knob': pygame.Rect(slider_x + slider_width // 2, 115, 20, 20),
            'value': self.edge_lower_level,
            'dragging': False
        }

        # Button rectangle
        self.reset_button_rect = None
        self.hide_button_rect = None

        # State
        self.is_visible = False
        self.active_slider = None

    def draw(self, screen):
        """
        Draws a user interface panel with sliders, labels, and a reset button on the provided screen.

        This method is responsible for rendering the panel background, adjustable sliders with their
        associated labels, and a reset button. The sliders allow modifying values within specific ranges,
        where each slider is rendered with a label and its current value displayed above it.

        Attributes:
            is_visible (bool): Indicates whether the panel should be visible.
            surface (pygame.Surface): Panel's main surface for drawing.
            rect (pygame.Rect): Panel's location and rectangular bounds.
            edge_upper_slider (dict): Data structure representing the "Edge Upper" slider including its
                geometry, current value, and ranges.
            edge_lower_slider (dict): Data structure representing the "Edge Lower" slider including its
                geometry, current value, and ranges.
            panel_width (int): Width of the UI panel.
            panel_height (int): Height of the UI panel.

        Parameters:
            screen (pygame.Surface): Screen surface where the panel and its components are drawn.

        Raises:
            None

        Returns:
            None
        """
        if not self.is_visible:
            return

        # Draw the panel background
        screen.blit(self.surface, self.rect)
        title_text = self.title_font.render('Edge Detect Filter', True, HEADING_COLOR)
        screen.blit(title_text, (self.rect.x + (self.panel_width - title_text.get_width()) // 2, self.rect.y + 10))

        # Draw sliders
        for slider, label, value_range in [(self.edge_upper_slider, "Edge Upper", (0, 255)), (self.edge_lower_slider, "Edge Lower", (0, 254))]:
            # Draw slider background
            pygame.draw.rect(screen, (100, 100, 100),
                             (self.rect.x + slider['rect'].x, self.rect.y + slider['rect'].y, slider['rect'].width, slider['rect'].height))
            # Draw slider knob
            pygame.draw.rect(screen, DODGERBLUE4, (self.rect.x + slider['knob'].x, self.rect.y + slider['knob'].y, slider['knob'].width, slider['knob'].height))
            pygame.draw.rect(screen, DODGERBLUE, (self.rect.x + slider['knob'].x, self.rect.y + slider['knob'].y, slider['knob'].width, slider['knob'].height),
                             2, border_radius=5)

            # Draw label and value
            font = pygame.font.Font(None, 36)
            label_text = font.render(f"{label}: {slider['value']}", True, DODGERBLUE)
            screen.blit(label_text, (self.rect.x + slider['rect'].x, self.rect.y + slider['rect'].y - 25))

        # Draw the reset button
        reset_button_rect = pygame.Rect(self.rect.x + self.panel_width // 2 - 180, self.rect.y + self.panel_height - 100, 120, 45)
        pygame.draw.rect(screen, DODGERBLUE, reset_button_rect, border_radius=10)
        pygame.draw.rect(screen, DODGERBLUE4, reset_button_rect, 1, border_radius=10)

        reset_text = pygame.font.Font(None, 36).render("Reset", True, (255, 255, 255))
        screen.blit(reset_text, (reset_button_rect.x + 25, reset_button_rect.y + 12))

        # Store the button rect for hit testing
        self.reset_button_rect = reset_button_rect

        # Draw the hide button
        hide_button_rect = pygame.Rect(self.rect.x + self.panel_width // 2 - 40, self.rect.y + self.panel_height - 100, 120, 45)
        pygame.draw.rect(screen, DODGERBLUE4, hide_button_rect, border_radius=10)
        pygame.draw.rect(screen, DODGERBLUE, hide_button_rect, 1, border_radius=10)
        hide_text = pygame.font.Font(None, 36).render("Hide", True, (255, 255, 255))
        screen.blit(hide_text, (hide_button_rect.x + 30, hide_button_rect.y + 12))

        self.hide_button_rect = hide_button_rect

    def handle_mouse_button_down(self, pos):
        """
        Handles mouse button down events for interacting with UI components such as sliders.

        Determines if a specific point (e.g., a mouse click position) intersects with any
        of the interactive components, such as sliders or buttons. Adjusts the state of
        the active UI element based on the interaction.

        Parameters:
        pos: tuple[int, int]
            The (x, y) position of the mouse click in absolute coordinates.

        Returns:
        bool
            True if the mouse button down event interacted with a UI element,
            False otherwise.
        """
        if not self.is_visible:
            return False

        relative_pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)

        # Check if click is within oil size slider knob
        edge_upper_knob_rect = pygame.Rect(
            self.edge_upper_slider['knob'].x,
            self.edge_upper_slider['knob'].y,
            self.edge_upper_slider['knob'].width,
            self.edge_upper_slider['knob'].height
        )
        # Check edge_upper slider
        if edge_upper_knob_rect.collidepoint(relative_pos):
            self.active_slider = 'edge-Upper'
            self.edge_upper_slider['dragging'] = True
            return True

        # Check if click is within oil dynamics slider knob
        edge_lower_knob_rect = pygame.Rect(
            self.edge_lower_slider['knob'].x,
            self.edge_lower_slider['knob'].y,
            self.edge_lower_slider['knob'].width,
            self.edge_lower_slider['knob'].height
        )
        if edge_lower_knob_rect.collidepoint(relative_pos):
            self.active_slider = 'edge-Lower'
            self.edge_lower_slider['dragging'] = True
            return True

        # Check if reset button was clicked
        if self.reset_button_rect and self.reset_button_rect.collidepoint(pos):
            self.reset_effects()
            return True

        if self.hide_button_rect and self.hide_button_rect.collidepoint(pos):
            self.set_visible(False)
            return True

        return False

    def handle_mouse_button_up(self):
        """
        Handles the event of the mouse button being released.

        This method manages the state of the active slider when the mouse button
        is released. It determines which slider (upper or lower edge) is currently
        active and updates its dragging state accordingly. Once processed, it
        resets the active slider to None.

        Raises:
            None
        """
        if self.active_slider:
            if self.active_slider == 'edge-Upper':
                self.edge_upper_slider['dragging'] = False
            else:
                self.edge_lower_slider['dragging'] = False
            self.active_slider = None

    def handle_mouse_motion(self, pos):
        """
        Handles mouse motion events for an active slider and adjusts the slider's position
        and associated values dynamically. This allows interactive control over certain
        thresholds or levels, such as 'edge-Upper' and 'edge-Lower', with updates applied
        to the associated video processing if applicable.

        Args:
            pos (tuple[int, int]): The position of the mouse during the motion event,
                given as a tuple of x and y coordinates.

        Returns:
            bool: True if the slider's position or value was updated as a result of the
                mouse motion; otherwise, False.
        """
        if not self.active_slider:
            return False

        relative_x = pos[0] - self.rect.x
        slider = (self.edge_upper_slider if self.active_slider == 'edge-Upper' else self.edge_lower_slider)

        # Calculate new position within bounds
        new_x = max(slider['rect'].left,
                    min(relative_x - slider['knob'].width / 2,
                        slider['rect'].right - slider['knob'].width))
        slider['knob'].x = new_x

        # Calculate value based on position
        value_range = (0, 255) if self.active_slider == 'edge-Upper' else (0, self.edge_upper_slider['value'] - 1)
        range_min, range_max = value_range

        pos_ratio = (new_x - slider['rect'].left) / (slider['rect'].width - slider['knob'].width)
        new_value = int(range_min + (range_max - range_min) * pos_ratio)

        # Only update if value changed
        if slider['value'] != new_value:
            slider['value'] = new_value
            if self.active_slider == 'edge-Upper':
                self.edge_upper_level = slider['value']
                # Update PlayVideo's opts.brightness if PlayVideo instance is available
                if self.play_video and hasattr(self.play_video, 'opts'):
                    self.play_video.opts.edge_upper = self.edge_upper_level
                    self.play_video.update_video_effects()
            else:
                self.edge_lower_level =  (slider['value'] - 1)
                # Update PlayVideo's opts.edge_lower if PlayVideo instance is available
                if self.play_video and hasattr(self.play_video, 'opts'):
                    # Convert our edge_lower value to the range expected by the video processor
                    self.play_video.opts.edge_lower = slider['value']
                    self.play_video.update_video_effects()

        return True

    def Apply_Effects(self, image):
        """
        Applies edge-detection effects on an input image using either CUDA acceleration or CPU fallback.

        The method utilizes OpenCV's Canny edge-detection algorithm. When CUDA-enabled devices are available,
        it uses GPU acceleration for processing to optimize performance. If CUDA is unavailable or fails during
        execution, it falls back to CPU-based edge-detection.

        Parameters:
            image: numpy.ndarray
                The input image on which edge-detection effects are applied.

        Returns:
            numpy.ndarray
                An image with applied edge-detection effects in BGR color format.

        Raises:
            cv2.error
                If any OpenCV-related error occurs during GPU or CPU processing.
        """
        #threshold1 = 100, threshold2 = 200
        threshold1 = int(self.edge_lower_slider['value'])
        threshold2 = int(self.edge_upper_slider['value'])

        if not hasattr(edgeDetectPanel, '_cuda_edge_detect_available'):
            edgeDetectPanel._cuda_edge_detect_available = cv2.cuda.getCudaEnabledDeviceCount() > 0
            edgeDetectPanel._cuda_edge_detect_filter = None
            if edgeDetectPanel._cuda_edge_detect_available:
                print("CUDA Edge-Detection Filter initialized")
                #print(f"threshold1: {threshold1}, threshold2: {threshold2}")
        if edgeDetectPanel._cuda_edge_detect_available:
            try:
                edgeDetectPanel._cuda_edge_detect_filter = cv2.cuda.createCannyEdgeDetector(threshold1, threshold2)
                gpu_image = cv2.cuda_GpuMat()
                gpu_image.upload(image)
                gray_gpu = cv2.cuda.cvtColor(gpu_image, cv2.COLOR_BGR2GRAY)
                result = edgeDetectPanel._cuda_edge_detect_filter.detect(gray_gpu)
                return cv2.cuda.cvtColor(result, cv2.COLOR_GRAY2BGR).download()

            except cv2.error:
                # Fallback to CPU if CUDA fails
                #PlayVideo._cuda_edge_detect_available = False
                edgeDetectPanel._cuda_edge_detect_available = False
                #print("Edge Detect: CUDA failed, falling back to CPU")
                edges = cv2.Canny(image, threshold1, threshold2)
                return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    def toggle_visibility(self):
        """
        Toggles the visibility state of an object.

        This method reverses the current visibility state of the object. If the
        object is currently visible, it will become invisible and vice versa.

        Raises:
            None
        """
        self.is_visible = not self.is_visible

    def set_visible(self, is_visible):
        self.is_visible = is_visible

    def reset_effects(self):
        """
        Resets the visual effects to their default values, which includes brightness and
        contrast adjustments. Ensures that sliders for the "edge_upper" and "edge_lower"
        levels are set to their initial neutral positions. Also disables edge detection
        within the video if both levels are at their default settings.

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        None
        """
        # Reset edge_upper slider
        self.edge_upper_slider['knob'].x = self.edge_upper_slider['rect'].left + self.edge_upper_slider['rect'].width // 2
        self.edge_upper_slider['value'] = 200
        self.edge_upper_level = 200

        # Reset edge_lower slider
        self.edge_lower_slider['knob'].x = self.edge_lower_slider['rect'].left + self.edge_lower_slider['rect'].width // 2
        self.edge_lower_slider['value'] = 100
        self.edge_lower_level = 100

        # Turn off video adjustment if both are at default values
        if self.play_video and hasattr(self.play_video, 'opts'):
            self.play_video.opts.edge_upper = 200
            self.play_video.opts.edge_lower = 100
            self.play_video.opts.edge_detect = False
            self.play_video.update_video_effects()
