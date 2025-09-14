import os
import time
import inspect
import pygame
import cv2

DODGERBLUE = (30, 144, 255)
DODGERBLUE4 = (16, 78, 139)
HEADING_COLOR = (255, 200, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def bilateral_debug(msg):
    """
    Prints a debug message including the function name and line number where it is called.

    This function is primarily used for logging debug messages with information about the
    current function and line of code. It is useful for tracing the flow of execution and
    identifying the context of logged messages during development and debugging.

    Parameters:
        msg (str): The debug message to log.
    """
    frame = inspect.currentframe().f_back
    line_no = frame.f_lineno
    func_name = frame.f_code.co_name
    print(f"CUDA_BILATERAL_DEBUG [{func_name}:{line_no}] {msg}")

class DropDown:
    """
    Represents a dropdown menu interface element.

    The DropDown class is used to create an interactive dropdown menu that can be rendered using the `pygame` library.
    It supports selecting an option, handling user interactions, and dynamically adjusting its appearance based on a
    given scaling factor. Options are displayed in a scrollable dropdown area, with styling configurable for various
    states such as hover, selection, and disabled appearance.

    Attributes:
        scaling_factor (float): Scaling factor applied to dimensions and font size.
        rect (pygame.Rect): Rectangular area of the dropdown button.
        options (list[str]): List of text options available in the dropdown.
        selected_index (int): Index of the currently selected option.
        is_open (bool): Indicates whether the dropdown menu is currently open.
        option_height (int): Height of each option in the dropdown.
        max_visible_options (int): Maximum number of options visibly displayed at once.
        font (pygame.font.Font): Font used to render text in the dropdown.
        bg_color (tuple[int, int, int]): Background color of the dropdown button.
        selected_color (tuple[int, int, int]): Background color of the selected option.
        hover_color (tuple[int, int, int]): Background color of an option when hovered.
        border_color (tuple[int, int, int]): Color of the dropdown's borders.
        text_color (tuple[int, int, int]): Color of the text in the dropdown.
        disabled_color (tuple[int, int, int]): Background color used to indicate a disabled option.
        dropdown_rect (pygame.Rect): Rectangular area of the dropdown menu when opened.

    Methods:
        get_selected_option:
            Retrieves the currently selected option text from the dropdown.
        set_selected_option:
            Sets the selected option in the dropdown by finding the matching text.
        handle_event:
            Processes user input events (such as mouse clicks) to interact with the dropdown.
        draw:
            Renders the dropdown menu on a `pygame.Surface`.
    """
    def __init__(self, x, y, width, height, options, initial_selection=0, scaling_factor=1.0):
        """
        Represents a dropdown menu UI element with various customization options and styling.

        Attributes:
            scaling_factor (float): Factor used to apply scaling to all dimensions.
            rect (pygame.Rect): Rectangle representing the dropdown's main area.
            options (list): List of options to display in the dropdown menu.
            selected_index (int): Index of the currently selected option.
            is_open (bool): Status indicating whether the dropdown is open or closed.
            option_height (int): Height of each individual option in the dropdown.
            max_visible_options (int): Maximum number of visible options in the dropdown
                when opened.
            font (pygame.font.Font): Font used to render dropdown text.
            bg_color (tuple): Background color of the dropdown menu in RGB format.
            selected_color (tuple): Background color of the selected option in RGB format.
            hover_color (tuple): Background color when an option is hovered in RGB format.
            border_color (tuple): Color of the dropdown's border in RGB format.
            text_color (tuple): Color of the text in RGB format.
            disabled_color (tuple): Color displayed for disabled options in RGB format.
            dropdown_rect (pygame.Rect): Rectangle representing the area for the dropdown
                when it is open.
        """
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
        """
        Retrieves the currently selected option based on the selected index.

        This method checks if the selected index is within a valid range and,
        if so, returns the corresponding option from the list of options. If
        the index is out of range, it will return None.

        Returns:
            str | None: The selected option if the index is valid; otherwise, None.
        """
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index]
        return None

    def set_selected_option(self, option_text):
        """
        Sets the selected option based on the provided option text.

        Attempts to find the index of the provided `option_text` in the available
        `options`. If the provided option text is not found, the `selected_index`
        remains unchanged.

        Parameters:
        option_text: str
            The text of the option to be selected.
        """
        try:
            self.selected_index = self.options.index(option_text)
        except ValueError:
            pass

    def handle_event(self, event):
        """
        Handles user interaction with the dropdown menu. Determines whether the dropdown
        menu should toggle open/closed state, maintain its current state, or update the
        selection based on user action. The function processes mouse events to interact
        with dropdown options or outside the dropdown area.

        Parameters:
        event: pygame.event.Event
            Event object, typically generated by user interactions with the display
            (e.g., mouse clicks).

        Returns:
        bool
            Returns True if the selection index has changed due to the user's interaction,
            otherwise returns False.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if self.rect.collidepoint(mouse_pos):
                self.is_open = not self.is_open
                return False

            if self.is_open and self.dropdown_rect.collidepoint(mouse_pos):
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
        """
        Draws the dropdown menu on a given surface. This method handles rendering
        the main button, the dropdown options when expanded, and the dropdown arrow
        indicating whether the menu is open or closed. The appearance adapts based
        on the scaling factor and the provided color configurations.

        Parameters:
            surface: The pygame.Surface object where the dropdown menu will be
                rendered. The caller is responsible for ensuring that the surface
                is properly initialized before invoking this method.

        Raises:
            None
        """
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
    """
    Represents a SpinBox widget for managing numerical input with defined bounds, step size,
    and precision. Allows scaling of all dimensions and fonts to adapt to different display
    sizes.

    Attributes:
        name: The lowercased and stripped version of the label, or a default "spinbox"
        if no valid label is provided.
        scaling_factor: Factor used to scale all dimensions and fonts of the widget's
        elements.
        rect: The scaled rectangle representing the overall dimensions and position
        of the spinbox.
        label: The text label of the spinbox, initially empty.
        original_label: The original label provided during initialization.
        min_val: The minimum allowable value for the spinbox.
        max_val: The maximum allowable value for the spinbox.
        value: The current value of the spinbox.
        step: The step size used to increment or decrement the spinbox value.
        decimals: The number of decimal places to display for the spinbox value.
        active: Indicates if the spinbox is currently active or in an editing state.
        text_input: The temporary text input if the spinbox is used for direct text input.
        button_width: The width of the buttons for incrementing or decrementing, scaled.
        input_width: The width of the text input area, scaled.
        input_rect: The scaled rectangle representing the text input box dimensions
        and position.
        up_button: The scaled rectangle representing the increment button dimensions
        and position.
        down_button: The scaled rectangle representing the decrement button dimensions
        and position.
        value_font: The scaled font object used for rendering the spinbox value.
    """
    def __init__(self, x, y, width, height, label, min_val, max_val, initial_value=None, step=1, decimals=0, scaling_factor=1.0):
        """
        Represents a SpinBox widget for managing numerical input with defined bounds, step size, and precision.
        Allows scaling of all dimensions and fonts to adapt to different display sizes.

        Attributes:
            name (str): The lowercased and stripped version of the label, or a default "spinbox" if no valid label is provided.
            scaling_factor (float): Factor used to scale all dimensions and fonts of the widget's elements.
            rect (pygame.Rect): The scaled rectangle representing the overall dimensions and position of the spinbox.
            label (str): The text label of the spinbox, initially empty.
            original_label (str): The original label provided during initialization.
            min_val (int/float): The minimum allowable value for the spinbox.
            max_val (int/float): The maximum allowable value for the spinbox.
            value (int/float): The current value of the spinbox.
            step (int/float): The step size used to increment or decrement the spinbox value.
            decimals (int): The number of decimal places to display for the spinbox value.
            active (bool): Indicates if the spinbox is currently active or in an editing state.
            text_input (str): The temporary text input if the spinbox is used for direct text input.
            button_width (int): The width of the buttons for incrementing or decrementing, scaled.
            input_width (int): The width of the text input area, scaled.
            input_rect (pygame.Rect): The scaled rectangle representing the text input box dimensions and position.
            up_button (pygame.Rect): The scaled rectangle representing the increment button dimensions and position.
            down_button (pygame.Rect): The scaled rectangle representing the decrement button dimensions and position.
            value_font (pygame.font.Font): The scaled font object used for rendering the spinbox value.
        """
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
            font_dir = os.path.expanduser("~/.local/share/pyVid/fonts/")
            font_size = max(12, int(17 * scaling_factor))
            self.value_font = pygame.font.Font(font_dir + 'Arial_Bold.ttf', font_size)
        except (IOError, FileNotFoundError):
            font_size = max(12, int(22 * scaling_factor))
            self.value_font = pygame.font.Font(None, font_size)

    def get_current_value(self):
        """
        Gets the current value of the attribute with special handling for intensity values.

        If the attribute name contains the word "intensity", the value is interpreted as a
        percentage and converted to a 0-1 range. Otherwise, it returns the attribute's raw value.

        Returns:
            float: Processed or raw value of the attribute depending on its name.
        """
        # Special handling for intensity - convert percentage to 0-1 range
        if 'intensity' in self.name.lower():
            return round(self.value / 100.0, 1)  # Convert percentage to intensity
        return self.value

    def set_value(self, new_value):
        """
        Sets the value of an instance attribute, ensuring it remains within
        the defined range, and resets specific attributes when the instance
        is active.

        Parameters:
            new_value: The new value to be set for the instance.

        Raises:
            None
        """
        self.value = max(self.min_val, min(self.max_val, new_value))
        if self.active:
            self.active = False
            self.text_input = ""

    def handle_event(self, event):
        """
        Handles input events for interactive elements, such as buttons and text input.

        This method processes mouse and keyboard inputs to update the state of the interactive
        fields like increment/decrement buttons or editable text input fields. Events such as
        mouse button click, pressing return, tab, backspace, escape, or valid character entry
        are handled here to modify the internal values appropriately.

        Parameters:
            event (pygame.event.Event): The event to handle, e.g., mouse button
            clicks, key presses, etc.

        Returns:
            bool: True if the value has changed due to interaction, otherwise False.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if self.up_button.collidepoint(mouse_pos):
                old_value = self.value
                self.value = min(self.max_val, self.value + self.step)
                return self.value != old_value

            if self.down_button.collidepoint(mouse_pos):
                old_value = self.value
                self.value = max(self.min_val, self.value - self.step)
                return self.value != old_value

            if self.input_rect.collidepoint(mouse_pos):
                self.active = True
                self.text_input = str(self.value)

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                old_value = self.value
                self._apply_text_input()
                self.active = False
                return self.value != old_value
            if event.key == pygame.K_TAB:
                old_value = self.value
                self._apply_text_input()
                self.active = False
                return self.value != old_value
            if event.key == pygame.K_ESCAPE:
                self.active = False
                self.text_input = ""
            elif event.key == pygame.K_BACKSPACE:
                self.text_input = self.text_input[:-1]
            else:
                if event.unicode and (event.unicode.isdigit() or event.unicode == '.' or event.unicode == '-'):
                    self.text_input += event.unicode

        return False

    def _apply_text_input(self):
        """
        Handles the application and validation of user-inputted text for a specific parameter. The method
        parses the input, validates it based on specific rules, and updates the parameter's value if valid.
        Parameters like "diameter" and "intensity" have additional validation-specific logic applied.

        Raises:
            ValueError: Raised if the input cannot be converted to a float or integer,
            though it is silently handled within the method logic.

        """
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
        """
        Clamps an input value to a valid percentage range (0-100).

        This helper function ensures that the provided value is constrained
        within the bounds of valid percentage values. Any value below 0
        is clamped to 0, and any value above 100 is clamped to 100.
        The adjusted percentage is then returned.

        Parameters:
        value : int or float
            The input value to be clamped to the percentage range.

        Returns:
        int
            The clamped value within the range of 0 to 100 inclusive.
        """
        # Clamp to percentage range and return as percentage
        percentage = max(0, min(100, value))
        return percentage  # ← Keep as percentage!

    def _validate_diameter(self, value):
        """
        Validates and adjusts the provided diameter value.

        If the given diameter is less than 3, it will be adjusted to 3. If the diameter
        is an even number, it will be incremented by 1 to make it odd. Odd values greater
        than or equal to 3 will remain unchanged.

        Parameters:
            value: int
                The diameter value to validate and adjust.

        Returns:
            int
                A valid, adjusted diameter value that is odd and greater than or equal to 3.
        """
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
    """
    Represents a graphical panel containing controls and labels.

    The Panel class manages a rectangular area on the screen, handles input events
    for added controls, and draws them onto a surface (screen). It is designed
    to serve as a container to group multiple controls and their labels while
    providing a mechanism for event handling and rendering visuals.
    """
    def __init__(self, x, y, width, height):
        """
        Represents a GUI element with a rectangular boundary, labels, and controls.

        Attributes:
        rect (pygame.Rect): Defines the rectangular boundary of the element.
        labels (list): A list to store labels belonging to the element.
        controls (list): A list to store controls associated with the element.

        """
        self.rect = pygame.Rect(x, y, width, height)
        self.labels = []
        self.controls = []

    def add_control(self, label, control):
        """
        Adds a control with an associated label to the corresponding lists.

        The method appends the provided label and control to their respective
        lists, maintaining the association between them.

        Args:
            label: The label to be added.
            control: The control to be added.
        """
        self.labels.append(label)
        self.controls.append(control)

    def handle_event(self, event):
        """
        Handles an event by delegating it to the control elements.

        This method iterates over all controls associated with the instance
        and checks if they have a 'handle_event' method. If a control has
        this method and it successfully handles the event, the process
        stops, and the method returns True. If none of the controls handle
        the event, the method returns False.

        Args:
            event: The event object to be handled.

        Returns:
            bool: True if the event was handled successfully by one of the
            controls, False otherwise.

        Raises:
            None
        """
        for control in self.controls:
            if hasattr(control, 'handle_event'):
                if control.handle_event(event):
                    return True
        return False

    def draw(self, screen):
        """
        Draws all controls in the instance on the given screen.

        This method iterates through the list of controls and calls the `draw` method
        for each control that has it. It assumes that each control that needs to be
        rendered has a method named `draw` implemented. The drawing will be performed
        on the provided screen object.

        Args:
            screen: The surface or screen object where controls will be drawn.

        """
        for i, control in enumerate(self.controls):
            if hasattr(control, 'draw'):
                control.draw(screen)

def draw_label(screen, text, x, y, width=None, height=20):
    """
    Render a text label on the screen with optional width and specified height.

    This function draws a label with the specified text, position, and dimension
    on a given screen surface. If a custom font is unavailable, it falls back to
    a default pygame font. The label's width can be adjusted based on the text's
    width or set explicitly. The label's background color is transparent, and the
    text is rendered in black.

    Arguments:
        screen: pygame.Surface
            The surface on which to draw the label.
        text: str
            The text to be displayed on the label.
        x: int
            The x-coordinate of the label's position.
        y: int
            The y-coordinate of the label's position.
        width: Optional[int]
            The width of the label. If not provided, it adjusts automatically
            based on the text width.
        height: int
            The height of the label. Default is 20.

    Returns:
        pygame.Rect
            A rectangle object representing the dimensions and position of
            the drawn label.
    """
    try:
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
    """
    A class representation of a CUDA-enabled Bilateral Filter control panel.

    This class manages the graphical user interface (GUI) for manipulating CUDA-based bilateral
    filter parameters. It includes elements such as dropdowns, spinboxes, and preset options to
    provide a convenient way for users to adjust the filtering behavior dynamically. The panel
    also supports scaling based on the display resolution for better visual adaptability.

    Attributes:
        scaling_factor: Scale of the panel based on display height.
        x: The x-coordinate of the panel.
        y: The y-coordinate of the panel.
        width: The width of the panel after applying scaling.
        height: The height of the panel after applying scaling.
        font: Font object used for rendering text (regular font size).
        title_font: Font object used for rendering the panel title (larger font size).
        presets: Dictionary of preset configurations for bilateral filter parameters.
        debug: Enable or disable debug mode for additional logs.
        debug_time: Additional debug mode to time operations.
        current_preset: Name of the currently active preset (default is 'OFF').
        filter_enabled: Flag to determine if the bilateral filter is currently active.
        current_preset_index: Index of the currently selected preset in the dropdown.
        custom_values: Dictionary holding custom-defined filter parameters.
        controls: Dictionary of SpinBox controls for user-adjustable parameters.
        preset_dropdown: DropDown control for selecting among preset configurations.
        labels: Dictionary mapping parameter keys to their display labels.
        label_positions: Array of label positions within the panel.
        panel_rect: The rectangle dimensions of the panel for rendering purposes.
        title_pos: The position of the panel's title text.
        cuda_available: Boolean flag for CUDA availability on the device.
        last_process_time: The timestamp of the last execution for performance tracking.

    Methods:
        get_current_preset_name:
            Return the current preset name for display purposes.
        is_filter_active:
            Return whether the bilateral filter is currently active (not 'OFF').
        get_params:
            Return the current filter parameters as a dictionary.
        get_scaling_factor:
            Calculate the scaling factor based on display height.
        cycle_preset:
            Cycle through presets with the 'x' key.
    """
    def __init__(self, display_width=1920, display_height=1080):
        """
        Initializes the object with specified display dimensions, scaling factors, UI elements, and presets
        for a filter management application.

        The constructor computes spatial dimensions and scaling factors based on the provided display
        resolution, initializes fonts and UI components such as spinboxes and dropdown menus, defines
        presets for filters, and handles initialization of default states and custom filter values.

        Parameters:
        display_width: int
            The width of the display in pixels (default is 1920).
        display_height: int
            The height of the display in pixels (default is 1080).

        Raises:
        IOError
            If the specified font files cannot be found or loaded correctly.
        FileNotFoundError
            If the font directory or required font files are missing.

        Attributes:
        scaling_factor: float
            The scaling factor calculated based on display height for UI elements.
        x: int
            The x-coordinate of the UI panel on the display.
        y: int
            The y-coordinate of the UI panel on the display.
        width: int
            The width of the UI panel.
        height: int
            The height of the UI panel.
        font: pygame.font.Font
            The font used for regular UI text.
        title_font: pygame.font.Font
            The font used for UI titles.
        presets: dict
            A dictionary of predefined filter presets, each containing parameters like diameter,
            sigma color, sigma space, and intensity.
        debug: bool
            A flag to enable or disable debug mode for displaying additional runtime information.
        debug_time: bool
            A flag to enable or disable timing debug information.
        current_preset: str
            The name of the currently active filter preset.
        filter_enabled: bool
            A flag indicating whether the filter is currently enabled or disabled.
        current_preset_index: int
            The index of the currently selected filter preset in the dropdown menu.
        custom_values: dict
            Custom filter parameter values for 'Custom' preset, stored separately to allow modifications.
        controls: dict
            A dictionary of spinbox controls for adjusting filter parameters like diameter, sigma values,
            and intensity.
        preset_dropdown: DropDown
            A dropdown menu object for selecting filter presets.
        labels: dict
            A dictionary of labels for filter parameter controls.
        label_positions: list of tuples
            A list of (x, y) positional tuples for placing parameter labels on the UI panel.
        panel_rect: pygame.Rect
            A rectangle object representing the geometry of the UI panel.
        title_pos: tuple
            The (x, y) position of the title text on the UI panel.
        cuda_available: bool
            Indicates whether CUDA-enabled devices for GPU acceleration are available.
        last_process_time: float
            Stores the timestamp of the last filter processing operation in seconds.
        """
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

        # Last preset that was not 'OFF'
        self.last_preset = 'default'

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

        # Visibility flag
        self.IS_visible = False
        # Hide button hover flag
        self.is_hovered = False


        # The hide button rectangle
        self.hide_button_rect = None

    def is_visible(self):
        return self.IS_visible

    def toggle_visibility(self):
        self.IS_visible = not self.IS_visible
        if self.opts_reference:
            self.opts_reference.show_bilateral_filter = self.IS_visible

    def set_visibility(self, visible):
        self.IS_visible = visible
        if self.opts_reference:
            self.opts_reference.show_bilateral_filter = self.IS_visible

    def get_current_preset_name(self):
        """
        Gets the current preset name.

        This method returns the name of the currently active preset
        if the filter is enabled. If the filter is not enabled, it
        returns 'OFF'.

        Returns:
            str: The name of the current preset or 'OFF' if the filter
            is disabled.
        """
        if not self.filter_enabled:
            return 'OFF'
        return self.current_preset

    def is_filter_active(self):
        """
        Determines if a filter is currently active based on specific conditions.

        A filter is considered active if the 'filter_enabled' property
        is set to True and the 'current_preset' is not equal to 'OFF'.

        Returns:
            bool: True if the filter is active; otherwise, False.
        """
        print(f"is_filter_active returns: {'True' if self.filter_enabled and self.current_preset != 'OFF' else 'False'}")
        return self.filter_enabled and self.current_preset != 'OFF'

    def get_params(self):
        """
        Retrieves the current parameters for the controls.

        Returns the parameters from the controls as a dictionary. Each parameter
        is fetched using its respective key and current value.

        Returns:
            dict: A dictionary containing the current parameter values with
            keys 'd', 'sigma_color', 'sigma_space', and 'intensity'.
        """
        return {
            'd': self.controls['d'].get_current_value(),
            'sigma_color': self.controls['sigma_color'].get_current_value(),
            'sigma_space': self.controls['sigma_space'].get_current_value(),
            'intensity': self.controls['intensity'].get_current_value()
        }

    def get_scaling_factor(self, display_height):
        """
        Determines the UI scaling factor based on the given display height.

        This method evaluates the height of a display in pixels and provides a corresponding
        scaling factor. The scaling factor is determined by pre-defined ranges of display
        heights, enabling optimized scaling for enhancing the user experience on various
        display resolutions.

        Args:
            display_height (int): The height of the display in pixels.

        Returns:
            float: The UI scaling factor based on the display height.
        """
        if display_height >= 2160:
            return 2.0
        if display_height >= 1440:
            return 1.5
        if display_height >= 1200:
            return 1.2

        return 1.0

    def cycle_preset(self):
        """
        Cycles through the filter presets, enabling or disabling the filter based
        on the current preset and user interaction.

        This method progresses the internal preset state, applying the corresponding
        preset configurations or turning off the filter when needed. If the filter is
        disabled, it resets to the 'OFF' state; otherwise, it cycles through the
        presets and applies the selected one.

        Returns:
            bool: True if a preset is applied or the filter is enabled; False if the
                  filter is turned off.
        """
        preset_keys = list(self.presets.keys())

        if not self.filter_enabled:
            self.current_preset_index = 0
            self.filter_enabled = True
            preset_name = preset_keys[self.current_preset_index]
            self.current_preset = preset_name
            self.apply_preset(preset_name)
            self.preset_dropdown.set_selected_option(preset_name)
            #print(f"Bilateral Filter: {preset_name}")
            return True
        self.current_preset_index += 1
        if self.current_preset_index >= len(preset_keys):
            self.filter_enabled = False
            self.current_preset_index = -1
            self.current_preset = 'OFF'
            self.preset_dropdown.set_selected_option('OFF')
            print("Bilateral Filter OFF")
            return False
        preset_name = preset_keys[self.current_preset_index]
        self.current_preset = preset_name
        self.apply_preset(preset_name)
        self.preset_dropdown.set_selected_option(preset_name)
        # print(f"Bilateral Filter: {preset_name}")
        return True

    def apply_preset(self, preset_name):
        """
        Applies a preset to configure controls and filter settings based on input `preset_name`. This method updates the
        internal state, control values, and potentially modifies associated options reference when available.

        Parameters:
            preset_name (str): Name of the preset to apply. Can be 'OFF', 'Custom', or a key in the presets dictionary.
        """
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

            print("CUDA_BILATERAL_DEBUG: Applied preset 'OFF': All controls set to 0")
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

        print(f"CUDA_BILATERAL_DEBUG: Applied preset '{preset_name}': {preset_values}")
        self.last_preset = preset_name
        if self.opts_reference:
            self.opts_reference.last_bilateral_preset = self.last_preset

    def get_current_preset(self):
        """
        Returns the current preset configuration in use.

        This method retrieves and returns the current preset value that is currently
        set within the instance.

        Returns:
            str: The current preset configuration.
        """
        return self.current_preset

    def save_custom_values(self):
        """
        Saves the current values from controls into the custom_values dictionary.

        This method stores the current state of the control parameters to the
        custom_values attribute without modifying or interacting with the presets
        dictionary. The values are retrieved directly from the respective control
        objects using their `value` attribute.

        Raises
        ------
        KeyError
            If required keys are not present in the `controls` dictionary.
        """
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
        """
        Restores custom values saved in the instance back to the corresponding controls.

        This method iterates over stored custom values and matches them with the controls
        using parameter names. If a match is found, the control's value is updated with
        the saved custom value. This provides functionality for reapplying custom settings to
        UI controls or other components.

        Parameters:
            None

        Raises:
            None

        Returns:
            None
        """
        print(f"DEBUG: Restoring custom values: {self.custom_values}")
        for param_name, value in self.custom_values.items():
            if param_name in self.controls:
                print(f"DEBUG: Setting {param_name} to {value}")
                self.controls[param_name].set_value(value)

    def detect_current_preset(self):
        """
        Determines the current preset by comparing the current control values with
        the predefined preset values. If the current values match a preset, it sets
        the current preset to the matching preset's name. If no match is found, it
        sets the current preset to 'Custom'.

        Returns:
            str: The name of the matching preset if found, otherwise 'Custom'.
        """
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
        """
        Compares current values against preset values within a given tolerance.

        This method checks if all keys in the preset values exist in the current
        values, and assesses whether their associated numerical differences exceed
        the specified tolerance.

        Parameters:
            current_values (dict): A dictionary containing the current values for
                comparison.
            preset_values (dict): A dictionary containing the preset values for
                comparison.
            tolerance (float): The numerical tolerance for comparison. Defaults to 0.1.

        Returns:
            bool: True if all current values match the preset values within the
            tolerance, otherwise False.
        """
        for key in preset_values:
            if key in current_values:
                if abs(current_values[key] - preset_values[key]) > tolerance:
                    return False
        return True

    def get_preset_names(self):
        """
        Retrieves the names of all available presets.

        Returns
        -------
        list of str
            A list containing the names of all the presets.
        """
        return list(self.presets.keys())

    def check_for_custom_values(self):
        """
        Checks whether the current control values match any existing preset, and updates
        the current preset accordingly. If no matching preset is found, the preset is
        updated to "Custom" and the current values are saved as a custom preset.

        Raises:
            None

        """
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
        """
        Handles an event and triggers corresponding actions such as update of dropdown selection,
        application of presets, detection of filter state change, and handling of custom spinbox
        event changes. If required, it performs video reinitialization with updated filter settings.

        Parameters:
        event: The event object that is being processed.

        Returns:
        bool: True if the event was successfully handled; otherwise, False.

        Raises:
        None.
        """
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

    def handle_mouse_button_down(self, pos):
        if not self.IS_visible:
            return False

        # Check if the hide button was clicked
        if self.hide_button_rect and self.hide_button_rect.collidepoint(pos):
            self.set_visibility(False)
            return True

        return False

    def draw(self, surface):
        """
        Draws the content of the panel on the given surface, including the background
        gradient, panel border, title, labels, controls, and preset dropdown.

        Parameters:
            surface (Surface): The Pygame surface where the panel will be drawn.
        """
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

        is_hovered = False
        # Draw the hide button
        hide_button_rect = pygame.Rect(self.x + self.width // 2 + 180, self.y + self.height - 91, 120, 45)
        pygame.draw.rect(surface, DODGERBLUE4, hide_button_rect, border_radius=10)
        pygame.draw.rect(surface, DODGERBLUE, hide_button_rect, 1, border_radius=10)
        hide_text = self.font.render("Hide", True, HEADING_COLOR if is_hovered else WHITE)
        surface.blit(hide_text, (hide_button_rect.x + 30, hide_button_rect.y + 6))

        self.hide_button_rect = hide_button_rect

    def apply_bilateral_filter(self, image):
        """
        Apply a bilateral filter to the given image.

        This method applies a bilateral filter to the provided image using either
        the CPU or CUDA, depending on the system's configuration. The bilateral
        filter preserves edges while smoothing the image. The intensity of the
        filter can also be adjusted. If the CUDA feature is available and enabled,
        the filtering operation is offloaded to the GPU for better performance.

        Parameters:
            image (numpy.ndarray): The input image on which the bilateral filter
            needs to be applied.

        Returns:
            numpy.ndarray: The result of applying the bilateral filter. If the
            input image is None or the filter is not enabled, the original input
            image is returned.

        Raises:
            Exception: Catches any unexpected errors during the filtering process
            and prints the error message but always ensures that the original
            image is returned in case of an error.
        """
        self.debug_time = False
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
    """
    Handles events, processes frames, and draws related components for a bilateral filter panel.

    This class facilitates the operation of a CUDA-accelerated bilateral filter, including
    managing user interaction through events, toggling filter options, and displaying a UI
    panel for filter parameter adjustment. It monitors keyboard events to show/hide the
    filter panel and enable/disable the bilateral filter functionality. Additionally, it
    processes video frames with the bilateral filter when enabled.

    Attributes:
        bilateral_panel: Instance of CUDABilateralFilterPanel used for handling the filter's UI
            and managing parameter adjustments.
        show_filter_panel: Boolean indicating whether the filter panel is currently displayed.
        bilateral_filter_enabled: Boolean indicating whether the bilateral filter functionality
            is enabled.

    Methods:
        __init__:
            Initializes the EventHandler, including pre-checking CUDA device availability
            and setting up the necessary properties.

        handle_event:
            Handles user events, toggling the filter panel display and filter functionality
            based on keyboard interaction. It processes internal updates when interaction
            occurs with the filter panel.

        process_frame:
            Processes a video frame, applying the CUDA-accelerated bilateral filter if
            the filter is enabled and the panel is active.

        draw:
            Renders the filter panel and related instructions onto the provided surface,
            based on the current state of the filter panel display.
    """
    def __init__(self):
        """
        Initializes the class and sets up bilateral filtering capabilities with CUDA
        support if available. It also initializes necessary attributes to control the
        filtering operation and displays information about CUDA availability.

        Attributes:
            bilateral_panel (CUDABilateralFilterPanel): Instance of the
                bilateral filter panel for processing images.
            show_filter_panel (bool): Indicates whether the filter panel should be
                displayed.
            bilateral_filter_enabled (bool): Flag to determine if the bilateral filter
                is enabled.
        """
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
        """
        Handles user input events and updates properties or panels accordingly.

        Attributes:
            show_filter_panel (bool): Indicates whether the filter panel is visible or not.
            bilateral_panel: An object responsible for managing the bilateral filter panel
                             and its parameters.
            bilateral_filter_enabled (bool): Indicates whether the bilateral filter is
                                              enabled or disabled.

        Args:
            event: The input event to handle.

        Raises:
            None

        Returns:
            None
        """
        if self.show_filter_panel:
            if self.bilateral_panel.handle_event(event):
                params = self.bilateral_panel.get_params()
                print(
                    f"🎛️  Filter params: d={params['d']}, σ_color={params['sigma_color']:.1f}, σ_space={params['sigma_space']:.1f}, intensity={params['intensity']:.2f}")

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                self.show_filter_panel = not self.show_filter_panel
                print(f"Filter panel: {'ON' if self.show_filter_panel else 'OFF'}")

            elif event.key == pygame.K_a:
                self.bilateral_filter_enabled = not self.bilateral_filter_enabled
                status = "ENABLED" if self.bilateral_filter_enabled else "DISABLED"
                print(f"🎯 Bilateral filter: {status}")

    def process_frame(self, frame):
        """
        Processes the given video frame by optionally applying a bilateral filter.

        If the bilateral filter is enabled, and the filter panel is enabled to
        show, the frame will have the bilateral filter applied before being
        returned.

        Parameters:
        frame: Any
            The video frame to be processed.

        Returns:
        Any
            The processed video frame, either filtered or unfiltered depending
            on the current settings.
        """
        if self.bilateral_filter_enabled and self.show_filter_panel:
            frame = self.bilateral_panel.apply_bilateral_filter(frame)
        return frame

    def draw(self, surface):
        """
        Render the filter panel and instructional text onto the given surface.

        This method is responsible for drawing the filter panel to the provided surface
        if the filter panel visibility is enabled. It further displays a set of instructional
        text below the filter panel to guide the user.

        Args:
            surface (pygame.Surface): The surface to draw the filter panel and
                                       instructions onto.
        """
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
    """
    Applies a vertical gradient effect to a specified area on a pygame surface.

    This function generates a gradient with colors transitioning vertically from
    `color_start` to `color_end` over the specified `height`. The alpha property
    also transitions smoothly from `alpha_start` to `alpha_end`. The gradient
    is applied to the area starting from `(x_offset, y_offset)` with the defined
    `width` and `height`.

    Args:
        surface (pygame.Surface): The surface on which to apply the gradient.
        color_start (tuple): The starting color of the gradient as an RGB tuple.
        color_end (tuple): The ending color of the gradient as an RGB tuple.
        width (int): The width of the gradient area.
        height (int): The height of the gradient area.
        alpha_start (int): The starting alpha value (0 to 255). Default is 50.
        alpha_end (int): The ending alpha value (0 to 255). Default is 200.
        x_offset (int): The x-coordinate offset for the gradient. Default is 0.
        y_offset (int): The y-coordinate offset for the gradient. Default is 0.
    """
    for y in range(height):
        ratio = y / height
        new_color = (
            int(color_start[0] * (1 - ratio) + color_end[0] * ratio),
            int(color_start[1] * (1 - ratio) + color_end[1] * ratio),
            int(color_start[2] * (1 - ratio) + color_end[2] * ratio),
            int(alpha_start * (1 - ratio) + alpha_end * ratio)
        )
        pygame.draw.line(surface, new_color, (x_offset, y_offset + y), (x_offset + width, y_offset + y))
