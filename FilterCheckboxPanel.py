
# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DODGERBLUE = (30, 144, 255)
DODGERBLUE4 = (16, 78, 139)
HEADING_COLOR = (255, 200, 0)  # Yellow for headings
FALSE_COLOR = HEADING_COLOR
TRUE_COLOR = (50, 200, 0)
CHECKBOX_CHECKED_COLOR = (80, 255, 0)
LABEL_TEXT_COLOR = (0, 175, 255)

import os
import pygame
import upScale as up_scale

class Checkbox:
    """
    Represents a checkbox UI component.

    A checkbox is a graphical element that can be toggled between a checked and unchecked
    state. This class allows the display, interaction, and optional labeling of the checkbox.
    It is designed to work with the pygame library and provides methods for drawing the
    checkbox on the screen, setting a label, and handling user events.

    Attributes:
        scaling_factor (float): The scaling factor used to resize the checkbox.
        rect (pygame.Rect): The bounding rectangle of the checkbox for placement and collision.
        checked (bool): Indicates whether the checkbox is currently checked or not.
        label (str): The text label displayed next to the checkbox, if any.
        label_surface (pygame.Surface or None): The rendered surface of the label text.
        font (pygame.font.Font): The font used for rendering the label.

    Methods:
        set_label(text: str):
            Sets the label text for the checkbox.

        draw(screen: pygame.Surface):
            Draws the checkbox, its current state (checked/unchecked), and optional label on
            the provided screen surface.

        handle_event(event: pygame.event.Event) -> bool:
            Handles input events for the checkbox, toggling its state if clicked.
    """
    def __init__(self, x, y, size, scaling_factor=1.0):
        """
        Initialize an instance of the class with position, size, and scaling factor,
        and prepare graphical elements for rendering.

        Attributes:
            scaling_factor: float
                The factor by which the size is scaled.
            rect: pygame.Rect
                The rectangular area representing the object's dimensions and position.
            checked: bool
                Indicates if the object has been marked checked.
            label: str
                The textual label associated with the object.
            label_surface: pygame.Surface or None
                The rendered surface of the label text, initialized as None.
            font: pygame.font.Font
                The font used for rendering the label.

        Parameters:
            x: int
                The x-coordinate of the top-left corner of the rectangle.
            y: int
                The y-coordinate of the top-left corner of the rectangle.
            size: int
                The base size of the rectangle.
            scaling_factor: float, optional
                A scaling multiplier for the size, default is 1.0.
        """
        self.scaling_factor = scaling_factor
        scaled_size = int(size * scaling_factor)
        self.rect = pygame.Rect(x, y, scaled_size, scaled_size)
        self.checked = False
        self.label = ""
        self.label_surface = None
        self.label_rect = None
        self.font = pygame.font.Font(None, int(24 * 1.8))
        USER_HOME = os.path.expanduser("~")
        RESOURCES_DIR = USER_HOME + "/.local/share/pyVid/Resources/"
        checked_icon = pygame.image.load(RESOURCES_DIR + "checkmark_white.png").convert_alpha()
        self.checked_icon = pygame.transform.scale(checked_icon, (24, 24))

    def set_label(self, text):
        """
        Sets the label's text and renders it with the specified font and color.

        This method updates the text for the label and generates a rendered
        surface for displaying the label using the current font and color.

        Args:
            text (str): The new text to set for the label.
        """
        self.label = text
        self.label_surface = self.font.render(text, True, LABEL_TEXT_COLOR)  # Bright Cyan

    def draw(self, screen):
        """
        Draw a checkbox onto the screen, including its label and optional GPU icon.

        This method is responsible for rendering a checkbox component on the given pygame
        screen surface. It draws the checkbox itself, a label if provided, and an optional
        GPU icon if the attribute `gpu_icon` is present in the object.

        Parameters:
        screen (pygame.Surface): The screen surface where the checkbox and its associated
        label and icon will be drawn.

        Raises:
        None
        """
        # Draw checkbox
        pygame.draw.rect(screen, WHITE, self.rect, 1, border_radius=2)
        if self.checked:
            inner_rect = pygame.Rect(
                self.rect.x + self.rect.width * 0.2,
                self.rect.y + self.rect.height * 0.2,
                self.rect.width * 0.6,
                self.rect.height * 0.6
            )
            # Draw checkmark icon
            pygame.draw.rect(screen, DODGERBLUE, inner_rect, border_radius=4)
            check_icon_x = inner_rect.centerx - 5
            check_icon_y = inner_rect.centery - 20
            screen.blit(self.checked_icon, (check_icon_x, check_icon_y))

        # Draw label
        if self.label_surface:
            label_pos = (self.rect.right + 10,
                         self.rect.centery - self.label_surface.get_height() // 2)
            screen.blit(self.label_surface, label_pos)
            label_rect = self.label_surface.get_rect(topleft=label_pos)
            self.label_rect = label_rect

            # Draw GPU icon if present
            if hasattr(self, 'gpu_icon'):
                icon_x = label_rect.right + 5  # 5 pixels after the label
                icon_y = label_rect.centery - self.gpu_icon.get_height() // 2
                screen.blit(self.gpu_icon, (icon_x, icon_y))

    def handle_event(self, event):
        """
        Handles the events triggered by user interaction with a graphical element. This function
        is specifically designed to handle mouse button interactions and toggles a check state
        based on whether the interaction occurs within a defined region (rect).

        Args:
            event (pygame.event.Event): The event object containing details about the user's interaction.

        Returns:
            bool: True if the event leads to a change in the checked state, otherwise False.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                print(f"Check status: {'Checked' if self.checked else 'unChecked'}")
                return True
        return False

class FilterCheckboxPanel:
    """
    Represents a panel containing filter selection checkboxes.

    This class is designed to manage a user interface panel that contains checkboxes
    allowing users to select and toggle various image and video processing filters.
    The panel supports CUDA-enabled filters and handles the layout, state management,
    and synchronization of checkbox states with the underlying filter settings.

    Attributes
    ----------
    play_video : object
        The object representing the video player or renderer to which the filter panel
        belongs. This is used to access display properties and resource directories.
    display_width : int
        The width of the display, derived from the associated video player's window.
    display_height : int
        The height of the display, derived from the associated video player's window.
    BOX_WIDTH_BASE : int
        The base width of the filter checkbox panel.
    BOX_HEIGHT_BASE : int
        The base height of the filter checkbox panel, derived with height scaling applied.
    cuda_filters : set
        A set of strings representing the names of CUDA-enabled filters available for
        selection.
    checkboxes : list
        A list containing checkbox objects, each corresponding to a filter.
    """
    def __init__(self, play_video):
        """
        A class initializer method that sets up video display properties, scaling, and filter options.
        This method initializes video-related parameters, defines CUDA-enabled filter types, configures
        scaling, and creates interactive checkboxes for filter management.

        Parameters:
            play_video: The video playback object used to retrieve display properties.

        Attributes:
            play_video: Stores the video playback object.
            display_width: Width of the video display obtained from the playback object.
            display_height: Height of the video display obtained from the playback object.
            filterCheckboxPanel_is_visible: Boolean flag indicating whether the filter panel is visible.
            BOX_WIDTH_BASE: Integer constant representing the base width size for the filter panel.
            BOX_HEIGHT_BASE: Integer constant representing the height size of the filter panel
                             calculated based on the video display's dimensions with scaling.
            cuda_filters: A set containing the available CUDA-enabled video filter types.
            checkboxes: A list that represents the individual checkboxes created for filter selection.

        Raises:
            This method does not explicitly raise any errors or exceptions.
        """
        self.play_video = play_video
        Display = self.play_video.win
        self.display_width = Display.get_width()
        self.display_height = Display.get_height()
        self.filterCheckboxPanel_is_visible = False
        self.BOX_WIDTH_BASE = 800

        # filter label tooltip
        self.filter_label_tooltip = None
        self.tooltip_surface = None

        # Calculate panel dimensions with 35% height reduction
        total_height = self.calculate_total_height()
        self.BOX_HEIGHT_BASE = int(total_height * 1)

        # Setup scaling
        self.setup_scaling()

        # Define CUDA-enabled filters
        self.cuda_filters = {'Bilateral', 'Laplacian', 'Gaussian-Blur', 'Emboss',
                             'Median-Blur' ,'Greyscale', 'Sepia', 'Saturation',
                             'Edge Detect', 'Edges-Sobel', 'Contrast Enhance'
        }
        # Create checkboxes
        self.checkboxes = []
        self.setup_checkboxes()

    def is_visible(self):
        """
        Checks whether the filter checkbox panel is visible.

        This method determines the visibility state of the filter checkbox panel.
        It returns a boolean indicating if the panel is currently visible.

        Returns:
            bool: True if the filter checkbox panel is visible, False otherwise.
        """
        return self.filterCheckboxPanel_is_visible

    def set_visible(self, is_visible):
        """
        Updates the visibility of the filter checkbox panel and ensures checkbox states
        are synchronized with the filter map when the panel becomes visible.

        Parameters
        ----------
        is_visible : bool
            Indicates whether the filter checkbox panel should be visible.

        Raises
        ------
        KeyError
            If a checkbox label is not found in the filter map.

        Notes
        -----
        When the panel is set to be visible, the method updates each checkbox's
        checked state based on the corresponding data in the filter map.
        """
        self.filterCheckboxPanel_is_visible = is_visible
        if is_visible:
            # Update checkbox states when panel becomes visible
            filter_map = self.get_filter_map()
            for checkbox in self.checkboxes:
                filter_info = filter_map.get(checkbox.label)
                if filter_info is not None:
                    checkbox.checked = filter_info['enabled']

    def toggle_visibility(self):
        """
        Toggles the visibility state of the filter checkbox panel.

        This method inverts the current visibility state of the filter checkbox
        panel, effectively toggling it between visible and hidden.

        Returns:
            None
        """
        self.filterCheckboxPanel_is_visible = not self.filterCheckboxPanel_is_visible
        self.set_visible(self.filterCheckboxPanel_is_visible)

    def calculate_total_height(self):
        """
        Calculate the total height required for a UI component.

        This method computes the total height needed for a user interface component
        by summing up the heights of different elements, including the title, spacing
        for content rows, button, and padding at the bottom.

        Returns:
            int: The total calculated height for the UI component.
        """
        title_height = 40
        content_start = 60
        row_spacing = 45
        button_height = 40
        bottom_padding = 20
        content_height = (len(self.get_filter_list()) // 2 + 1) * row_spacing
        return title_height + content_height + button_height + bottom_padding

    def setup_scaling(self):
        """
        Sets up scaling for box dimensions and position based on the display size.

        This method computes the width, height, and position of a box centered on the
        display. The dimensions are initialized based on predefined base values, and
        the box is centered horizontally and vertically with an additional offset
        applied to its vertical position.

        Attributes
        ----------
        BOX_WIDTH : int
            The width of the box after scaling.
        BOX_HEIGHT : int
            The height of the box after scaling.
        BOX_X : int
            The x-coordinate of the top-left corner of the box after centering horizontally.
        BOX_Y : int
            The y-coordinate of the top-left corner of the box after centering vertically
            with an additional vertical offset.
        """
        # Add existing scaling code here
        self.BOX_WIDTH = self.BOX_WIDTH_BASE
        self.BOX_HEIGHT = self.BOX_HEIGHT_BASE
        self.BOX_X = (self.display_width - self.BOX_WIDTH) // 2
        self.BOX_Y = (self.display_height - self.BOX_HEIGHT) // 2 - 50

    def setup_checkboxes(self):
        """
        Sets up checkbox UI components with corresponding filters and their states.

        This method initializes the positions and appearances of checkboxes based
        on the filter map retrieved from the configuration. Filters are divided into
        two columns, and each filter is represented by a checkbox. For CUDA-related
        filters, a GPU icon is assigned to the checkbox.

        Attributes
        ----------
        checkbox_size : int
            The size of each checkbox in pixels.
        gpu_icon : pygame.Surface
            A GPU icon loaded and scaled for display in checkboxes related to CUDA filters.
        start_x : int
            The x-coordinate of the starting position for checkboxes.
        start_y : int
            The y-coordinate of the starting position for checkboxes.
        row_spacing : int
            The vertical spacing between checkboxes in a column.
        column_width : int
            The width allocated to a single column of checkboxes.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        gpu_icon = pygame.image.load(os.path.join(self.play_video.RESOURCES_DIR, 'cuda.svg')).convert_alpha()
        gpu_icon = pygame.transform.scale(gpu_icon, (24, 24))

        # Get the current filter states from opts
        filter_map = self.get_filter_map()

        # Setup checkboxes with their current states
        column_count = (len(filter_map) + 1) // 2
        checkbox_size = 20
        start_x = self.BOX_X + 50
        start_y = self.BOX_Y + 80
        row_spacing = 45
        column_width = self.BOX_WIDTH // 2

        # Create checkboxes in the first column
        for i, (filter_name, filter_info) in enumerate(list(filter_map.items())[:column_count]):
            checkbox = Checkbox(start_x, start_y + (i * row_spacing), checkbox_size)
            checkbox.set_label(filter_name)
            checkbox.checked = filter_info['enabled']  # Set the initial state from self.play_video.opts
            # If it's a CUDA filter, store the icon reference
            if filter_name in self.cuda_filters:
                checkbox.gpu_icon = gpu_icon
            self.checkboxes.append(checkbox)

        # Create checkboxes in the second column
        for i, (filter_name, filter_info) in enumerate(list(filter_map.items())[column_count:]):
            checkbox = Checkbox(start_x + column_width, start_y + (i * row_spacing), checkbox_size)
            checkbox.set_label(filter_name)
            checkbox.checked = filter_info['enabled']  # Set the initial state from self.play_video.opts
            # If it's a CUDA filter, store the icon reference
            if filter_name in self.cuda_filters:
                checkbox.gpu_icon = gpu_icon
            self.checkboxes.append(checkbox)

    def get_filter_list(self):
        """
        Retrieves the list of available filters.

        This method accesses the filter map, extracting the keys which represent
        the available filter names, and compiles them into a list.

        Returns:
            list: A list of filter names derived from the filter map.
        """
        filter_map = self.get_filter_map()
        return list(filter_map.keys())

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
            'Laplacian': {
                'enabled': getattr(self.play_video.opts, 'apply_laplacian')
            },
            'U-Sharp': {
                'enabled': getattr(self.play_video.opts, 'apply_sharpening')
            },
            'Blur': {
                'enabled': getattr(self.play_video.opts, 'blur')
            },
            'Median-Blur': {
                'enabled': getattr(self.play_video.opts, 'median_blur')
            },
            'Gaussian-Blur': {
                'enabled': getattr(self.play_video.opts, 'gaussian_blur')
            },
            'Noise': {
                'enabled': getattr(self.play_video.opts, 'noise')
            },
            'Denoise': {
                'enabled': getattr(self.play_video.opts, 'apply_denoising')
            },
            'Greyscale': {
                'enabled': getattr(self.play_video.opts, 'greyscale')
            },
            'Sepia': {
                'enabled': getattr(self.play_video.opts, 'sepia')
            },
            'Cel-Shading': {
                'enabled': getattr(self.play_video.opts, 'cel_shading')
            },
            'Saturation': {
                'enabled': getattr(self.play_video.opts, 'saturation')
            },
            'Contrast Enhance': {
                'enabled': getattr(self.play_video.opts, 'apply_contrast_enhancement')
            },
            'Bright/Contrast': {
                'enabled': getattr(self.play_video.opts, 'apply_adjust_video')
            },
            'Vignette': {
                'enabled': getattr(self.play_video.opts, 'vignette')
            },
            'Thermal': {
                'enabled': getattr(self.play_video.opts, 'thermal')
            },
            'Emboss': {
                'enabled': getattr(self.play_video.opts, 'emboss')
            },
            'Dream': {
                'enabled': getattr(self.play_video.opts, 'dream')
            },
            'Neon': {
                'enabled': getattr(self.play_video.opts, 'neon')
            },
            'Pixelate': {
                'enabled': getattr(self.play_video.opts, 'pixelate')
            },
            'Invert': {
                'enabled': getattr(self.play_video.opts, 'apply_inverted')
            },
            'Flip-Left-Right': {
                'enabled': getattr(self.play_video.opts, 'fliplr')
            },
            'Flip-Up-Down': {
                'enabled': getattr(self.play_video.opts, 'flipup')
            },
            'Comic': {
                'enabled': getattr(self.play_video.opts, 'comic')
            },
            'Comic-Sharp': {
                'enabled': getattr(self.play_video.opts, 'comic_sharp')
            },
            'Oil Painting': {
                'enabled': getattr(self.play_video.opts, 'oil_painting')
            },
            'Watercolor': {
                'enabled': getattr(self.play_video.opts, 'watercolor')
            },
            'Pencil Sketch': {
                'enabled': getattr(self.play_video.opts, 'pencil_sketch')
            },
            'Edges-Sobel': {
                'enabled': getattr(self.play_video.opts, 'apply_edges_sobel')
            },
            'Edge Detect': {
                'enabled': getattr(self.play_video.opts, 'apply_edge_detect')
            },
            'Artistic': {
                'enabled': getattr(self.play_video.opts, 'apply_artistic_filters')
            },
            'Bilateral': {
                'enabled': getattr(self.play_video.opts, 'apply_bilateral_filter')
            }
        }
        return filter_map

    def get_filter_tooltip(self, filter_name):
        """
        Retrieves a tooltip description for a specified filter.

        The method matches a filter name to its corresponding
        tooltip description from a predefined mapping. The tooltip
        provides insight into the functionality and/or
        characteristics of the filter.

        Parameters:
            filter_name (str): The name of the filter for which to
            retrieve the tooltip description.

        Returns:
            str: The tooltip description associated with the filter
            name.

        Raises:
            KeyError: If the specified filter_name does not exist in
            the predefined filter map.
        """
        filter_map = {
            'Laplacian': 'Laplacian Boost Filter.  CUDA-Accelerated',
            'U-Sharp': 'U-Sharp Filter',
            'Blur': 'Blur Filter',
            'Median-Blur': 'Median-Blur Filter, Kernel Size: 3, CUDA-Accelerated',
            'Gaussian-Blur': 'Gaussian-Blur Filter, Kernel Size: 5,5, SigmaX: 0, CUDA-Accelerated',
            'Noise': 'Apply Noise to a video frame',
            'Denoise': 'Remove noise from a video frame (S-L-O-W)',
            'Greyscale': 'Convert video to greyscale. CUDA-Accelerated',
            'Sepia': 'Apply sepia filter. Presets: Classic, Warm, Cool, Vintage. CUDA-Accelerated',
            'Cel-Shading': 'Apply cel-shading filter',
            'Saturation': 'Color Saturation Adjustment Filter.  CUDA-Accelerated',
            'Contrast Enhance': 'Contrast Enhancement Filter. CUDA-Accelerated',
            'Bright/Contrast': 'Apply Bright/Contrast Filter (Very Fast)',
            'Vignette': 'Apply Vignette Filter',
            'Thermal': 'Apply Thermal Filter',
            'Emboss': 'Emboss Filter.  CUDA-Accelerated',
            'Dream': 'Apply Dream Filter',
            'Neon': 'Apply Neon Filter',
            'Pixelate': 'Apply Pixelate Filter',
            'Invert': 'Invert Filter',
            'Flip-Left-Right': 'Flip Left-Right Filter',
            'Flip-Up-Down': 'Flip Up-Down Filter',
            'Comic': 'Comic Filter',
            'Comic-Sharp': 'Comic-Sharp Filter',
            'Oil Painting': 'Oil Painting Filter',
            'Watercolor': 'Watercolor Filter',
            'Pencil Sketch': 'Pencil Sketch Filter',
            'Edges-Sobel': 'Apply Sobel Filter. CUDA-Accelerated',
            'Edge Detect': 'Edge Detect Filter. CUDA-Accelerated',
            'Artistic': 'Artistic Filter',
            'Bilateral': 'Apply Bilateral Filter. CUDA-Accelerated'
        }
        return filter_map[filter_name]

    def draw(self, screen):
        """
        Draws the filter checkbox panel on the given screen.

        This function renders the UI section for post-processing filter controls, including
        a gradient background, a bordered rectangle, a title, and individual checkboxes.

        NOTE: If the filter checkbox panel is not visible, this function does nothing.

        Parameters:
        screen : pygame.Surface
            The surface where the filter checkbox panel is drawn.
        """
        if not self.is_visible():
            return

        gradient_surface = pygame.Surface((self.BOX_WIDTH, self.BOX_HEIGHT), pygame.SRCALPHA)
        self.play_video.apply_gradient(
            gradient_surface,
            (0, 0, 255),
            (0, 0, 100),
            self.BOX_WIDTH,
            self.BOX_HEIGHT,
            alpha_start=185,
            alpha_end=255
        )

        pygame.draw.rect(
            screen,
            DODGERBLUE,
            (self.BOX_X, self.BOX_Y, self.BOX_WIDTH, self.BOX_HEIGHT),
            6,
            border_radius=8
        )

        screen.blit(gradient_surface, (self.BOX_X, self.BOX_Y))

        # Draw title
        title_font = pygame.font.Font(None, 52)
        title = title_font.render("Post-Processing Filters", True, HEADING_COLOR)
        screen.blit(title, (self.BOX_X + (self.BOX_WIDTH - title.get_width()) // 2,
                            self.BOX_Y + 20))

        # Draw checkboxes
        for checkbox in self.checkboxes:
            checkbox.draw(screen)

    def handle_event(self, event):
        """
        Handles user interaction with checkboxes and updates filter options accordingly.

        This method processes an event, checks if the current UI component is visible,
        and iterates over a list of checkboxes to determine which one has been interacted
        with. If a checkbox is toggled, the corresponding filter attribute in the video
        options is updated, and the video is reinitialized with the updated configuration.
        Specific filter attributes correspond to various video effects and are updated
        based on the label of the interacted checkbox.

        Parameters:
        event (Event): The event data that is used to detect interactions with
        checkboxes.

        Returns:
        bool: True if any checkbox interaction was handled; otherwise, False.
        """
        if not self.is_visible():
            return False

        for checkbox in self.checkboxes:
            if checkbox.handle_event(event):
                # Update the corresponding filter state in opts
                filter_name = checkbox.label
                match filter_name:
                    case 'Laplacian':
                        setattr(self.play_video.opts, 'apply_laplacian', checkbox.checked)
                        self.play_video.laplacian_panel.set_visible(checkbox.checked)

                        if self.play_video.laplacian_panel.is_visible:
                            if self.play_video.edge_panel.is_visible:
                                self.play_video.edge_panel.toggle_visibility()
                            elif self.play_video.saturation_panel.is_visible:
                                self.play_video.saturation_panel.toggle_visibility()
                            elif self.play_video.bilateral_panel.is_visible():
                                self.play_video.bilateral_panel.toggle_visibility()
                            elif self.play_video.sepia_panel.is_visible:
                                self.play_video.sepia_panel.toggle_visibility()
                            elif self.play_video.control_panel.is_visible:
                                self.play_video.control_panel.toggle_visibility()
                            elif self.play_video.oil_painting_panel.is_visible:
                                self.play_video.oil_painting_panel.toggle_visibility()
                        self.play_video.reInitVideo('laplacian',self.play_video.vid.frame)
                    case 'U-Sharp':
                        setattr(self.play_video.opts, 'apply_sharpening', checkbox.checked)
                        self.play_video.reInitVideo('apply_sharpening',self.play_video.vid.frame)
                    case 'Blur':
                        setattr(self.play_video.opts, 'blur', checkbox.checked)
                        self.play_video.reInitVideo('blur',self.play_video.vid.frame)
                    case 'Median-Blur':
                        setattr(self.play_video.opts, 'median_blur', checkbox.checked)
                        self.play_video.reInitVideo('median_blur',self.play_video.vid.frame)
                    case 'Gaussian-Blur':
                        setattr(self.play_video.opts, 'gaussian_blur', checkbox.checked)
                        self.play_video.reInitVideo('gaussian_blur',self.play_video.vid.frame)
                    case 'Noise':
                        setattr(self.play_video.opts, 'noise', checkbox.checked)
                        self.play_video.reInitVideo('apply_noise',self.play_video.vid.frame)
                    case 'Denoise':
                        setattr(self.play_video.opts, 'apply_denoising', checkbox.checked)
                        self.play_video.reInitVideo('apply_denoising',self.play_video.vid.frame)
                    case 'Greyscale':
                        if self.play_video.opts.apply_sepia or self.play_video.opts.thermal or self.play_video.opts.emboss or self.play_video.opts.dream or self.play_video.opts.neon or self.play_video.opts.vignette or self.play_video.opts.saturation:
                            if self.play_video.opts.apply_sepia:  # is sepia enabled?
                                cb = self.find_checkbox_by_label('Sepia')
                                cb.checked = False
                                self.play_video.apply_sepia = False
                                self.play_video.opts.sepia = False
                                self.play_video.sepia_panel.set_visible(False)

                            if self.play_video.opts.saturation:
                                cb = self.find_checkbox_by_label('Saturation')
                                cb.checked = False
                                self.play_video.opts.saturation = False
                                self.play_video.opts.apply_saturation = False

                            if self.play_video.opts.thermal:
                                cb = self.find_checkbox_by_label('Thermal')
                                cb.checked = False
                                self.play_video.opts.thermal = False

                            if self.play_video.opts.emboss:
                                cb = self.find_checkbox_by_label('Emboss')
                                cb.checked = False
                                self.play_video.opts.emboss = False

                            if self.play_video.opts.dream:
                                cb = self.find_checkbox_by_label('Dream')
                                cb.checked = False
                                self.play_video.opts.dream = False

                            if self.play_video.opts.neon:
                                cb = self.find_checkbox_by_label('Neon')
                                cb.checked = False
                                self.play_video.opts.neon = False

                            if self.play_video.opts.vignette:
                                cb = self.find_checkbox_by_label('Vignette')
                                cb.checked = False
                                self.play_video.opts.vignette = False
                            if self.play_video.opts.sepia:
                                cb = self.find_checkbox_by_label('Sepia')
                                cb.checked = False
                                self.play_video.opts.sepia = False
                                self.play_video.opts.apply_sepia = False

                            if self.play_video.opts.saturation:
                                cb = self.find_checkbox_by_label('Saturation')
                                cb.checked = False
                                self.play_video.opts.saturation = False
                                self.play_video.opts.apply_saturation = False

                            if self.play_video.opts.thermal:
                                cb = self.find_checkbox_by_label('Thermal')
                                cb.checked = False
                                self.play_video.opts.thermal = False

                            if self.play_video.opts.emboss:
                                cb = self.find_checkbox_by_label('Emboss')
                                cb.checked = False
                                self.play_video.opts.emboss = False

                            if self.play_video.opts.dream:
                                cb = self.find_checkbox_by_label('Dream')
                                cb.checked = False
                                self.play_video.opts.dream = False

                            if self.play_video.opts.neon:
                                cb = self.find_checkbox_by_label('Neon')
                                cb.checked = False
                                self.play_video.opts.neon = False

                            if self.play_video.opts.vignette:
                                cb = self.find_checkbox_by_label('Vignette')
                                cb.checked = False
                                self.play_video.opts.vignette = False

                        setattr(self.play_video.opts, 'greyscale', checkbox.checked)        # enable greyscale
                        if self.play_video.sepia_panel.is_visible:
                            self.play_video.sepia_panel.toggle_visibility()
                        elif self.play_video.edge_panel.is_visible:
                            self.play_video.edge_panel.toggle_visibility()
                        elif self.play_video.bilateral_panel.is_visible():
                            self.play_video.bilateral_panel.toggle_visibility()
                        elif self.play_video.saturation_panel.is_visible:
                            self.play_video.saturation_panel.toggle_visibility()
                        elif self.play_video.control_panel.is_visible:
                            self.play_video.control_panel.toggle_visibility()
                        elif self.play_video.oil_painting_panel.is_visible:
                            self.play_video.oil_painting_panel.toggle_visibility()
                        elif self.play_video.laplacian_panel.is_visible:
                            self.play_video.laplacian_panel.toggle_visibility()
                        self.play_video.reInitVideo('greyscale',self.play_video.vid.frame)  # update the post-processing filter chain
                    case 'Sepia':
                        if self.play_video.opts.greyscale or self.play_video.opts.thermal or self.play_video.opts.emboss or self.play_video.opts.dream or self.play_video.opts.neon or self.play_video.opts.vignette or self.play_video.opts.saturation:
                            if self.play_video.opts.greyscale:
                                cb = self.find_checkbox_by_label('Greyscale')
                                cb.checked = False
                                self.play_video.opts.greyscale = False

                            if self.play_video.opts.saturation:
                                cb = self.find_checkbox_by_label('Saturation')
                                cb.checked = False
                                self.play_video.opts.saturation = False
                                self.play_video.opts.apply_saturation = False

                            if self.play_video.opts.thermal:
                                cb = self.find_checkbox_by_label('Thermal')
                                cb.checked = False
                                self.play_video.opts.thermal = False

                            if self.play_video.opts.emboss:
                                cb = self.find_checkbox_by_label('Emboss')
                                cb.checked = False
                                self.play_video.opts.emboss = False

                            if self.play_video.opts.dream:
                                cb = self.find_checkbox_by_label('Dream')
                                cb.checked = False
                                self.play_video.opts.dream = False

                            if self.play_video.opts.neon:
                                cb = self.find_checkbox_by_label('Neon')
                                cb.checked = False
                                self.play_video.opts.neon = False

                            if self.play_video.opts.vignette:
                                cb = self.find_checkbox_by_label('Vignette')
                                cb.checked = False
                                self.play_video.opts.vignette = False
                            if self.play_video.opts.greyscale:
                                cb = self.find_checkbox_by_label('Greyscale')
                                cb.checked = False
                                self.play_video.opts.greyscale = False

                            if self.play_video.opts.saturation:
                                cb = self.find_checkbox_by_label('Saturation')
                                cb.checked = False
                                self.play_video.opts.saturation = False
                                self.play_video.opts.apply_saturation = False

                            if self.play_video.opts.thermal:
                                cb = self.find_checkbox_by_label('Thermal')
                                cb.checked = False
                                self.play_video.opts.thermal = False

                            if self.play_video.opts.emboss:
                                cb = self.find_checkbox_by_label('Emboss')
                                cb.checked = False
                                self.play_video.opts.emboss = False

                            if self.play_video.opts.dream:
                                cb = self.find_checkbox_by_label('Dream')
                                cb.checked = False
                                self.play_video.opts.dream = False

                            if self.play_video.opts.neon:
                                cb = self.find_checkbox_by_label('Neon')
                                cb.checked = False
                                self.play_video.opts.neon = False

                            if self.play_video.opts.vignette:
                                cb = self.find_checkbox_by_label('Vignette')
                                cb.checked = False
                                self.play_video.opts.vignette = False

                        setattr(self.play_video.opts, 'apply_sepia', checkbox.checked)
                        self.play_video.sepia_panel.set_visible(checkbox.checked)
                        if self.play_video.sepia_panel.is_visible:
                            if self.play_video.edge_panel.is_visible:
                                self.play_video.edge_panel.toggle_visibility()
                            elif self.play_video.bilateral_panel.is_visible():
                                self.play_video.bilateral_panel.toggle_visibility()
                            elif self.play_video.saturation_panel.is_visible:
                                self.play_video.saturation_panel.toggle_visibility()
                            elif self.play_video.control_panel.is_visible:
                                self.play_video.control_panel.toggle_visibility()
                            elif self.play_video.oil_painting_panel.is_visible:
                                self.play_video.oil_painting_panel.toggle_visibility()
                            elif self.play_video.laplacian_panel.is_visible:
                                self.play_video.laplacian_panel.toggle_visibility()
                        self.play_video.reInitVideo('sepia',self.play_video.vid.frame)
                    case 'Cel-Shading':
                        setattr(self.play_video.opts, 'cel_shading', checkbox.checked)
                        self.play_video.reInitVideo('cel_shading',self.play_video.vid.frame)
                    case 'Saturation':
                        if self.play_video.opts.apply_sepia or self.play_video.opts.vignette or self.play_video.opts.greyscale or self.play_video.opts.apply_adjust_video:

                            if self.play_video.opts.apply_sepia:  # is sepia enabled?
                                cb = self.find_checkbox_by_label('Sepia')
                                cb.checked = False
                                self.play_video.apply_sepia = False
                                self.play_video.opts.sepia = False

                            if self.play_video.opts.greyscale:
                                cb = self.find_checkbox_by_label('Greyscale')
                                cb.checked = False
                                self.play_video.opts.greyscale = False

                            if self.play_video.opts.vignette:
                                cb = self.find_checkbox_by_label('Vignette')
                                cb.checked = False
                                self.play_video.opts.vignette = False

                            if self.play_video.opts.apply_adjust_video:
                                cb = self.find_checkbox_by_label('Bright/Contrast')
                                cb.checked = False
                                self.play_video.opts.apply_adjust_video = False

                        setattr(self.play_video.opts, 'apply_saturation', checkbox.checked)
                        self.play_video.saturation_panel.set_visible(checkbox.checked)
                        if self.play_video.saturation_panel.is_visible:
                            if self.play_video.edge_panel.is_visible:
                                self.play_video.edge_panel.toggle_visibility()
                            elif self.play_video.sepia_panel.is_visible:
                                self.play_video.sepia_panel.toggle_visibility()
                            elif self.play_video.bilateral_panel.is_visible():
                                self.play_video.bilateral_panel.toggle_visibility()
                            elif self.play_video.control_panel.is_visible:
                                self.play_video.control_panel.toggle_visibility()
                            elif self.play_video.oil_painting_panel.is_visible:
                                self.play_video.oil_painting_panel.toggle_visibility()
                            elif self.play_video.laplacian_panel.is_visible:
                                self.play_video.laplacian_panel.toggle_visibility()
                        self.play_video.reInitVideo('saturation',self.play_video.vid.frame)
                    case 'Contrast Enhance':
                        setattr(self.play_video.opts, 'apply_contrast_enhancement', checkbox.checked)
                        self.play_video.reInitVideo('apply_contrast_enhancement',self.play_video.vid.frame)
                    case 'Bright/Contrast':
                        if self.play_video.opts.saturation or self.play_video.opts.apply_saturation:
                            cb = self.find_checkbox_by_label('Saturation')
                            cb.checked = False
                            self.play_video.opts.saturation = False
                            self.play_video.opts.apply_saturation = False

                        setattr(self.play_video.opts, 'apply_adjust_video', checkbox.checked)
                        self.play_video.control_panel.set_visible(checkbox.checked)
                        if self.play_video.control_panel.is_visible:
                            if self.play_video.edge_panel.is_visible:
                                self.play_video.edge_panel.toggle_visibility()
                            elif self.play_video.bilateral_panel.is_visible():
                                self.play_video.bilateral_panel.toggle_visibility()
                            elif self.play_video.saturation_panel.is_visible:
                                self.play_video.saturation_panel.toggle_visibility()
                            elif self.play_video.sepia_panel.is_visible:
                                self.play_video.sepia_panel.toggle_visibility()
                            elif self.play_video.oil_painting_panel.is_visible:
                                self.play_video.oil_painting_panel.toggle_visibility()
                            elif self.play_video.laplacian_panel.is_visible:
                                self.play_video.laplacian_panel.toggle_visibility()
                        self.play_video.reInitVideo('apply_adjust_video',self.play_video.vid.frame)
                    case 'Vignette':
                        if self.play_video.opts.greyscale or self.play_video.opts.sepia or self.play_video.opts.apply_adjust_video or self.play_video.opts.saturation:
                            if self.play_video.opts.greyscale:
                                cb = self.find_checkbox_by_label('Greyscale')
                                cb.checked = False
                                self.play_video.opts.greyscale = False

                            if self.play_video.opts.sepia:
                                cb = self.find_checkbox_by_label('Sepia')
                                cb.checked = False
                                self.play_video.opts.sepia = False
                                self.play_video.opts.apply_sepia = False
                                self.play_video.sepia_panel.set_visible(False)

                            if self.play_video.opts.apply_adjust_video:
                                cb = self.find_checkbox_by_label('Bright/Contrast')
                                cb.checked = False
                                self.play_video.opts.apply_adjust_video = False
                                self.play_video.control_panel.set_visible(False)

                            if self.play_video.opts.saturation:
                                cb = self.find_checkbox_by_label('Saturation')
                                cb.checked = False
                                self.play_video.opts.saturation = False
                                self.play_video.saturation_panel.set_visible(False)
                                self.play_video.opts.apply_saturation = False
                                self.play_video.saturation_panel.set_visible(False)

                        setattr(self.play_video.opts, 'vignette', checkbox.checked)
                        self.play_video.reInitVideo('vignette',self.play_video.vid.frame)
                    case 'Thermal':
                        setattr(self.play_video.opts, 'thermal', checkbox.checked)
                        self.play_video.reInitVideo('thermal',self.play_video.vid.frame)
                    case 'Emboss':
                        setattr(self.play_video.opts, 'emboss', checkbox.checked)
                        self.play_video.reInitVideo('emboss',self.play_video.vid.frame)
                    case 'Dream':
                        setattr(self.play_video.opts, 'dream', checkbox.checked)
                        self.play_video.reInitVideo('dream',self.play_video.vid.frame)
                    case 'Neon':
                        setattr(self.play_video.opts, 'neon', checkbox.checked)
                        self.play_video.reInitVideo('neon',self.play_video.vid.frame)
                    case 'Pixelate':
                        setattr(self.play_video.opts, 'pixelate', checkbox.checked)
                        self.play_video.reInitVideo('pixelate',self.play_video.vid.frame)
                    case 'Invert':
                        setattr(self.play_video.opts, 'apply_inverted', checkbox.checked)
                        self.play_video.reInitVideo('apply_inverted',self.play_video.vid.frame)
                    case 'Flip-Left-Right':
                        setattr(self.play_video.opts, 'fliplr', checkbox.checked)
                        self.play_video.reInitVideo('fliplr',self.play_video.vid.frame)
                    case 'Flip-Up-Down':
                        setattr(self.play_video.opts, 'flipup', checkbox.checked)
                        self.play_video.reInitVideo('flipup',self.play_video.vid.frame)
                    case 'Comic':
                        setattr(self.play_video.opts, 'comic', checkbox.checked)
                        self.play_video.reInitVideo('comic',self.play_video.vid.frame)
                    case 'Comic-Sharp':
                        setattr(self.play_video.opts, 'comic_sharp', checkbox.checked)
                        self.play_video.reInitVideo('comic_sharp',self.play_video.vid.frame)
                    case 'Oil Painting':
                        setattr(self.play_video.opts, 'apply_oil_painting', checkbox.checked)
                        self.play_video.oil_painting_panel.set_visible(checkbox.checked)
                        if self.play_video.edge_panel.is_visible:
                            self.play_video.edge_panel.toggle_visibility()
                        elif self.play_video.bilateral_panel.is_visible():
                            self.play_video.bilateral_panel.toggle_visibility()
                        elif self.play_video.saturation_panel.is_visible:
                            self.play_video.saturation_panel.toggle_visibility()
                        elif self.play_video.sepia_panel.is_visible:
                            self.play_video.sepia_panel.toggle_visibility()
                        elif self.play_video.control_panel.is_visible:
                            self.play_video.control_panel.toggle_visibility()
                        elif self.play_video.laplacian_panel.is_visible:
                            self.play_video.laplacian_panel.toggle_visibility()
                        self.play_video.reInitVideo('oil_painting',self.play_video.vid.frame)
                    case 'Watercolor':
                        setattr(self.play_video.opts, 'watercolor', checkbox.checked)
                        self.play_video.reInitVideo('watercolor',self.play_video.vid.frame)
                    case 'Pencil Sketch':
                        setattr(self.play_video.opts, 'pencil_sketch', checkbox.checked)
                        self.play_video.reInitVideo('pencil_sketch',self.play_video.vid.frame)
                    case 'Edges-Sobel':
                        setattr(self.play_video.opts, 'apply_edges_sobel', checkbox.checked)
                        self.play_video.reInitVideo('apply_edges_sobel',self.play_video.vid.frame)
                    case 'Edge Detect':
                        setattr(self.play_video.opts, 'apply_edge_detect', checkbox.checked)
                        self.play_video.edge_panel.set_visible(checkbox.checked)
                        if self.play_video.edge_panel.is_visible:
                            if self.play_video.control_panel.is_visible:
                                self.play_video.control_panel.toggle_visibility()
                            elif self.play_video.saturation_panel.is_visible:
                                self.play_video.saturation_panel.toggle_visibility()
                            elif self.play_video.sepia_panel.is_visible:
                                self.play_video.sepia_panel.toggle_visibility()
                            elif self.play_video.oil_painting_panel.is_visible:
                                self.play_video.oil_painting_panel.toggle_visibility()
                            elif self.play_video.laplacian_panel.is_visible:
                                self.play_video.laplacian_panel.toggle_visibility()
                        self.play_video.reInitVideo('edge_detect',self.play_video.vid.frame)
                    case 'Artistic':
                        setattr(self.play_video.opts, 'apply_artistic_filters', checkbox.checked)
                        self.play_video.reInitVideo('apply_artistic_filters',self.play_video.vid.frame)
                    case 'Bilateral':
                        setattr(self.play_video.opts, 'apply_bilateral_filter', checkbox.checked)
                        if self.play_video.edge_panel.is_visible:
                            self.play_video.edge_panel.toggle_visibility()
                        elif self.play_video.sepia_panel.is_visible:
                            self.play_video.sepia_panel.toggle_visibility()
                        elif self.play_video.saturation_panel.is_visible:
                            self.play_video.saturation_panel.toggle_visibility()
                        elif self.play_video.control_panel.is_visible:
                            self.play_video.control_panel.toggle_visibility()
                        elif self.play_video.laplacian_panel.is_visible:
                            self.play_video.laplacian_panel.toggle_visibility()
                        self.play_video.reInitVideo('apply_bilateral_filter_panel',self.play_video.vid.frame)
                return True
        return False

    def find_checkbox_by_label(self, label):
        """
        Find a checkbox by its label in the checkboxes list.

        Parameters
        ----------
        label : str
            The label text to search for

        Returns
        -------
        Checkbox or None
            The found checkbox object or None if not found
        """
        for checkbox in self.checkboxes:
            if checkbox.label == label:
                return checkbox
        return None

        # Tooltip function

    def draw_tooltip(self, disp_surface, text, x, y):
        """
        Draws a tooltip on the provided display surface at the specified coordinates with the given text. The tooltip
        is styled with a blue background, a border, and displays the text in bold font. The tooltip size is adjusted
        based on the scaled font size and the length of the text provided. This function ensures proper text
        visibility on the user interface by rendering the tooltip dynamically.

        Args:
            disp_surface (pygame.Surface): The display surface where the tooltip will be drawn.
            text (str): The textual content to display within the tooltip.
            x (int): The x-coordinate of the tooltip's top-left corner on the display surface.
            y (int): The y-coordinate of the tooltip's top-left corner on the display surface.
        """

        USER_HOME = os.path.expanduser("~")
        FONT_DIR = USER_HOME + "/.local/share/pyVid/fonts/"
        scaled_font_size = up_scale.scale_font(18, self.display_height)
        tooltip_font = pygame.font.Font(FONT_DIR + "Montserrat-Bold.ttf", scaled_font_size)
        self.tooltip_surface = tooltip_font.render(text, True, WHITE)
        tooltip_width, tooltip_height = self.tooltip_surface.get_size()

        pygame.draw.rect(
            disp_surface,
            DODGERBLUE,
            (x, y, tooltip_width + 10, tooltip_height + 8),
            border_radius=8
        )

        pygame.draw.rect(
            disp_surface,
            DODGERBLUE4,
            (x, y, tooltip_width + 10, tooltip_height + 8),
            1,
            border_radius=8
        )

        disp_surface.blit(self.tooltip_surface, (x + 5, y + 3))
