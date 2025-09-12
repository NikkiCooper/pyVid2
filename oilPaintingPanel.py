#  oilPaintingPanel.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Class to display a control panel for adjusting --oil-size and --oil-dynamics values for use with --oil-painting.

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

class oilPaintingPanel:
    """
    A pygame graphical user interface panel for managing oil painting effect settings, such as
    brush size and dynamics, displayed with sliders and optional reset functionality.

    This class is designed to integrate into pyvidplayer2's video post-processing facility
    allowing users to interact with controls for adjusting oil painting effect attributes. The panel
    can be shown or hidden and reflects user interaction changes in real-time.
    """

    def __init__(self, play_video):
        # Panel dimensions and position
        self.play_video = play_video
        Screen = self.play_video.win
        screen_width = Screen.get_width()
        screen_height = Screen.get_height()

        self.panel_height = int(screen_height * 0.15)  # 15% of screen height
        self.panel_width = int(screen_width * 0.3)  # 30% of screen width
        self.panel_x = screen_width - self.panel_width - 20  # 20px padding from right
        self.panel_y = 50  # 20px from top

        # Create the panel surface with an alpha channel
        self.surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        self.rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        self.surface.set_colorkey((0, 255, 0))

        # Draw translucent panel border
        pygame.draw.rect(
            self.surface,
            DODGERBLUE,
            (0, 0, self.panel_width, self.panel_height),
            1,
            border_radius=8
        )

        # Apply gradient for translucent effect
        self.play_video.apply_gradient(self.surface,
                                  (0, 0, 200),
                                  (0, 0, 100),
                                  self.panel_width,
                                  self.panel_height,
                                  alpha_start=100,
                                  alpha_end=200
                                  )

        # Redraw border after gradient
        pygame.draw.rect(
            self.surface,
            DODGERBLUE,
            (0, 0, self.panel_width, self.panel_height),
            1,
            border_radius=8
        )

        # Initialize font for title
        self.title_font = pygame.font.Font(None, 48)

        # Initialize oil painting parameters
        if self.play_video and hasattr(self.play_video, 'opts'):
            self.is_disabled = True if self.play_video.opts.apply_oil_painting is False else False
            self.oil_size = self.play_video.opts.oil_size
            self.oil_dynamics = self.play_video.opts.oil_dynamics
        else:
            self.is_disabled = None
            self.oil_size = 7
            self.oil_dynamics = 1

        # Slider dimensions
        slider_width = int(self.panel_width * 0.8)
        slider_height = 10
        slider_x = int((self.panel_width - slider_width) / 2)

        # Initialize oil size slider
        self.oil_size_slider = {
            'rect': pygame.Rect(slider_x, 60, slider_width, slider_height),
            'knob': pygame.Rect(slider_x + slider_width // 2, 55, 20, 20),
            'value': self.oil_size,
            'dragging': False
        }

        # Initialize oil dynamics slider
        self.oil_dynamics_slider = {
            'rect': pygame.Rect(slider_x, 120, slider_width, slider_height),
            'knob': pygame.Rect(slider_x + slider_width // 2, 115, 20, 20),
            'value': self.oil_dynamics,
            'dragging': False
        }

        # Button rectangle
        self.reset_button_rect = None
        self.hide_button_rect = None

        # State
        self.is_visible = False
        self.active_slider = None

    def draw(self, screen):
        if not self.is_visible:
            return

        screen.blit(self.surface, self.rect)
        title_text = self.title_font.render('Oil Painting Filter', True, HEADING_COLOR)
        screen.blit(title_text, (self.rect.x + (self.panel_width - title_text.get_width()) // 2, self.rect.y + 10))

        for slider, label, value_range in [(self.oil_size_slider, "Neighbor Size", (5, 15)), (self.oil_dynamics_slider, "Dynamic Ratio", (1, 5))]:
            pygame.draw.rect(screen, (100, 100, 100),
                             (self.rect.x + slider['rect'].x, self.rect.y + slider['rect'].y, slider['rect'].width, slider['rect'].height))
            pygame.draw.rect(screen, DODGERBLUE4, (self.rect.x + slider['knob'].x, self.rect.y + slider['knob'].y, slider['knob'].width, slider['knob'].height))
            pygame.draw.rect(screen, DODGERBLUE, (self.rect.x + slider['knob'].x, self.rect.y + slider['knob'].y, slider['knob'].width, slider['knob'].height),
                             2, border_radius=5)

            font = pygame.font.Font(None, 36)
            label_text = font.render(f"{label}: {slider['value']}", True, DODGERBLUE)
            screen.blit(label_text, (self.rect.x + slider['rect'].x, self.rect.y + slider['rect'].y - 25))

        reset_button_rect = pygame.Rect(self.rect.x + self.panel_width // 2 - 180, self.rect.y + self.panel_height - 100, 120, 45)
        pygame.draw.rect(screen, DODGERBLUE, reset_button_rect, border_radius=10)
        pygame.draw.rect(screen, DODGERBLUE4, reset_button_rect, 1, border_radius=10)

        reset_text = pygame.font.Font(None, 36).render("Reset", True, (255, 255, 255))
        screen.blit(reset_text, (reset_button_rect.x + 25, reset_button_rect.y + 12))

        self.reset_button_rect = reset_button_rect

        # Draw the hide button
        hide_button_rect = pygame.Rect(self.rect.x + self.panel_width // 2 - 40, self.rect.y + self.panel_height - 100, 120, 45)
        pygame.draw.rect(screen, DODGERBLUE, hide_button_rect, border_radius=10)
        pygame.draw.rect(screen, DODGERBLUE4, hide_button_rect, 1, border_radius=10)
        hide_text = pygame.font.Font(None, 36).render("Hide", True, (255, 255, 255))
        screen.blit(hide_text, (hide_button_rect.x + 30, hide_button_rect.y + 12))

        self.hide_button_rect = hide_button_rect

    def handle_mouse_button_down(self, pos):
        if not self.is_visible:
            return False

        # Calculate relative mouse position
        relative_pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)

        # Check if click is within oil size slider knob
        oil_size_knob_rect = pygame.Rect(
            self.oil_size_slider['knob'].x,
            self.oil_size_slider['knob'].y,
            self.oil_size_slider['knob'].width,
            self.oil_size_slider['knob'].height
        )
        if oil_size_knob_rect.collidepoint(relative_pos):
            self.active_slider = 'oil-Size'
            self.oil_size_slider['dragging'] = True
            return True

        # Check if click is within oil dynamics slider knob
        oil_dynamics_knob_rect = pygame.Rect(
            self.oil_dynamics_slider['knob'].x,
            self.oil_dynamics_slider['knob'].y,
            self.oil_dynamics_slider['knob'].width,
            self.oil_dynamics_slider['knob'].height
        )
        if oil_dynamics_knob_rect.collidepoint(relative_pos):
            self.active_slider = 'oil-Dynamics'
            self.oil_dynamics_slider['dragging'] = True
            return True

        # Check if the reset button was clicked
        if self.reset_button_rect and self.reset_button_rect.collidepoint(pos):
            self.reset_effects()
            return True

        if self.hide_button_rect and self.hide_button_rect.collidepoint(pos):
            self.set_visible(False)
            return True

        return False

    def handle_mouse_button_up(self):
        """
        Handles the mouse button-up event for interactive sliders.

        This method is used to update the state of the slider components when
        the mouse button is released. It resets the dragging state of the
        slider and clears the current active slider.

        Raises:
            None
        """
        if self.active_slider:
            if self.active_slider == 'oil-Size':
                self.oil_size_slider['dragging'] = False
            else:
                self.oil_dynamics_slider['dragging'] = False
            self.active_slider = None

    def handle_mouse_motion(self, pos):
        """
        Handles the movement of the mouse when interacting with a slider. This method is
        responsible for determining the position of a slider's knob, updating the slider's
        value, and applying the respective changes to external systems (e.g., video effects)
        if necessary.

        Parameters:
            pos (Tuple[int, int]): The current position of the mouse as (x, y) coordinates.

        Returns:
            bool: True if the slider's value or state was updated, False otherwise.
        """
        if not self.active_slider:
            return False

        relative_x = pos[0] - self.rect.x
        slider = (self.oil_size_slider if self.active_slider == 'oil-Size' else self.oil_dynamics_slider)

        # Calculate new position within bounds
        new_x = max(slider['rect'].left,
                    min(relative_x - slider['knob'].width / 2,
                        slider['rect'].right - slider['knob'].width))
        slider['knob'].x = new_x

        # Calculate value based on position
        value_range = (5, 15) if self.active_slider == 'oil-Size' else (1, 5)
        range_min, range_max = value_range

        pos_ratio = (new_x - slider['rect'].left) / (slider['rect'].width - slider['knob'].width)
        new_value = int(range_min + (range_max - range_min) * pos_ratio)

        # Only update if value changed
        if slider['value'] != new_value:
            slider['value'] = new_value
            if self.active_slider == 'oil-Size':
                self.oil_size = slider['value']
                # Update PlayVideo's opts.brightness if PlayVideo instance is available
                if self.play_video and hasattr(self.play_video, 'opts'):
                    self.play_video.opts.oil_size = self.oil_size
                    self.play_video.update_video_effects()
            else:
                self.oil_dynamics =  slider['value']
                # Update PlayVideo's opts.edge_lower if PlayVideo instance is available
                if self.play_video and hasattr(self.play_video, 'opts'):
                    # Convert our edge_lower value to the range expected by the video processor
                    self.play_video.opts.oil_dynamics = self.oil_dynamics
                    self.play_video.update_video_effects()

        return True

    def Apply_Effects(self, frame):
        """
        Applies an oil painting effect to the provided frame.

        This method utilizes OpenCV's oilPainting function to apply the effect,
        using the values obtained from the oil_size_slider and oil_dynamics_slider.

        Parameters:
            frame (Any): The image or frame to which the oil painting effect
            should be applied.

        Returns:
            Any: The processed frame with the oil painting effect applied.
        """
        return cv2.xphoto.oilPainting( frame,
                                       int(self.oil_size_slider['value']),
                                       int(self.oil_dynamics_slider['value'])
               )

    def toggle_visibility(self):
        """
        Toggles the visibility state by inverting the current value of is_visible.

        Returns
        -------
        None
        """
        self.is_visible = not self.is_visible

    def set_visible(self, is_visible):
        self.is_visible = is_visible

    def reset_effects(self):
        """
        Resets the effects applied to the video to their default states. This method adjusts
        the sliders controlling the "oil size" and "oil dynamics" values back to their initial
        positions and values. If `play_video` is active and carries specific options, it updates
        the video effects correspondingly by disabling the oil painting effect and refreshing
        the video.

        Raises:
            None
        """
        #Reset oil_size_slider
        self.oil_size_slider['knob'].x = self.oil_size_slider['rect'].left + self.oil_size_slider['rect'].width // 2
        self.oil_size_slider['value'] = 7
        self.oil_size = 7

        # Reset oil_dynamics_slider
        self.oil_dynamics_slider['knob'].x = self.oil_dynamics_slider['rect'].left + self.oil_dynamics_slider['rect'].width // 2
        self.oil_dynamics_slider['value'] = 1
        self.oil_dynamics = 1

        # Turn off video adjustment if both are at default values
        if self.play_video and hasattr(self.play_video, 'opts'):
            self.play_video.opts.oil_size = 7
            self.play_video.opts.oil_dynamics = 1
            self.play_video.opts.oil_painting = False
            self.play_video.update_video_effects()
