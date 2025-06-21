import time
import pygame
import cv2
import numpy as np

import inspect

DODGERBLUE = (30, 144, 255)
DODGERBLUE4 = (16, 78, 139)

def bilateral_debug(msg):
    frame = inspect.currentframe().f_back
    line_no = frame.f_lineno
    func_name = frame.f_code.co_name
    print(f"BILATERAL_DEBUG [{func_name}:{line_no}] {msg}")


class DropDown:
    def __init__(self, x, y, width, height, options, initial_selection=0, scaling_factor=1.0):
        # Apply scaling to all dimensions
        self.scaling_factor = scaling_factor
        self.rect = pygame.Rect(int(x * scaling_factor), int(y * scaling_factor),
                                int(width * scaling_factor), int(height * scaling_factor))
        self.options = options
        self.selected_index = initial_selection
        self.is_open = False
        self.option_height = int(height * scaling_factor)
        self.max_visible_options = 10

        # Fonts - scale font size
        try:
            import os
            font_dir = os.path.expanduser("~/.local/share/pyVid/fonts/")
            font_size = max(12, int(16 * scaling_factor))
            self.font = pygame.font.Font(font_dir + 'Arial_Bold.ttf', font_size)
        except (IOError, FileNotFoundError):
            font_size = max(12, int(18 * scaling_factor))
            self.font = pygame.font.Font(None, font_size)

        # Colors
        self.bg_color = DODGERBLUE
        self.selected_color = (100, 149, 237)
        self.hover_color = (135, 206, 250)
        self.border_color = (200, 200, 200)
        self.text_color = (0, 0, 0)
        self.disabled_color = (180, 180, 180)

        # Calculate dropdown area
        visible_options = min(len(self.options), self.max_visible_options)
        self.dropdown_rect = pygame.Rect(
            self.rect.x, self.rect.y + self.rect.height,
            self.rect.width,
                         visible_options * self.option_height
        )

    def get_selected_option(self):
        """Return the currently selected option"""
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index]
        return None

    def set_selected_option(self, option_text):
        """Set the selected option by text"""
        try:
            self.selected_index = self.options.index(option_text)
        except ValueError:
            pass

    def handle_event(self, event):
        """Handle dropdown events - return True if selection changed"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if self.rect.collidepoint(mouse_pos):
                self.is_open = not self.is_open
                return False

            elif self.is_open and self.dropdown_rect.collidepoint(mouse_pos):
                relative_y = mouse_pos[1] - self.dropdown_rect.y
                clicked_index = relative_y // self.option_height

                if 0 <= clicked_index < len(self.options):
                    old_selection = self.selected_index
                    self.selected_index = clicked_index
                    self.is_open = False
                    return self.selected_index != old_selection
            else:
                if self.is_open:
                    self.is_open = False

        return False

    def draw(self, surface):
        """Draw the dropdown"""
        # Draw main button
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, max(1, int(2 * self.scaling_factor)))

        # Draw selected text
        if 0 <= self.selected_index < len(self.options):
            text = self.options[self.selected_index]
        else:
            text = "Select..."

        text_surface = self.font.render(text, True, self.text_color)
        text_x = self.rect.x + int(8 * self.scaling_factor)
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))

        # Draw dropdown arrow - scaled
        arrow_size = int(4 * self.scaling_factor)
        arrow_x = self.rect.right - int(20 * self.scaling_factor)
        arrow_y = self.rect.centery
        if self.is_open:
            points = [
                (arrow_x, arrow_y + arrow_size // 2),
                (arrow_x - arrow_size, arrow_y - arrow_size // 2),
                (arrow_x + arrow_size, arrow_y - arrow_size // 2)
            ]
        else:
            points = [
                (arrow_x, arrow_y - arrow_size // 2),
                (arrow_x - arrow_size, arrow_y + arrow_size // 2),
                (arrow_x + arrow_size, arrow_y + arrow_size // 2)
            ]
        pygame.draw.polygon(surface, self.text_color, points)

        # Draw dropdown options if open
        if self.is_open:
            pygame.draw.rect(surface, self.bg_color, self.dropdown_rect)
            pygame.draw.rect(surface, self.border_color, self.dropdown_rect, max(1, int(2 * self.scaling_factor)))

            for i, option in enumerate(self.options):
                if i >= self.max_visible_options:
                    break

                option_rect = pygame.Rect(
                    self.dropdown_rect.x,
                    self.dropdown_rect.y + i * self.option_height,
                    self.dropdown_rect.width,
                    self.option_height
                )

                if i == self.selected_index:
                    pygame.draw.rect(surface, self.selected_color, option_rect)

                option_surface = self.font.render(option, True, self.text_color)
                option_x = option_rect.x + int(8 * self.scaling_factor)
                option_y = option_rect.y + (option_rect.height - option_surface.get_height()) // 2
                surface.blit(option_surface, (option_x, option_y))

                if i < len(self.options) - 1 and i < self.max_visible_options - 1:
                    pygame.draw.line(surface, self.border_color,
                                     (option_rect.x, option_rect.bottom),
                                     (option_rect.right, option_rect.bottom))


class SpinBox:
    def __init__(self, x, y, width, height, label, min_val, max_val, initial_value=None, step=1, decimals=0, scaling_factor=1.0):
        self.name = label.replace(":", "").lower() if isinstance(label, str) else "spinbox"
        self.scaling_factor = scaling_factor

        # Apply scaling to all dimensions
        scaled_x = int(x * scaling_factor)
        scaled_y = int(y * scaling_factor)
        scaled_width = int(width * scaling_factor)
        scaled_height = int(height * scaling_factor)

        self.rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        self.label = ""
        self.original_label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_value if initial_value is not None else min_val
        self.step = step
        self.decimals = decimals
        self.active = False
        self.text_input = ""

        # Create properly scaled components
        self.button_width = int(20 * scaling_factor)
        self.input_width = scaled_width - self.button_width

        self.input_rect = pygame.Rect(scaled_x, scaled_y, self.input_width, scaled_height)
        self.up_button = pygame.Rect(scaled_x + self.input_width, scaled_y,
                                     self.button_width, scaled_height // 2)
        self.down_button = pygame.Rect(scaled_x + self.input_width, scaled_y + scaled_height // 2,
                                       self.button_width, scaled_height - (scaled_height // 2))

        # Scale fonts
        try:
            import os
            font_dir = os.path.expanduser("~/.local/share/pyVid/fonts/")
            font_size = max(12, int(17 * scaling_factor))
            self.value_font = pygame.font.Font(font_dir + 'Arial_Bold.ttf', font_size)
        except (IOError, FileNotFoundError):
            font_size = max(12, int(22 * scaling_factor))
            self.value_font = pygame.font.Font(None, font_size)

    def get_current_value(self):
        # Special handling for intensity - convert percentage to 0-1 range
        if 'intensity' in self.name.lower():
            return round(self.value / 100.0, 1)  # Convert percentage to intensity
        return self.value

    def set_value(self, new_value):
        self.value = max(self.min_val, min(self.max_val, new_value))
        if self.active:
            self.active = False
            self.text_input = ""

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if self.up_button.collidepoint(mouse_pos):
                old_value = self.value
                self.value = min(self.max_val, self.value + self.step)
                return self.value != old_value

            elif self.down_button.collidepoint(mouse_pos):
                old_value = self.value
                self.value = max(self.min_val, self.value - self.step)
                return self.value != old_value

            elif self.input_rect.collidepoint(mouse_pos):
                self.active = True
                self.text_input = str(self.value)

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                old_value = self.value
                self._apply_text_input()
                self.active = False
                return self.value != old_value
            elif event.key == pygame.K_TAB:
                old_value = self.value
                self._apply_text_input()
                self.active = False
                return self.value != old_value
            elif event.key == pygame.K_ESCAPE:
                self.active = False
                self.text_input = ""
            elif event.key == pygame.K_BACKSPACE:
                self.text_input = self.text_input[:-1]
            else:
                if event.unicode and (event.unicode.isdigit() or event.unicode == '.' or event.unicode == '-'):
                    self.text_input += event.unicode

        return False

    def _apply_text_input(self):
        try:
            new_value = float(self.text_input) if '.' in self.text_input else int(self.text_input)

            # Special validation for diameter parameter (must be odd, min 3)
            if self.name == 'diameter':
                new_value = self._validate_diameter(new_value)

            # Special handling for intensity - convert percentage to 0-1 range
            elif 'intensity' in self.name.lower():
                new_value = self._validate_intensity_percentage(new_value)

            self.value = max(self.min_val, min(self.max_val, new_value))
        except ValueError:
            pass

    def _validate_intensity_percentage(self, value):
        """Validate percentage (0-100) and keep it as percentage for SpinBox"""
        # Clamp to percentage range and return as percentage
        percentage = max(0, min(100, value))
        return percentage  # ← Keep as percentage!

    def _validate_diameter(self, value):
        """Ensure diameter is odd and >= 3"""
        d = int(value)
        if d < 3:
            return 3
        if d % 2 == 0:  # Even number - round up to next odd
            return d + 1
        return d

    def draw(self, screen):
        # Scale arrow sizes
        arrow_size = max(2, int(4 * self.scaling_factor))
        active_color = (150, 180, 190)
        text_color = (0, 0, 0)
        border_width = max(1, int(1 * self.scaling_factor))

        # Draw input field
        input_bg = active_color if self.active else DODGERBLUE
        pygame.draw.rect(screen, input_bg, self.input_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.input_rect, border_width)

        # Draw up button with scaled arrow
        pygame.draw.rect(screen, DODGERBLUE4, self.up_button)
        pygame.draw.rect(screen, (200, 200, 200), self.up_button, border_width)
        points = [
            (self.up_button.centerx, self.up_button.y + arrow_size),
            (self.up_button.centerx - arrow_size, self.up_button.bottom - arrow_size),
            (self.up_button.centerx + arrow_size, self.up_button.bottom - arrow_size)
        ]
        pygame.draw.polygon(screen, text_color, points)

        # Draw down button with scaled arrow
        pygame.draw.rect(screen, DODGERBLUE4, self.down_button)
        pygame.draw.rect(screen, (200, 200, 200), self.down_button, border_width)
        points = [
            (self.down_button.centerx, self.down_button.bottom - arrow_size),
            (self.down_button.centerx - arrow_size, self.down_button.y + arrow_size),
            (self.down_button.centerx + arrow_size, self.down_button.y + arrow_size)
        ]
        pygame.draw.polygon(screen, text_color, points)

        # Draw text with special handling for intensity
        if self.active:
            display_value = self.text_input
        elif 'intensity' in self.name.lower():
            # Show as percentage for intensity - self.value is already a percentage!
            display_value = f"{self.value:.0f}%"
        elif self.decimals > 0:
            display_value = f"{self.value:.{self.decimals}f}"
        else:
            display_value = str(int(self.value))

        text_surface = self.value_font.render(display_value, True, text_color)

        # Scale text if needed
        max_width = self.input_rect.width - int(8 * self.scaling_factor)
        if text_surface.get_width() > max_width:
            scale_factor = max_width / text_surface.get_width()
            new_width = int(text_surface.get_width() * scale_factor)
            new_height = int(text_surface.get_height() * scale_factor)
            text_surface = pygame.transform.scale(text_surface, (new_width, new_height))

        text_x = self.input_rect.x + (self.input_rect.width - text_surface.get_width()) // 2
        text_y = self.input_rect.y + (self.input_rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))


class Panel:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.labels = []
        self.controls = []

    def add_control(self, label, control):
        self.labels.append(label)
        self.controls.append(control)

    def handle_event(self, event):
        for control in self.controls:
            if hasattr(control, 'handle_event'):
                if control.handle_event(event):
                    return True
        return False

    def draw(self, screen):
        for i, control in enumerate(self.controls):
            if hasattr(control, 'draw'):
                control.draw(screen)


def draw_label(screen, text, x, y, width=None, height=20):
    try:
        import os
        font_dir = os.path.expanduser("~/.local/share/pyVid/fonts/")
        label_font = pygame.font.Font(font_dir + 'Arial_Black.ttf', 18)
    except (IOError, FileNotFoundError):
        label_font = pygame.font.Font(None, 20)

    text_surface = label_font.render(text, True, (0, 0, 0))

    if width is None:
        width = text_surface.get_width() + 10

    label_rect = pygame.Rect(x, y, width, height)
    text_y = y + (height - text_surface.get_height()) // 2
    screen.blit(text_surface, (x, text_y))

    return label_rect


class CUDABilateralFilterPanel:
    def __init__(self, display_width=1920, display_height=1080):
        # Calculate scaling factor based on display height
        self.scaling_factor = self.get_scaling_factor(display_height)

        # Base dimensions (designed for 1080p)
        base_width = 350
        base_height = 220
        base_x = display_width - (base_width * self.scaling_factor) - 20
        base_y = 20

        # Apply scaling
        self.x = int(base_x)
        self.y = int(base_y)
        self.width = int(base_width * self.scaling_factor)
        self.height = int(base_height * self.scaling_factor)

        # Load fonts with scaling
        import os
        font_dir = os.path.expanduser("~/.local/share/pyVid/fonts/")
        try:
            regular_size = max(12, int(15 * self.scaling_factor))
            title_size = max(16, int(24 * self.scaling_factor))
            self.font = pygame.font.Font(font_dir + 'Arial_Bold.ttf', regular_size)
            self.title_font = pygame.font.Font(font_dir + 'Arial_Bold.ttf', title_size)
        except (IOError, FileNotFoundError):
            regular_size = max(12, int(20 * self.scaling_factor))
            title_size = max(16, int(24 * self.scaling_factor))
            self.font = pygame.font.Font(None, regular_size)
            self.title_font = pygame.font.Font(None, title_size)

            self.opts_reference = None

        # Define presets
        self.presets = {
            'default': {'d': 5, 'sigma_color': 50.0, 'sigma_space': 50.0, 'intensity': 70},
            'Subtle': {'d': 3, 'sigma_color': 30.0, 'sigma_space': 30.0, 'intensity': 50},
            'Noise Reduction': {'d': 7, 'sigma_color': 75.0, 'sigma_space': 75.0, 'intensity': 80},
            'Skin Smoothing': {'d': 9, 'sigma_color': 80.0, 'sigma_space': 80.0, 'intensity': 60},
            'Strong Smoothing': {'d': 13, 'sigma_color': 150, 'sigma_space': 150, 'intensity': 95},
            'Light': {'d': 5, 'sigma_color': 30, 'sigma_space': 30, 'intensity': 70},
            'Medium': {'d': 9, 'sigma_color': 75, 'sigma_space': 75, 'intensity': 85},
            'Strong': {'d': 15, 'sigma_color': 100, 'sigma_space': 100, 'intensity': 100},
            'Custom': {'d': 9, 'sigma_color': 75, 'sigma_space': 75, 'intensity': 85},
        }

        self.debug = False
        self.debug_time = False

        # Initialize state - start with OFF
        self.current_preset = 'OFF'
        self.filter_enabled = False
        self.current_preset_index = -1

        # Store custom values separately to preserve them - FIXED: Use a deep copy
        self.custom_values = {
            'd': 9,
            'sigma_color': 75.0,
            'sigma_space': 75.0,
            'intensity': 85
        }

        # Initialize with default values but don't enable filter
        default_preset = self.presets['default']

        # Create spinboxes with BASE coordinates (let SpinBox handle scaling internally)
        base_spinbox_x = (self.x / self.scaling_factor) + 160
        base_spinbox_y_start = (self.y / self.scaling_factor) + 45
        base_spinbox_width = 80
        base_spinbox_height = 25

        self.controls = {
            'd': SpinBox(
                base_spinbox_x, base_spinbox_y_start,
                base_spinbox_width, base_spinbox_height, "Diameter:",
                3, 15, initial_value=default_preset['d'], step=2, decimals=0,
                scaling_factor=self.scaling_factor),
            'sigma_color': SpinBox(
                base_spinbox_x, base_spinbox_y_start + 30,
                base_spinbox_width, base_spinbox_height, "Sigma Color:",
                10.0, 200.0, initial_value=default_preset['sigma_color'], step=5.0, decimals=1,
                scaling_factor=self.scaling_factor),
            'sigma_space': SpinBox(
                base_spinbox_x, base_spinbox_y_start + 60,
                base_spinbox_width, base_spinbox_height, "Sigma Space:",
                10.0, 200.0, initial_value=default_preset['sigma_space'], step=5.0, decimals=1,
                scaling_factor=self.scaling_factor),
            'intensity': SpinBox(
                base_spinbox_x, base_spinbox_y_start + 90,
                base_spinbox_width, base_spinbox_height, "Intensity:",
                0, 100, initial_value=default_preset['intensity'], step=5, decimals=0,
                scaling_factor=self.scaling_factor)
        }

        # Create dropdown with BASE coordinates (let DropDown handle scaling internally)
        preset_options = ['OFF'] + list(self.presets.keys())
        base_dropdown_x = (self.x / self.scaling_factor) + 50
        base_dropdown_y = (self.y / self.scaling_factor) + 170

        self.preset_dropdown = DropDown(
            base_dropdown_x, base_dropdown_y,
            200, 30,
            preset_options,
            initial_selection=0,
            scaling_factor=self.scaling_factor
        )

        # Define labels with scaling
        self.labels = {
            'd': "Diameter:",
            'sigma_color': "Sigma Color:",
            'sigma_space': "Sigma Space:",
            'intensity': "Intensity:"
        }

        # Scale label positions - positioned relative to panel
        base_label_x = 50
        self.label_positions = [
            (self.x + int(base_label_x * self.scaling_factor), self.y + int(50 * self.scaling_factor)),
            (self.x + int(base_label_x * self.scaling_factor), self.y + int(80 * self.scaling_factor)),
            (self.x + int(base_label_x * self.scaling_factor), self.y + int(110 * self.scaling_factor)),
            (self.x + int(base_label_x * self.scaling_factor), self.y + int(140 * self.scaling_factor))
        ]

        # Panel rect and title position
        self.panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.title_pos = (self.x + int(75 * self.scaling_factor), self.y + int(5 * self.scaling_factor))

        # Check CUDA availability
        self.cuda_available = cv2.cuda.getCudaEnabledDeviceCount() > 0
        self.last_process_time = 0

    def get_current_preset_name(self):
        """Return the current preset name for display purposes"""
        if not self.filter_enabled:
            return 'OFF'
        return self.current_preset

    def is_filter_active(self):
        """Return whether the bilateral filter is currently active (not 'OFF')"""
        print(f"is_filter_active rturns: {'True' if self.filter_enabled and self.cursrent_preset != 'OFF' else 'False'}")
        return self.filter_enabled and self.current_preset != 'OFF'

    def get_params(self):
        """Return current filter parameters as a dictionary"""
        return {
            'd': self.controls['d'].get_current_value(),
            'sigma_color': self.controls['sigma_color'].get_current_value(),
            'sigma_space': self.controls['sigma_space'].get_current_value(),
            'intensity': self.controls['intensity'].get_current_value()
        }

    def get_scaling_factor(self, display_height):
        """Calculate scaling factor based on display height"""
        if display_height >= 2160:
            return 2.0
        elif display_height >= 1440:
            return 1.5
        elif display_height >= 1200:
            return 1.2
        else:
            return 1.0

    def cycle_preset(self):
        """Cycle through presets with 'x' key"""
        preset_keys = list(self.presets.keys())

        if not self.filter_enabled:
            self.current_preset_index = 0
            self.filter_enabled = True
            preset_name = preset_keys[self.current_preset_index]
            self.current_preset = preset_name
            self.apply_preset(preset_name)
            self.preset_dropdown.set_selected_option(preset_name)
            print(f"Bilateral Filter: {preset_name}")
            return True
        else:
            self.current_preset_index += 1

            if self.current_preset_index >= len(preset_keys):
                self.filter_enabled = False
                self.current_preset_index = -1
                self.current_preset = 'OFF'
                self.preset_dropdown.set_selected_option('OFF')
                print("Bilateral Filter OFF")
                return False
            else:
                preset_name = preset_keys[self.current_preset_index]
                self.current_preset = preset_name
                self.apply_preset(preset_name)
                self.preset_dropdown.set_selected_option(preset_name)
                print(f"Bilateral Filter: {preset_name}")
                return True

    def apply_preset(self, preset_name):
        """Apply a preset and update all controls"""
        if preset_name == 'OFF':
            self.filter_enabled = False
            self.current_preset = 'OFF'

            # Set all spinboxes to zero for OFF state (bypass validation)
            for control in self.controls.values():
                control.value = 0  # Set directly to bypass min/max validation
                if control.active:
                    control.active = False
                    control.text_input = ""

            # Update opts if available
            if self.opts_reference:
                self.opts_reference.apply_bilateral_filter = self.filter_enabled

            print("Applied preset 'OFF': All controls set to 0")
            return

        if preset_name == 'Custom':
            # Use stored custom values
            preset_values = self.custom_values.copy()
            self.filter_enabled = True
        elif preset_name in self.presets:
            preset_values = self.presets[preset_name].copy()
            self.filter_enabled = True
        else:
            print(f"Unknown preset: {preset_name}")
            return

        # Update the spinbox values (use normal set_value for validation)
        for param, value in preset_values.items():
            if param in self.controls:
                self.controls[param].set_value(value)

        # Update current preset
        self.current_preset = preset_name

        # Update opts if available
        if self.opts_reference:
            self.opts_reference.apply_bilateral_filter = self.filter_enabled

        print(f"Applied preset '{preset_name}': {preset_values}")

    def get_current_preset(self):
        return self.current_preset

    def save_custom_values(self):
        """Save current control values as custom values - FIXED"""
        print("DEBUG: Saving current values to custom_values")
        # Save current values directly from controls, don't modify the presets dict
        self.custom_values = {
            'd': int(self.controls['d'].value),  # Use .value directly, not get_current_value()
            'sigma_color': float(self.controls['sigma_color'].value),
            'sigma_space': float(self.controls['sigma_space'].value),
            'intensity': int(self.controls['intensity'].value)
        }
        print(f"DEBUG: Saved custom values: {self.custom_values}")

    def restore_custom_values(self):
        """Restore saved custom values to controls - FIXED"""
        print(f"DEBUG: Restoring custom values: {self.custom_values}")
        for param_name, value in self.custom_values.items():
            if param_name in self.controls:
                print(f"DEBUG: Setting {param_name} to {value}")
                self.controls[param_name].set_value(value)

    def detect_current_preset(self):
        current_values = {
            'd': int(self.controls['d'].value),  # FIXED: Use .value directly
            'sigma_color': float(self.controls['sigma_color'].value),
            'sigma_space': float(self.controls['sigma_space'].value),
            'intensity': int(self.controls['intensity'].value)
        }

        for preset_name, preset_values in self.presets.items():
            if preset_name == 'Custom':  # Skip Custom preset in comparison
                continue
            if self._values_match(current_values, preset_values):
                self.current_preset = preset_name
                return preset_name

        self.current_preset = 'Custom'
        return 'Custom'

    def _values_match(self, current_values, preset_values, tolerance=0.1):
        for key in preset_values:
            if key in current_values:
                if abs(current_values[key] - preset_values[key]) > tolerance:
                    return False
        return True

    def get_preset_names(self):
        return list(self.presets.keys())

    def check_for_custom_values(self):
        """Check if current values match any preset, if not switch to Custom - FIXED"""
        current_values = {
            'd': int(self.controls['d'].value),  # FIXED: Use .value directly
            'sigma_color': float(self.controls['sigma_color'].value),
            'sigma_space': float(self.controls['sigma_space'].value),
            'intensity': int(self.controls['intensity'].value)
        }

        # Check if current values match any existing preset (excluding Custom)
        for preset_name, preset_values in self.presets.items():
            if preset_name == 'Custom':
                continue

            if self._values_match(current_values, preset_values):
                if self.current_preset != preset_name:
                    self.current_preset = preset_name
                    self.preset_dropdown.set_selected_option(preset_name)
                return

        # No match found - switch to Custom and save current values
        if self.current_preset != 'Custom':
            self.current_preset = 'Custom'
            self.preset_dropdown.set_selected_option('Custom')
            self.save_custom_values()

    def handle_event(self, event):
        """Handle events for the bilateral filter panel"""
        event_handled = False

        if self.preset_dropdown.handle_event(event):
            selected_preset = self.preset_dropdown.get_selected_option()

            if selected_preset:
                print(f"Dropdown changed from '{self.current_preset}' to '{selected_preset}'")

                old_filter_state = self.filter_enabled

                # Apply the selected preset
                self.apply_preset(selected_preset)

                # Check if we need to trigger video reinitialization
                new_filter_state = self.filter_enabled

                # If filter state changed, we need to reinit video
                if old_filter_state != new_filter_state:
                    print(f"Filter state changed from {old_filter_state} to {new_filter_state} - triggering video reinit")

                    # Get the current frame position before reinitialization
                    if hasattr(self.opts_reference, '_play_video_instance'):
                        play_video = self.opts_reference._play_video_instance

                        try:
                            current_frame = play_video.vid.frame
                        except:
                            current_frame = 0

                        # Update PlayVideo instance flags
                        play_video.bilateral_filter_enabled = new_filter_state

                        # Get the event handler and trigger reinitialization
                        if hasattr(play_video, '_event_handler'):
                            event_handler = play_video._event_handler
                            # Call reInitVideo with a special flag that bypasses panel logic
                            event_handler.reInitVideo('bilateral_filter_dropdown_change', current_frame)

                event_handled = True

        # Handle spinbox events
        for control in self.controls.values():
            if control.handle_event(event):
                # If any spinbox changed, we're now in "Custom" mode
                if self.current_preset != 'Custom':
                    self.current_preset = 'Custom'
                    self.preset_dropdown.set_selected_option('Custom')

                    # Store the current values as custom values
                    for param, control in self.controls.items():
                        self.custom_values[param] = control.value

                event_handled = True

        return event_handled

    def draw(self, surface):
        """Draw the filter panel with proper scaling"""
        # Create a temporary surface for the gradient
        gradient_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Draw gradient background on the temporary surface
        apply_gradient(
            gradient_surface,
            (0, 0, 100),
            (0, 0, 255),
            self.width,
            self.height,
            alpha_start=50,
            alpha_end=200
        )

        # Blit the gradient surface to the main surface at the panel position
        surface.blit(gradient_surface, (self.x, self.y))

        # Draw panel border
        border_width = max(1, int(1 * self.scaling_factor))
        border_radius = max(4, int(8 * self.scaling_factor))
        pygame.draw.rect(surface, DODGERBLUE, self.panel_rect, border_width, border_radius=border_radius)

        # Draw title
        HEADING_COLOR = (255, 200, 0)
        title_text = "CUDA Bilateral Filter"
        if not self.cuda_available:
            title_text += " (CPU)"
        title_surface = self.title_font.render(title_text, True, HEADING_COLOR)
        surface.blit(title_surface, self.title_pos)

        # Draw labels and controls
        for i, (key, label) in enumerate(self.labels.items()):
            label_surface = self.font.render(label, True, (255, 255, 255))
            surface.blit(label_surface, self.label_positions[i])
            self.controls[key].draw(surface)

        # Draw preset dropdown label and control
        preset_label = "Presets:"
        preset_label_surface = self.font.render(preset_label, True, (255, 255, 255))
        preset_label_x = int(50 * self.scaling_factor)
        preset_label_y = int(175 * self.scaling_factor)
        surface.blit(preset_label_surface, (self.x + preset_label_x, self.y + preset_label_y))

        self.preset_dropdown.draw(surface)

    def apply_bilateral_filter(self, image):
        self.debug_time = True
        #print(f"apply_bilateral_filter: {'True' if image is not None or self.filter_enabled else 'False'}, self.filter_enabled: {'True' if self.filter_enabled else 'False'}")
        if image is None or not self.filter_enabled:
            return image

        start_time = time.time()

        try:
            d = int(self.controls['d'].value)  # FIXED: Use .value directly
            sigma_color = float(self.controls['sigma_color'].value)
            sigma_space = float(self.controls['sigma_space'].value)
            intensity = float(self.controls['intensity'].value) / 100.0  # Convert to 0-1 range

            if self.debug:
                print(f"Applying bilateral filter: d={d}, sigma_color={sigma_color}, sigma_space={sigma_space}, intensity={intensity}")

            if self.cuda_available:
                #print("CUDA enabled, applying CUDA bilateral filter")
                gpu_image = cv2.cuda_GpuMat()
                gpu_image.upload(image)
                gpu_result = cv2.cuda.bilateralFilter(gpu_image, d, sigma_color, sigma_space)
                filtered_image = gpu_result.download()
            else:
                print("CUDA disabled, applying CPU bilateral filter")
                filtered_image = cv2.bilateralFilter(image, d, sigma_color, sigma_space)

            if intensity < 1.0:
                filtered_image = cv2.addWeighted(image, 1.0 - intensity, filtered_image, intensity, 0)

            self.last_process_time = time.time() - start_time
            if self.debug_time:
                print(f"Bilateral filter applied in {self.last_process_time:.4f}s")

            return filtered_image

        except Exception as e:
            print(f"Error applying bilateral filter: {e}")
            return image


class EventHandler:
    def __init__(self):
        self.bilateral_panel = CUDABilateralFilterPanel()
        self.show_filter_panel = False
        self.bilateral_filter_enabled = False

        cuda_devices = cv2.cuda.getCudaEnabledDeviceCount()
        print(f"CUDA devices available: {cuda_devices}")
        if cuda_devices > 0:
            print("🚀 CUDA acceleration enabled for bilateral filter!")
        else:
            print("⚠️  CUDA not available, using CPU fallback")

    def handle_event(self, event):
        if self.show_filter_panel:
            if self.bilateral_panel.handle_event(event):
                params = self.bilateral_panel.get_params()
                print(
                    f"🎛️  Filter params: d={params['d']}, σ_color={params['sigma_color']:.1f}, σ_space={params['sigma_space']:.1f}, intensity={params['intensity']:.2f}")

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                self.show_filter_panel = not self.show_filter_panel
                print(f"Filter panel: {'ON' if self.show_filter_panel else 'OFF'}")

            elif event.key == pygame.K_b:
                self.bilateral_filter_enabled = not self.bilateral_filter_enabled
                status = "ENABLED" if self.bilateral_filter_enabled else "DISABLED"
                print(f"🎯 Bilateral filter: {status}")

    def process_frame(self, frame):
        if self.bilateral_filter_enabled and self.show_filter_panel:
            frame = self.bilateral_panel.apply_bilateral_filter(frame)
        return frame

    def draw(self, surface):
        if self.show_filter_panel:
            self.bilateral_panel.draw(surface)

            instructions = [
                "F - Toggle Filter Panel",
                "B - Enable/Disable Filter",
                "Click spin boxes to adjust"
            ]

            y_offset = surface.get_height() - 80
            for i, instruction in enumerate(instructions):
                text = pygame.font.Font(None, 20).render(instruction, True, (200, 200, 200))
                surface.blit(text, (10, y_offset + i * 20))


def apply_gradient(surface, color_start, color_end, width, height, alpha_start=50, alpha_end=200, x_offset=0, y_offset=0):
    """Apply a vertical gradient with proper positioning"""
    for y in range(height):
        ratio = y / height
        new_color = (
            int(color_start[0] * (1 - ratio) + color_end[0] * ratio),
            int(color_start[1] * (1 - ratio) + color_end[1] * ratio),
            int(color_start[2] * (1 - ratio) + color_end[2] * ratio),
            int(alpha_start * (1 - ratio) + alpha_end * ratio)
        )
        pygame.draw.line(surface, new_color, (x_offset, y_offset + y), (x_offset + width, y_offset + y))