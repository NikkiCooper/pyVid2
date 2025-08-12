
import cv2
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

class sepiaPanel:
    def __init__(self, play_video):
        self.play_video = play_video
        self.opts = self.play_video.opts

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
            self.is_disabled = True if self.play_video.opts.apply_sepia is False else False
            self.sepia_preset = None

            self.sepia_intensity = self.play_video.opts.sepia_intensity

        else:
            self.is_disabled = None
            self.sepia_preset =  2
            self.sepia_intensity = 1.0

        # Slider dimensions
        slider_width = int(self.panel_width * 0.8)
        slider_height = 10
        slider_x = int((self.panel_width - slider_width) / 2)

        # Initialize sliders
        self.sepia_preset_slider = {
            'rect': pygame.Rect(slider_x, 60, slider_width, slider_height),
            'knob': pygame.Rect(slider_x + slider_width // 2, 55, 20, 20),
            'value': self.sepia_preset,
            'dragging': False
        }

        self.sepia_intensity_slider = {
            'rect': pygame.Rect(slider_x, 120, slider_width, slider_height),
            'knob': pygame.Rect(slider_x + slider_width // 2, 115, 20, 20),
            'value': round(self.sepia_intensity * 10.0, 1),
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
        title_text = self.title_font.render('Super-Sepia Filter', True, HEADING_COLOR)
        screen.blit(title_text, (self.rect.x + (self.panel_width - title_text.get_width()) // 2, self.rect.y + 10))

        preset = self.play_video.opts.sepia_preset
        presetStr = f"{'Preset: '}{preset}"

        # Draw sliders
        for slider, label, value_range in [(self.sepia_preset_slider, f"{presetStr}", (0, 3)), (self.sepia_intensity_slider, "Intensity", (0, 10))]:
            # Draw slider background
            pygame.draw.rect(screen, (100, 100, 100),
                             (self.rect.x + slider['rect'].x, self.rect.y + slider['rect'].y, slider['rect'].width, slider['rect'].height))
            # Draw slider knob
            pygame.draw.rect(screen, DODGERBLUE4, (self.rect.x + slider['knob'].x, self.rect.y + slider['knob'].y, slider['knob'].width, slider['knob'].height))
            pygame.draw.rect(screen, DODGERBLUE, (self.rect.x + slider['knob'].x, self.rect.y + slider['knob'].y, slider['knob'].width, slider['knob'].height),
                             2, border_radius=5)

            # Draw label and value
            font = pygame.font.Font(None, 36)
            label_text = font.render(f"{label} {round(slider['value'] / 10.0, 1) if label == 'Intensity' else ''}", True, DODGERBLUE)
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
        sepia_preset_knob_rect = pygame.Rect(
            self.sepia_preset_slider['knob'].x,
            self.sepia_preset_slider['knob'].y,
            self.sepia_preset_slider['knob'].width,
            self.sepia_preset_slider['knob'].height
        )
        # Check speia_preset_slider
        if sepia_preset_knob_rect.collidepoint(relative_pos):
            self.active_slider = 'sepia-Preset'
            self.sepia_preset_slider['dragging'] = True
            return True

        # Check if click is within sepia_intensity slider knob
        sepia_intensity_knob_rect = pygame.Rect(
            self.sepia_intensity_slider['knob'].x,
            self.sepia_intensity_slider['knob'].y,
            self.sepia_intensity_slider['knob'].width,
            self.sepia_intensity_slider['knob'].height
        )
        if sepia_intensity_knob_rect.collidepoint(relative_pos):
            self.active_slider = 'sepia-Intensity'
            self.sepia_intensity_slider['dragging'] = True
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
        Handles the event of the mouse button being released.

        This method manages the state of the active slider when the mouse button
        is released. It determines which slider (upper or lower edge) is currently
        active and updates its dragging state accordingly. Once processed, it
        resets the active slider to None.

        Raises:
            None
        """
        if self.active_slider:
            if self.active_slider == 'sepia-Preset':
                self.sepia_preset_slider['dragging'] = False
            else:
                self.sepia_intensity_slider['dragging'] = False
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
        slider = (self.sepia_preset_slider if self.active_slider == 'sepia-Preset' else self.sepia_intensity_slider)

        # Calculate the new position within bounds
        new_x = max(slider['rect'].left,
                    min(relative_x - slider['knob'].width / 2,
                        slider['rect'].right - slider['knob'].width))
        slider['knob'].x = new_x

        # Calculate value based on position
        value_range = (0, 3) if self.active_slider == 'sepia-Preset' else (0, 10)
        range_min, range_max = value_range

        pos_ratio = (new_x - slider['rect'].left) / (slider['rect'].width - slider['knob'].width)
        new_value = int(range_min + (range_max - range_min) * pos_ratio)

        # Only update if the value changed
        if slider['value'] != new_value:
            slider['value'] = new_value
            if self.active_slider == 'sepia-Preset':
                self.sepia_preset = int(slider['value'])
                # Update play_video opts.sepia_preset if play_video instance is available
                if self.play_video and hasattr(self.play_video, 'opts'):
                    self.play_video.opts.sepia_preset = self.play_video.opts.SepiaPresetList[self.sepia_preset]
                    self.play_video.update_video_effects()
            else:
                self.sepia_intensity = round(slider['value'] / 10.0, 1)
                # Update play_video's opts.sepia_intensity if play_video's instance is available
                if self.play_video and hasattr(self.play_video, 'opts'):
                    # Convert our sepia_intensity value to the range expected by the video processor
                    self.play_video.opts.sepia_intensity = self.sepia_intensity
                    self.play_video.update_video_effects()

        return True

    def super_sepia(self, frame):
        #preset='classic', intensity=1.0
        """
        Applies an adjustable sepia-tone effect using CUDA if available.

        Args:
            frame (numpy.ndarray): Input BGR image frame
            preset (str): 'classic', 'warm', 'cool', or 'vintage'
            intensity (float): Effect intensity from 0.0 to 1.0

        Returns:
            numpy.ndarray: Sepia-toned image frame
        """
        # Preset weights for different looks
        preset = self.play_video.opts.sepia_preset
        intensity = self.play_video.opts.sepia_intensity

        presets = {
            'classic': {
                'r': (0.393, 0.769, 0.189),
                'g': (0.349, 0.686, 0.168),
                'b': (0.272, 0.534, 0.131)
            },
            'warm': {
                'r': (0.443, 0.769, 0.189),
                'g': (0.349, 0.686, 0.168),
                'b': (0.272, 0.534, 0.131)
            },
            'cool': {
                'r': (0.393, 0.769, 0.189),
                'g': (0.349, 0.686, 0.168),
                'b': (0.272, 0.534, 0.231)
            },
            'vintage': {
                'r': (0.493, 0.769, 0.189),
                'g': (0.349, 0.786, 0.168),
                'b': (0.272, 0.534, 0.131)
            }
        }

        if not hasattr(sepiaPanel, '_cuda_super_sepia_available'):
            sepiaPanel._cuda_super_sepia_available = cv2.cuda.getCudaEnabledDeviceCount() > 0
            if sepiaPanel._cuda_super_sepia_available:
                print("CUDA Super-Sepia effect initialized")

        # Get weights for the selected preset
        weights = presets.get(preset, presets['classic'])

        # Apply an intensity factor to the color transformation
        w = weights
        if intensity != 1.0:
            # Interpolate between the original image (intensity=0) and full effect (intensity=1)
            w = {
                'r': tuple(i * intensity for i in weights['r']),
                'g': tuple(i * intensity for i in weights['g']),
                'b': tuple(i * intensity for i in weights['b'])
            }

        try:
            if sepiaPanel._cuda_super_sepia_available:                # Upload to GPU
                gpu_frame = cv2.cuda_GpuMat()
                gpu_frame.upload(frame)

                # Split into channels
                b, g, r = cv2.cuda.split(gpu_frame)

                # Apply sepia weights with the selected preset
                sepia_b = cv2.cuda.addWeighted(r, w['b'][0], g, w['b'][1], 0)
                sepia_b = cv2.cuda.addWeighted(sepia_b, 1.0, b, w['b'][2], 0)

                sepia_g = cv2.cuda.addWeighted(r, w['g'][0], g, w['g'][1], 0)
                sepia_g = cv2.cuda.addWeighted(sepia_g, 1.0, b, w['g'][2], 0)

                sepia_r = cv2.cuda.addWeighted(r, w['r'][0], g, w['r'][1], 0)
                sepia_r = cv2.cuda.addWeighted(sepia_r, 1.0, b, w['r'][2], 0)

                # Download results from GPU
                sepia_b = sepia_b.download()
                sepia_g = sepia_g.download()
                sepia_r = sepia_r.download()

                # Merge channels
                return cv2.merge([sepia_b, sepia_g, sepia_r])

            # CPU fallback
            sepia_matrix = np.array([
                w['b'],
                w['g'],
                w['r']
            ])
            return cv2.transform(frame, sepia_matrix)

        except cv2.error:
            sepiaPanel._cuda_super_sepia_available = False
            # CPU fallback
            sepia_matrix = np.array([
                w['b'],
                w['g'],
                w['r']
            ])
            return cv2.transform(frame, sepia_matrix)

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
        self.sepia_preset_slider['knob'].x = self.sepia_preset_slider['rect'].left + self.sepia_preset_slider['rect'].width // 2
        self.sepia_preset_slider['value'] = 2
        self.sepia_preset = 2

        # Reset edge_lower slider
        self.sepia_intensity_slider['knob'].x = self.sepia_intensity_slider['rect'].left + self.sepia_intensity_slider['rect'].width // 2
        self.sepia_intensity_slider['value'] = 1.0
        self.sepia_intensity = 1.0

        # Turn off video adjustment if both are at default values
        if self.play_video and hasattr(self.play_video, 'opts'):
            self.play_video.opts.sepia_preset = self.play_video.opts.SepiaPresetList[2]
            self.play_video.opts.sepia_intensity = 1.0
            self.play_video.opts.sepia = False
            self.play_video.update_video_effects()
