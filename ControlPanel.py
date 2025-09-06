#  ControlPanel.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Class to create a control panel for adjusting brightness and contrast values for use with --adjust-video.

import pygame
import numpy as np

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DODGERBLUE = (30, 144, 255)
DODGERBLUE4 = (16, 78, 139)
HEADING_COLOR = (255, 200, 0)  # Yellow for headings
FALSE_COLOR = HEADING_COLOR
TRUE_COLOR = (50, 200, 0)
TEXT_COLOR = WHITE

class ControlPanel:
    """
    Represents a settings control panel allowing users to adjust screen effects through interactive
    components such as sliders and buttons.

    This class is designed to render an overlay panel on the screen for real-time adjustments of
    brightness and contrast settings. The interface includes two sliders for effect parameters and
    a reset button, with dynamic scaling based on the screen dimensions. The panel supports rotation
    of visibility state and interaction detection for mouse-based controls.

    Attributes:
        panel_height (int): Height of the panel, calculated as 12% of the screen height.
        panel_width (int): Width of the panel, calculated as 30% of the screen width.
        panel_x (int): X-coordinate of the panel's position, with padding from the screen edge.
        panel_y (int): Y-coordinate of the panel's position, with padding from the screen edge.
        play_video (PlayVideo | None): Optional reference for applying graphical gradients.
        surface (pygame.Surface): Panel's rendering surface supporting alpha transparency.
        rect (pygame.Rect): Rectangular frame that defines the panel's boundaries.
        brightness_slider (dict): Properties for the brightness slider, including its dimensions,
            position, and state.
        contrast_slider (dict): Properties for the contrast slider, including its dimensions,
            position, and state.
        reset_button_rect (None | pygame.Rect): Rectangle representing the "Reset" button position
            and size.
        brightness_level (int): Value representing the brightness adjustment.
        contrast_multiplier (float): Value representing the contrast adjustment multiplier.
        is_visible (bool): Panel display state indicating whether the overlay is active.
        active_slider (None | str): Slider currently interacted with (if any).

    Methods:
        __init__(screen_width: int, screen_height: int, play_video: PlayVideo | None = None):
            Initializes the ControlPanel instance with required screen dimensions and optional
            video effect handler.
        draw(screen: pygame.Surface):
            Renders the panel, including sliders and button, onto the given surface if it is set
            as visible.
        handle_mouse_button_down(pos: tuple[int, int]) -> bool:
            Processes mouse button down events to check interaction on sliders or the reset button.
    """
    def __init__(self, play_video):
        """
        Initializes a panel for managing brightness and contrast sliders, and rendering related
        visual elements such as a gradient background and panel borders. The panel is positioned
        on the screen based on given dimensions and is optionally linked to a PlayVideo instance
        to handle visual effects. The panel includes interactive sliders for brightness and
        contrast adjustment.

        Arguments:
            screen_width: The width of the display screen (int).
            screen_height: The height of the display screen (int).
            play_video: Optional reference to an instance of PlayVideo for applying visual effects.

        Attributes:
            panel_height: Height of the panel, determined as 12% of the screen height (int).
            panel_width: Width of the panel, determined as 30% of the screen width (int).
            panel_x: x-coordinate of the top-left corner of the panel (int).
            panel_y: y-coordinate of the top-left corner of the panel (int).
            play_video: Reference to an instance of PlayVideo (optional).
            surface: Pygame surface used for rendering the panel.
            rect: A rectangle representing the panel's dimensions and position.
            brightness_slider: Dictionary holding details of the brightness slider including its position,
                knob geometry, current value, and dragging state.
            contrast_slider: Dictionary holding details of the contrast slider including its position,
                knob geometry, current value, and dragging state.
            reset_button_rect: Rectangle for defining the position and dimensions of a reset button.
            brightness_level: Level of brightness adjustment (int, defaults to 0).
            contrast_multiplier: Multiplier for contrast adjustment (float, defaults to 1.0).
            is_visible: Boolean indicating if the panel is visible or not (boolean).
            active_slider: Currently active/dragged slider. Can be brightness, contrast, or None.
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

        # Slider dimensions
        slider_width = int(self.panel_width * 0.8)
        slider_height = 10
        slider_x = int((self.panel_width - slider_width) / 2)

        # Initialize sliders
        self.brightness_slider = {
            'rect': pygame.Rect(slider_x, 60, slider_width, slider_height),
            'knob': pygame.Rect(slider_x + slider_width // 2, 55, 20, 20),
            'value': 0,
            'dragging': False
        }

        self.contrast_slider = {
            'rect': pygame.Rect(slider_x, 120, slider_width, slider_height),
            'knob': pygame.Rect(slider_x + slider_width // 2, 115, 20, 20),
            'value': 0,
            'dragging': False
        }

        # Button rectangle
        self.reset_button_rect = None
        self.hide_button_rect = None

        # Effect values
        self.brightness_level = 0
        self.contrast_multiplier = 1.0

        # State
        self.is_visible = False
        self.active_slider = None

    def draw(self, screen):
        """
        Draws the slider panel and its components onto the given screen.

        The function checks the visibility of the panel and draws the necessary components, including
        the panel background, sliders with their respective labels and values, and a reset button.
        It also updates the reset button's rectangle to enable hit testing for interaction.

        Attributes
        ----------
        self.surface : pygame.Surface
            The surface representing the background of the panel.
        self.rect : pygame.Rect
            The rectangle defining the position and size of the panel.
        self.brightness_slider : dict
            A dictionary containing details about the brightness slider, such as its position, value, and range.
        self.contrast_slider : dict
            A dictionary containing details about the contrast slider, such as its position, value, and range.
        self.reset_button_rect : pygame.Rect
            The rectangle that represents the position and dimensions of the reset button.
        self.panel_width : int
            The width of the panel used to position components dynamically.
        self.panel_height : int
            The height of the panel used to position components dynamically.

        Parameters
        ----------
        screen : pygame.Surface
            The surface to which the panel and its components are drawn.

        Raises
        ------
        None
        """
        if not self.is_visible:
            return False

        # Draw the panel background
        screen.blit(self.surface, self.rect)
        title_text = self.title_font.render('Brightness/Contrast', True, HEADING_COLOR)
        screen.blit(title_text, (self.rect.x + (self.panel_width - title_text.get_width()) // 2, self.rect.y + 10))

        # Draw sliders
        for slider, label, value_range in [(self.brightness_slider, "Brightness", (-100, 100)), (self.contrast_slider, "Contrast", (-127, 127))]:
            # Draw slider background
            pygame.draw.rect(screen, (100, 100, 100), (self.rect.x + slider['rect'].x, self.rect.y + slider['rect'].y, slider['rect'].width, slider['rect'].height))
            # Draw slider knob
            pygame.draw.rect(screen, DODGERBLUE4, (self.rect.x + slider['knob'].x, self.rect.y + slider['knob'].y, slider['knob'].width, slider['knob'].height))
            pygame.draw.rect(screen, DODGERBLUE,  (self.rect.x + slider['knob'].x, self.rect.y + slider['knob'].y, slider['knob'].width, slider['knob'].height),
                             2, border_radius=5)

            # Draw label and value
            font = pygame.font.Font(None, 36)
            label_text = font.render(f"{label}: {slider['value']}", True, DODGERBLUE)
            screen.blit(label_text, (self.rect.x + slider['rect'].x, self.rect.y + slider['rect'].y - 25))

        # Draw the reset button
        reset_button_rect = pygame.Rect(
            self.rect.x + self.panel_width // 2 - 180, self.rect.y + self.panel_height - 100, 120, 45)
        pygame.draw.rect(screen, DODGERBLUE4, reset_button_rect, border_radius=10)
        pygame.draw.rect(screen, DODGERBLUE, reset_button_rect, 1, border_radius=10)

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

        return True

    def handle_mouse_button_down(self, pos):
        """
        Handles the mouse button down event and processes interaction with UI elements
        such as sliders (brightness and contrast) or a reset button within the component.
        Checks whether the visible UI elements are being interacted with based on the
        current position of the mouse click.

        Parameters:
            pos (tuple): The position of the mouse cursor when the button is clicked,
                represented as (x, y) coordinates.

        Returns:
            bool: True if any UI component (brightness slider, contrast slider,
            or reset button) is interacted with, otherwise False.
        """
        if not self.is_visible:
            return False

        relative_pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)

        # Check if click is within brightness slider knob
        brightness_knob_rect = pygame.Rect(
            self.brightness_slider['knob'].x,
            self.brightness_slider['knob'].y,
            self.brightness_slider['knob'].width,
            self.brightness_slider['knob'].height
        )
        if brightness_knob_rect.collidepoint(relative_pos):
            self.active_slider = 'brightness'
            self.brightness_slider['dragging'] = True
            return True

        # Check if click is within contrast slider knob
        contrast_knob_rect = pygame.Rect(
            self.contrast_slider['knob'].x,
            self.contrast_slider['knob'].y,
            self.contrast_slider['knob'].width,
            self.contrast_slider['knob'].height
        )
        if contrast_knob_rect.collidepoint(relative_pos):
            self.active_slider = 'contrast'
            self.contrast_slider['dragging'] = True
            return True

        # Check if the reset button was clicked
        if self.reset_button_rect and self.reset_button_rect.collidepoint(pos):
            self.reset_effects()
            return True

        # Check if the hide button was clicked
        if self.hide_button_rect and self.hide_button_rect.collidepoint(pos):
            self.set_visible(False)
            return True

        return False

    def handle_mouse_button_up(self):
        """
        Handles the event when a mouse button is released.

        This method is used to process the mouse button release event particularly
        for sliders being interacted with. It updates the state of the sliders
        to stop the "dragging" behavior and resets the active slider.

        Raises
        ------
        None
        """
        if self.active_slider:
            if self.active_slider == 'brightness':
                self.brightness_slider['dragging'] = False
            else:
                self.contrast_slider['dragging'] = False
            self.active_slider = None

    def handle_mouse_motion(self, pos):
        """
        Handles mouse motion events to update the position of an active slider knob and adjust
        the corresponding value (e.g., brightness or contrast) based on the slider's state.

        If a slider is currently active, the method calculates the new knob position within its
        allowed bounds, determines the corresponding value in the associated range, and updates
        the slider's value. Changes are propagated to a PlayVideo instance if available.

        Parameters:
            pos (tuple[int, int]): The current mouse position as (x, y) coordinates.

        Returns:
            bool: True if a slider's state was updated, otherwise False.

        Raises:
            None
        """
        if not self.active_slider:
            return False

        relative_x = pos[0] - self.rect.x
        slider = (self.brightness_slider if self.active_slider == 'brightness' else self.contrast_slider)

        # Calculate the new position within bounds
        new_x = max(slider['rect'].left,
                    min(relative_x - slider['knob'].width / 2,
                        slider['rect'].right - slider['knob'].width))
        slider['knob'].x = new_x

        # Calculate value based on position
        value_range = (-100, 100) if self.active_slider == 'brightness' else (-127, 127)
        range_min, range_max = value_range
        pos_ratio = (new_x - slider['rect'].left) / (slider['rect'].width - slider['knob'].width)
        new_value = int(range_min + (range_max - range_min) * pos_ratio)

        # Only update if slider['value'] changed
        if slider['value'] != new_value:
            slider['value'] = new_value
            if self.active_slider == 'brightness':
                self.brightness_level = slider['value']
                # Update PlayVideo's opts.brightness if PlayVideo instance is available
                if self.play_video and hasattr(self.play_video, 'opts'):
                    self.play_video.opts.brightness = self.brightness_level
                    self.play_video.opts.adjust_video = True
                    self.play_video.update_video_effects()
            else:
                self.contrast_multiplier = 1 + (slider['value'] / 64.0)
                # Update PlayVideo's opts.contrast if PlayVideo instance is available
                if self.play_video and hasattr(self.play_video, 'opts'):
                    # Convert our contrast multiplier to the range expected by the video processor
                    self.play_video.opts.contrast = slider['value']
                    self.play_video.opts.adjust_video = True
                    self.play_video.update_video_effects()

        return True

    '''
    #
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
        if not self.play_video.opts.adjust_video or self.play_video.vid.frame_surf is None or (self.play_video.opts.brightness == 0 and self.play_video.opts.contrast == 0):
            return None
        #if self.play_video.vid.frame_surf is None:
        #   return None

        # Lock the surface before creating a copy
        self.play_video.vid.frame_surf.lock()
        try:
            frame = self.play_video.vid.frame_surf.copy()
        finally:
            # Always unlock the surface
            self.play_video.vid.frame_surf.unlock()

        # Now apply effects if control panel is visible
        #if self.is_visible:
        #   frame = self.apply_effects(frame)
            #self.apply_effects(frame)
        #return frame
        return None
    '''

    ''' 
    def apply_effects(self, surface):
        """
        Applies brightness and contrast effects to the provided surface. The method handles different combinations of
        brightness and contrast adjustments, such as when only brightness or only contrast changes are required, or
        when both are applied together. Depending on the need, the method internally optimizes for performance by
        either modifying the surface directly or creating a copy to apply the effects sequentially.

        Parameters:
            surface: The target Pygame surface on which brightness and contrast effects will be applied.

        Returns:
            pygame.Surface: The modified surface with the applied brightness and contrast effects.
        """
        if self.brightness_level == 0 and self.contrast_multiplier == 1:
            return surface

        # For brightness changes only, we can use direct blending
        if self.brightness_level != 0 and self.contrast_multiplier == 1:
            # Use the original surface and blend directly
            if self.brightness_level > 0:
                surface.fill((self.brightness_level, self.brightness_level, self.brightness_level),
                             special_flags=pygame.BLEND_RGB_ADD)
            else:
                surface.fill((-self.brightness_level, -self.brightness_level, -self.brightness_level),
                             special_flags=pygame.BLEND_RGB_SUB)
            return surface

        # For contrast-only changes
        if self.brightness_level == 0 and self.contrast_multiplier != 1:
            # Use pygame's built-in per-surface alpha
            surface.set_alpha(int(255 * self.contrast_multiplier))
            return surface

        # If both effects are needed, we need a copy
        effect_surface = surface.copy()

        # Apply contrast first
        effect_surface.set_alpha(int(255 * self.contrast_multiplier))

        # Then brightness
        if self.brightness_level > 0:
            effect_surface.fill((self.brightness_level, self.brightness_level, self.brightness_level),
                                special_flags=pygame.BLEND_RGB_ADD)
        else:
            effect_surface.fill((-self.brightness_level, -self.brightness_level, -self.brightness_level),
                                special_flags=pygame.BLEND_RGB_SUB)

        return effect_surface
    '''

    ''' adjust_brightness_contrast() is appearantly the money shot here.  very very high performance.'''
    @staticmethod
    def adjust_brightness_contrast(frame, brightness, contrast):
        """
        Adjust brightness and contrast of a video frame
        :param frame: Input frame
        :param brightness: Brightness adjustment (-100 to 100)
        :param contrast: Contrast adjustment (-127 to 127)
        :return: Adjusted frame
        """

        # Don't do anything if no adjustment is needed'
        if brightness == 0 and contrast == 0:
            return frame

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

    def toggle_visibility(self):
        """
        Toggles the visibility state.

        This function flips the current visibility state of an object. If the object
        is visible, it will be set to invisible, and vice versa.

        Returns:
            None
        """
        self.is_visible = not self.is_visible

    def set_visible(self, is_visible):
        self.is_visible = is_visible

    def reset_effects(self):
        """
        Resets the brightness and contrast settings to their default values and updates the video
        adjustments as necessary. The method resets associated sliders, clears custom adjustments,
        and ensures that any video-related options are updated to reflect default settings.

        Raises:
            AttributeError: If `self.play_video` does not have the expected attributes when it is not None
        """
        # Reset brightness slider
        self.brightness_slider['knob'].x = self.brightness_slider['rect'].left + self.brightness_slider['rect'].width // 2
        self.brightness_slider['value'] = 0
        self.brightness_level = 0

        # Reset contrast slider
        self.contrast_slider['knob'].x = self.contrast_slider['rect'].left + self.contrast_slider['rect'].width // 2
        self.contrast_slider['value'] = 0
        self.contrast_multiplier = 1.0

        # Turn off video adjustment if both are at default values
        if self.play_video and hasattr(self.play_video, 'opts'):
            self.play_video.opts.brightness = 0
            self.play_video.opts.contrast = 0
            self.play_video.opts.adjust_video = False
            self.play_video.update_video_effects()

