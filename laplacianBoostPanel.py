#  laplacianBoostPanel.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Class to display a control panel for adjusting laplacian Boost values
#
import pygame
import cv2
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

class laplacianBoostPanel:

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
        # Laplacian Boost parameters
        if self.play_video and hasattr(self.play_video, 'opts'):
            self.is_disabled = True if self.play_video.opts.apply_laplacian is False else False
            self.laplacian_kernel_size = self.play_video.opts.laplacian_kernel_size
            self.laplacian_boost_strength = self.play_video.opts.laplacian_boost_strength
        else:
            self.is_disabled = None
            self.laplacian_kernel_size = 1
            self.laplacian_boost_strength = 9.5

        # Slider dimensions
        slider_width = int(self.panel_width * 0.8)
        slider_height = 10
        slider_x = int((self.panel_width - slider_width) / 2)

        # Initialize sliders
        self.laplacian_kernel_size_slider = {
            'rect': pygame.Rect(slider_x, 60, slider_width, slider_height),
            'knob': pygame.Rect(slider_x + slider_width // 2, 55, 20, 20),
            'value': self.laplacian_kernel_size,
            'dragging': False
        }
        self.laplacian_boost_strength_slider = {
            'rect': pygame.Rect(slider_x, 120, slider_width, slider_height),
            'knob': pygame.Rect(slider_x + slider_width // 2, 115, 20, 20),
            'value': self.laplacian_boost_strength,
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
        title_text = self.title_font.render('Laplacian Boost Filter', True, HEADING_COLOR)
        screen.blit(title_text, (self.rect.x + (self.panel_width - title_text.get_width()) // 2, self.rect.y + 10))

        # Draw sliders
        for slider, label, value_range in [(self.laplacian_kernel_size_slider, "Kernel Size", (1, 5)), (self.laplacian_boost_strength_slider, "Boost Strength", (1, 10))]:
            # Draw slider background
            pygame.draw.rect(screen, (100, 100, 100),
                             (self.rect.x + slider['rect'].x, self.rect.y + slider['rect'].y, slider['rect'].width, slider['rect'].height))
            # Draw slider knob
            pygame.draw.rect(screen, DODGERBLUE4,(self.rect.x + slider['knob'].x, self.rect.y + slider['knob'].y, slider['knob'].width, slider['knob'].height))
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
        if not self.is_visible:
            return False

        relative_pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)

        # Check if click is within kernel size slider knob
        kernel_size_knob_rect = pygame.Rect(
            self.laplacian_kernel_size_slider['knob'].x,
            self.laplacian_kernel_size_slider['knob'].y,
            self.laplacian_kernel_size_slider['knob'].width,
            self.laplacian_kernel_size_slider['knob'].height
        )
        # Check laplacian kernel size slider
        if kernel_size_knob_rect.collidepoint(relative_pos):
            self.active_slider = 'Kernel-Size'
            self.laplacian_kernel_size_slider['dragging'] = True
            return True

        # Check if click is within laplacian_boost_strength_slider knob
        boost_strength_knob_rect = pygame.Rect(
            self.laplacian_boost_strength_slider['knob'].x,
            self.laplacian_boost_strength_slider['knob'].y,
            self.laplacian_boost_strength_slider['knob'].width,
            self.laplacian_boost_strength_slider['knob'].height
        )
        # Check laplacian_boost_strength slider
        if boost_strength_knob_rect.collidepoint(relative_pos):
            self.active_slider = 'Boost-Strength'
            self.laplacian_boost_strength_slider['dragging'] = True
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
            if self.active_slider == 'Kernel-Size':
                self.laplacian_kernel_size_slider['dragging'] = False
            else:
                self.laplacian_boost_strength_slider['dragging'] = False
            self.active_slider = None

    def handle_mouse_motion(self, pos):
        if not self.active_slider:
            return False

        relative_x = pos[0] - self.rect.x
        slider = (self.laplacian_kernel_size_slider if self.active_slider == 'Kernel-Size' else self.laplacian_boost_strength_slider)

        # Calculate new position within bounds
        new_x = max(slider['rect'].left,
                    min(relative_x - slider['knob'].width / 2,
                        slider['rect'].right - slider['knob'].width))
        slider['knob'].x = new_x

        # Calculate value based on position
        value_range = (1, 5) if self.active_slider == 'Kernel-Size' else (1, 10)
        range_min, range_max = value_range

        pos_ratio = (new_x - slider['rect'].left) / (slider['rect'].width - slider['knob'].width)
        if self.active_slider == 'Kernel-Size':
            new_value = int(range_min + (range_max - range_min) * pos_ratio)
        else:
            new_value = round(range_min + (range_max - range_min) * pos_ratio, 2)

        # Only update if value changed
        if slider['value'] != new_value:
            slider['value'] = new_value
            if self.active_slider == 'Kernel-Size':
                self.laplacian_kernel_size = slider['value']
                # Update PlayVideo's opts.brightness if PlayVideo instance is available
                if self.play_video and hasattr(self.play_video, 'opts'):
                    self.play_video.opts.laplacian_kernel_size = self.laplacian_kernel_size
                    self.play_video.update_video_effects()
            else:
                self.laplacian_boost_strength =  round(slider['value'] / 10.0, 2)
                # Update PlayVideo's opts.laplacian_boost_strength if PlayVideo instance is available
                if self.play_video and hasattr(self.play_video, 'opts'):
                    # Convert our laplacian_boost_strength value to the range expected by the video processor
                    self.play_video.opts.laplacian_boost_strength = self.laplacian_boost_strength
                    self.play_video.update_video_effects()

        return True

    def laplacian_boost(self, image):
        if not isinstance(image, np.ndarray):
            raise TypeError("Input must be a NumPy ndarray")

        self.cuda_devices = cv2.cuda.getCudaEnabledDeviceCount()
        if not hasattr(laplacianBoostPanel, '_cuda_laplacianBoost_available'):
            laplacianBoostPanel._cuda_laplacianBoost_available = self.cuda_devices > 0
            if laplacianBoostPanel._cuda_laplacianBoost_available:
                print(f"CUDA-based Laplacian boost initialized and available.")
            else:
                print(f"CUDA-based Laplacian boost is not available. Using CPU instead.")

        if self.cuda_devices > 0:
            return self.cuda_laplacian_boost(image)
        else:
            return self.cpu_laplacian_boost(image)

    def enhanced_cuda_laplacian_boost(self, image):
        """
        Applies an enhanced CUDA-based Laplacian boost filter to an image.

        This function uses GPU acceleration to process the input image in a series of
        steps: smoothing the image to reduce noise, applying a Laplacian filter for
        edge detection, and blending the Laplacian result with the original image
        using a configurable boost strength. This technique enhances the edges in the
        image while maintaining overall clarity.

        Parameters:
        image: numpy.ndarray
            The input image to process, provided as a NumPy array.

        Returns:
        numpy.ndarray
            The processed image with enhanced edges, returned as a NumPy array.

        Raises:
        cv2.error
            If any OpenCV CUDA operations fail.
        """
        boost_strength = 0.05 + self.laplacian_boost_strength_slider['value'] * 0.1
        # Upload to GPU once
        gpu_image = cv2.cuda_GpuMat()
        gpu_image.upload(image)
        # First pass - smooth slightly to reduce noise
        gaussian = cv2.cuda.createGaussianFilter(cv2.CV_8UC3, cv2.CV_8UC3, (3, 3), 0.5)
        smoothed = gaussian.apply(gpu_image)
        # Then apply Laplacian with kernel size 1
        gray = cv2.cuda.cvtColor(smoothed, cv2.COLOR_BGR2GRAY)
        lap_filter = cv2.cuda.createLaplacianFilter(cv2.CV_8UC1, cv2.CV_8UC1, 1)
        lap = lap_filter.apply(gray)
        # Convert back to BGR and blend
        lap_bgr = cv2.cuda.cvtColor(lap, cv2.COLOR_GRAY2BGR)
        result = cv2.cuda.addWeighted(gpu_image, 1.0, lap_bgr, boost_strength, 0)
        return result.download()

    def cuda_laplacian_boost(self, image):
        """
        Applies a Laplacian filter to enhance edges in an input image using CUDA, and blends the result
        with the original image for a boosted effect.

        This method performs the following operations:
        1. Adjusts the boost strength based on a slider value.
        2. Uploads the input image to the GPU.
        3. Converts the image to grayscale.
        4. Applies a fixed 3x3 Laplacian kernel to the grayscale image to detect edges.
        5. Takes the absolute value of the Laplacian filter result.
        6. Converts the processed image back to BGR format.
        7. Blends the processed image with the original using the computed boost strength.
        8. Downloads the final result from the GPU to the host system.

        Parameters:
        image: numpy.ndarray
            The input image to be processed. It must be in BGR color format.

        Returns:
        numpy.ndarray
            The processed image after applying the Laplacian filter and boost blending.
        """
        #boost_strength = round((self.laplacian_boost_strength_slider['value'] / 10.0) ** 2, 2)
        # maps  slider values 1-10 to 0.15-1.05  = linear scale
        boost_strength = 0.05 + self.laplacian_boost_strength_slider['value'] * 0.1

        # Upload to GPU
        gpu_image = cv2.cuda_GpuMat()
        gpu_image.upload(image)
        # Convert to grayscale
        gpu_gray = cv2.cuda.cvtColor(gpu_image, cv2.COLOR_BGR2GRAY)
        # Use fixed 3x3 Laplacian kernel
        lap_filter = cv2.cuda.createLaplacianFilter(cv2.CV_8UC1, cv2.CV_8UC1, 3)
        # Apply filter
        gpu_lap = lap_filter.apply(gpu_gray)
        gpu_lap_abs = cv2.cuda.abs(gpu_lap)
        gpu_lap_bgr = cv2.cuda.cvtColor(gpu_lap_abs, cv2.COLOR_GRAY2BGR)
        # Blend with original
        gpu_result = cv2.cuda.addWeighted(gpu_image, 1.0, gpu_lap_bgr, boost_strength, 0)
        # Download result
        result = gpu_result.download()
        return result

    def cpu_laplacian_boost(self, image):
        """
        Applies Laplacian boosting to enhance image sharpness.

        This function converts the input image to grayscale, calculates the Laplacian
        to detect edges, and then uses the Laplacian result as a boost to enhance
        the original image. The strength of this enhancement is controlled by both
        a kernel size and a boost strength parameter, which are derived from
        the associated UI sliders.

        Parameters:
        image: numpy.ndarray
            The input image to be enhanced, provided as a NumPy array.

        Returns:
        numpy.ndarray
            The sharpened image as a NumPy array.

        Raises:
        ValueError
            If the input image does not meet the expected requirements or dimensions.
        """
        kernel_size = int(self.laplacian_kernel_size_slider['value'])
        # maps  slider values 1-10 to 0.15-1.05  = linear scale
        boost_strength = 0.05 + self.laplacian_boost_strength_slider['value'] * 0.1
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        lap = cv2.convertScaleAbs(lap)
        lap_bgr = cv2.cvtColor(lap, cv2.COLOR_GRAY2BGR)
        sharpened = cv2.addWeighted(image, kernel_size, lap_bgr, boost_strength, 0)
        return sharpened

    def toggle_visibility(self):
        self.is_visible = not self.is_visible

    def set_visible(self, is_visible):
        self.is_visible = is_visible

    def reset_effects(self):
        self.laplacian_kernel_size_slider['knob'].x = self.laplacian_kernel_size_slider['rect'].left + self.laplacian_kernel_size_slider['rect'].width // 2
        self.laplacian_kernel_size_slider['value'] = 1
        self.laplacian_kernel_size = 1

        # Reset oil_dynamics_slider
        self.laplacian_boost_strength_slider['knob'].x = self.laplacian_boost_strength_slider['rect'].left + self.laplacian_boost_strength_slider['rect'].width // 2
        self.laplacian_boost_strength_slider['value'] = 9.5
        self.laplacian_boost_strength = 9.5

        # Turn off video adjustment if both are at default values
        if self.play_video and hasattr(self.play_video, 'opts'):
            self.play_video.opts.laplacian_kernel_size = 1
            self.play_video.opts.laplacian_boost_strength = 9.5
            self.play_video.opts.laplacian = False
            self.play_video.update_video_effects()
