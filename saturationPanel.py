#  saturationPanel.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Class to display a control panel for adjusting saturation factor.
#
import pygame
import numpy as np
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

class saturationPanel:

    def __init__(self, play_video):

        self.play_video = play_video
        Screen = self.play_video.win
        screen_width = Screen.get_width()
        screen_height = Screen.get_height()
        # Panel dimensions and position
        self.panel_height = int(screen_height * 0.15)   		# 15% of screen height
        self.panel_width = int(screen_width * 0.3)  			# 30% of screen width
        self.panel_x = screen_width - self.panel_width - 20  	# 20px padding from right
        self.panel_y = 50  	# 50px from top
        # Create the panel surface with an alpha channel
        self.surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        self.rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        self.surface.set_colorkey((0, 255, 0))
        #
        pygame.draw.rect(
            self.surface,
            DODGERBLUE,
            (0, 0, self.panel_width, self.panel_height),
            1,
            border_radius=8
        )
        #
        self.play_video.apply_gradient(self.surface,
                                 (0, 0, 200),
                                 (0, 0, 100),
                                 self.panel_width,
                                 self.panel_height,
                                 alpha_start=100,
                                 alpha_end=200
        )
        #
        pygame.draw.rect(
            self.surface,
            DODGERBLUE,
            (0, 0, self.panel_width, self.panel_height),
            1,
            border_radius=8
        )
        # Initialize font for title
        self.title_font = pygame.font.Font(None, 48)
        # Saturation parameters
        if self.play_video and hasattr(self.play_video, 'opts'):
            self.is_disabled = True if self.play_video.opts.apply_saturation is False else False
            self.saturation_factor = self.play_video.opts.saturation_factor
        else:
            self.is_disabled = None
            self.saturation_factor = 1.0

        # Slider dimensions
        slider_width = int(self.panel_width * 0.8)
        slider_height = 10
        slider_x = int((self.panel_width - slider_width) / 2)

        # Initialize slider.  Actual value range is from 0.0 to 2.0 however,
        # The slider will use (0-100) for the value. (slider['value'] / 100 ) * 2.0'
        self.saturation_factor_slider = {
            'rect': pygame.Rect(slider_x, 60, slider_width, slider_height),
            'knob': pygame.Rect(slider_x + slider_width // 2, 55, 20, 20),
            'value': self.saturation_factor * 50,
            'dragging': False
        }

        # Button rectangle
        self.reset_button_rect = None
        self.hide_button_rect = None
        # State
        self.is_visible = False
        self.active_slider = None

        self.cuda_devices = cv2.cuda.getCudaEnabledDeviceCount()

    def draw(self, screen):
        if not self.is_visible:
            return

        # Draw the panel background
        screen.blit(self.surface, self.rect)
        title_text = self.title_font.render('Color Saturation Filter', True, HEADING_COLOR)
        screen.blit(title_text, (self.rect.x + (self.panel_width - title_text.get_width()) // 2, self.rect.y + 10))

        # Draw sliders
        for slider, label, value_range in [(self.saturation_factor_slider, "Saturation Strength", (0, 100))]:
            # Draw slider background
            pygame.draw.rect(screen, (100, 100, 100),
                             (self.rect.x + slider['rect'].x, self.rect.y + slider['rect'].y + 75, slider['rect'].width, slider['rect'].height))
            # Draw slider knob
            pygame.draw.rect(screen, DODGERBLUE4,(self.rect.x + slider['knob'].x, self.rect.y + 75 + slider['knob'].y, slider['knob'].width, slider['knob'].height))
            pygame.draw.rect(screen, DODGERBLUE, (self.rect.x + slider['knob'].x, self.rect.y + 75 + slider['knob'].y, slider['knob'].width, slider['knob'].height),
                             2, border_radius=5)

            # Draw label and value
            font = pygame.font.Font(None, 36)
            label_text = font.render(f"{label}: {int(slider['value'])}", True, DODGERBLUE)
            screen.blit(label_text, (self.rect.x + slider['rect'].x, self.rect.y + slider['rect'].y + 50 ))

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
        if not self.is_visible:
            return False

        relative_pos = (pos[0] - self.rect.x, pos[1] - self.rect.y - 75)

        # Check if click is within kernel size slider knob
        saturation_factor_knob_rect = pygame.Rect(
            self.saturation_factor_slider['knob'].x,
            self.saturation_factor_slider['knob'].y,
            self.saturation_factor_slider['knob'].width,
            self.saturation_factor_slider['knob'].height
        )
        # Check laplacian kernel size slider
        if saturation_factor_knob_rect.collidepoint(relative_pos):
            self.active_slider = 'Saturation-Factor'
            self.saturation_factor_slider['dragging'] = True
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
        if self.active_slider:
            self.saturation_factor_slider['dragging'] = False
            self.active_slider = None

    def handle_mouse_motion(self, pos):
        if not self.active_slider:
            return False

        relative_x = pos[0] - self.rect.x
        slider = self.saturation_factor_slider

        # Calculate new position within bounds
        new_x = max(slider['rect'].left,
                    min(relative_x - slider['knob'].width / 2,
                        slider['rect'].right - slider['knob'].width))
        slider['knob'].x = new_x

        # Calculate value based on position
        value_range = (0, 100)
        range_min, range_max = value_range

        pos_ratio = (new_x - slider['rect'].left) / (slider['rect'].width - slider['knob'].width)
        new_value = round(pos_ratio * 100)

        # Only update if value changed
        if slider['value'] != new_value:
            slider['value'] = new_value
            self.saturation_factor = slider['value']
            if self.play_video and hasattr(self.play_video, 'opts'):
                self.play_video.opts.saturation_factor = self.saturation_factor
                self.play_video.update_video_effects()

        return True

    def adjust_saturation(self, frame):
        """
        Adjusts the saturation of a video frame using CUDA acceleration.

        Parameters:
            frame: numpy.ndarray
                The input image frame in BGR color space
            factor: float, optional
                The saturation adjustment factor (default: 2.0)

        Returns:
            numpy.ndarray
                The processed frame with adjusted saturation in BGR color space
        """

        saturation_factor = (self.saturation_factor_slider['value'] / 100.0) * 2.0

        if not hasattr(saturationPanel, '_cuda_saturation_detect_available'):
            saturationPanel._cuda_saturation_detect_available = cv2.cuda.getCudaEnabledDeviceCount() > 0
            if saturationPanel._cuda_saturation_detect_available:
                print("CUDA Saturation Filter initialized")
                print(f"saturation_factor: {saturation_factor}")

        if saturationPanel._cuda_saturation_detect_available:
            try:
                # Create a GPU matrix and upload the frame
                gpu_frame = cv2.cuda_GpuMat()
                gpu_frame.upload(frame)
                # Convert to HSV
                gpu_hsv = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2HSV)
                # Create an identity matrix with the same dimensions for scaling
                zeros = cv2.cuda_GpuMat(gpu_hsv.size(), cv2.CV_8UC3)
                zeros.setTo(0)
                # Create a scaled matrix for the saturation channel
                scaled = cv2.cuda.addWeighted(gpu_hsv, saturation_factor, zeros, 0, 0)
                # Convert back to BGR
                result = cv2.cuda.cvtColor(scaled, cv2.COLOR_HSV2BGR)
                return result.download()

            except cv2.error as e:
                #print(f"CUDA operation failed: {str(e)}")
                # Fallback to CPU version
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation_factor, 0, 255)
                return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    def toggle_visibility(self):
        self.is_visible = not self.is_visible

    def set_visible(self, is_visible):
        self.is_visible = is_visible

    def reset_effects(self):
        self.saturation_factor_slider['knob'].x = self.saturation_factor_slider['rect'].left + self.saturation_factor_slider['rect'].width // 2
        self.saturation_factor_slider['value'] = 50
        self.saturation_factor = 1

        # Turn off video adjustment if both are at default values
        if self.play_video and hasattr(self.play_video, 'opts'):
            self.play_video.opts.saturation_factor = 1.0
            self.play_video.opts.saturation = False
            self.play_video.update_video_effects()
