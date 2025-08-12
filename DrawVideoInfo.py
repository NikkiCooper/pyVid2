#  DrawVideoInfo.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
#  Class to display a video metadata information box.
import json
import pygame
import subprocess
import upScale as up_scale

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DODGERBLUE = (30, 144, 255)
DODGERBLUE4 = (16, 78, 139)
HEADING_COLOR = (255, 200, 0)  # Yellow for headings

class DrawVideoInfo:
    """
    Represents a display for video information, utilizing UI elements and fonts.

    This class is designed to handle the creation and rendering of information
    about a video file, such as its filename, filepath, and metadata. It manages
    font loading, text wrapping, tooltip rendering, and the configuration of
    key graphical elements like dialog boxes and buttons. It also supports scaling
    based on the display resolution and includes utility functions for text
    truncation and wrapping.

    Attributes:
        display: The pygame display surface used for rendering UI.
        display_width: The width of the display surface in pixels.
        display_height: The height of the display surface in pixels.
        resolution: A tuple representing the resolution of the display (width, height).
        displayType: The type of display scaled based on resolution.
        filename: The name of the video file being displayed.
        filepath: The path to the directory containing the video file.
        USER_HOME: The user's home directory path.
        FONT_DIR: Path to the directory containing application fonts.
        RESOURCES_DIR: Path to the directory containing application resources.
        filename_rect: The rectangle bounding the filename text surface.
        filename_surface: The surface used for rendering the filename.
        path_rect: The rectangle bounding the filepath text surface.
        path_surface: The surface used for rendering the filepath.
        font_filename: The font used for displaying filenames.
        font_filepath: The font used for displaying filepaths.
        font_button: The font used for displaying button text.
        font_info: The font used for displaying additional information.
        font_info_bold: The bold font used for displaying emphasized information.
        check_icon: A checkmark icon loaded and scaled for display.
        filepath_wrap_width: The maximum width in pixels for wrapping filepaths.
        wrapped_filepath_lines: A list of wrapped filepath lines based on the wrap width.
        num_filepath_lines: The number of wrapped lines in the filepath.
        video_metadata: Metadata parsed from the video file.
        temp_hide: A boolean indicating whether the information box is temporarily hidden.
        BOX_WIDTH_BASE: The base width of the dialog box, used for scaling.
        num_metadata_lines: The number of metadata lines plus additional filepath lines.
        BOX_HEIGHT_BASE: The base height of the dialog box, dynamically adjusted with metadata.
        BOX_WIDTH: The actual width of the dialog box after scaling.
        BOX_HEIGHT: The actual height of the dialog box after scaling.
        BOX_X: The x-coordinate for positioning the dialog box on screen.
        BOX_Y: The y-coordinate for positioning the dialog box on screen.
        is_hovered: A boolean indicating whether the dialog box is being hovered over.
        button_rect: A rectangle defining the position and size of the button.

    Methods:
        wrap_text(text, font, max_width):
            Static method to wrap text within a maximum width using a specific font.

        truncate_text(text, font, max_width):
            Static method to truncate text with ellipses if it exceeds a maximum width.

        truncate_path(path, max_length):
            Static method to truncate paths with ellipses while keeping a defined character limit.

        draw_tooltip(disp_surface, text, x, y):
            Renders a tooltip with the given text at a specified position.

        draw_path_tooltip(disp_surface, text, x, y):
            Renders a tooltip specific to a filepath at a specified position.

        draw_info_box():
            Draws an information box, including metadata and visually relevant elements, on the display.
    """
    def __init__(self, Display, Filepath, Filename, USER_HOME):
        """
        Initializes an instance of a class responsible for managing display properties, fonts, icons, file
        metadata, and UI components such as buttons. This class sets up the visual dimensions and components
        based on the provided display configuration and paths to resources.

        Attributes:
            display (pygame.Surface): The display onto which all elements are rendered.
            display_width (int): Width of the display in pixels.
            display_height (int): Height of the display in pixels.
            resolution (tuple[int, int]): Tuple containing the width and height of the display.
            displayType (str): The type of display based on resolution.
            filename (str): Name of the file to be processed or displayed.
            filepath (str): Path of the file to be processed or displayed.
            USER_HOME (str): Path to the user's home directory.
            FONT_DIR (str): Directory path where application fonts are stored.
            RESOURCES_DIR (str): Directory path where application resources are stored.
            filename_rect (pygame.Rect): Rectangle defining the position of the filename on the display.
            filename_surface (pygame.Surface): Surface to render the filename text.
            path_rect (pygame.Rect): Rectangle defining the position of the filepath on the display.
            path_surface (pygame.Surface): Surface to render the filepath text.
            font_filename (pygame.font.Font): Font used for rendering the filename text.
            font_filepath (pygame.font.Font): Font used for rendering the filepath text.
            font_button (pygame.font.Font): Font used for rendering button text.
            font_info (pygame.font.Font): Font used for rendering informational text.
            font_info_bold (pygame.font.Font): Bold font used for rendering informational text.
            check_icon (pygame.Surface): Scaled icon surface for a checkmark image.
            filepath_wrap_width (int): Maximum width for wrapping the filepath text.
            wrapped_filepath_lines (list[str]): Wrapped lines of text for the filepath.
            num_filepath_lines (int): Number of wrapped filepath lines.
            video_metadata (list[str]): Metadata retrieved from the given file.
            temp_hide (bool): Temporary state to hide certain elements or components.
            BOX_WIDTH_BASE (int): Base width for the dialog box.
            num_metadata_lines (int): Number of metadata lines to be displayed dynamically.
            BOX_HEIGHT_BASE (int): Base height for the dialog box.
            BOX_WIDTH (int): Final width for the dialog box, scaled based on resolution type.
            BOX_HEIGHT (int): Final height for the dialog box, scaled based on resolution type.
            BOX_X (int): X-coordinate for positioning the dialog box on the display.
            BOX_Y (int): Y-coordinate for positioning the dialog box on the display.
            is_hovered (bool): Boolean indicating whether a button is hovered upon.
            button_rect (pygame.Rect): Rectangle defining the position and size of a button.
        """
        self.display = Display
        self.display_width = self.display.get_width()
        self.display_height = self.display.get_height()
        self.resolution = self.display_width, self.display_height
        self.displayType = up_scale.get_display_type(self.resolution)

        # Get the filename and the filepath
        self.filename = Filename
        self.filepath = Filepath

        # Generate path to the application fonts
        self.USER_HOME = USER_HOME
        self.FONT_DIR = self.USER_HOME + "/.local/share/pyVid/fonts/"
        # Resources
        self.RESOURCES_DIR = self.USER_HOME + "/.local/share/pyVid/Resources/"

        # Rect and Surface for the Filename
        self.filename_rect = None
        self.filename_surface = None
        # Rect and surface for the Path
        self.path_rect = None
        self.path_surface = None

        original_font_sizes = [36, 24, 24, 26, 26]
        scaled_font_size = up_scale.get_scaled_fonts(original_font_sizes,self.display_height)
        # Load Fonts
        self.font_filename = pygame.font.Font(self.FONT_DIR + 'Arial_Black.ttf', scaled_font_size[0])       #36
        self.font_filepath = pygame.font.Font(self.FONT_DIR + 'Montserrat-Bold.ttf', scaled_font_size[1])   #24
        self.font_button = pygame.font.Font(self.FONT_DIR + 'Montserrat-Bold.ttf', scaled_font_size[2])     #24
        self.font_info = pygame.font.Font(self.FONT_DIR + 'Arial.ttf', scaled_font_size[3])                 #26
        self.font_info_bold = pygame.font.Font(self.FONT_DIR + 'Arial_Black.ttf', scaled_font_size[4])      #26
        # Load and scale checkmark icon
        self.check_icon = pygame.image.load(self.RESOURCES_DIR + 'checkmark.png').convert_alpha()
        self.check_icon = pygame.transform.scale(self.check_icon, (32, 32))

        # Calculate wrapped filepath lines
        self.filepath_wrap_width = 740  # Independent wrap width for filepath
        self.wrapped_filepath_lines = DrawVideoInfo.wrap_text(self.filepath, self.font_filepath, self.filepath_wrap_width)  # Apply new wrap width
        self.num_filepath_lines = len(self.wrapped_filepath_lines)

        # Get the metadata from self.filepath and parse it, stuff it into self.video_metadata
        self.video_metadata = DrawVideoInfo.get_metadata(self.filepath + self.filename)

        self.temp_hide = False

        self.BOX_WIDTH_BASE = 800
        self.num_metadata_lines = len(self.video_metadata) + self.num_filepath_lines
        if self.num_metadata_lines < 14:
            self.num_metadata_lines = 14

        # Determine box height dynamically
        self.BOX_HEIGHT_BASE = 250 + (self.num_metadata_lines * 24)  # Increased line spacing in height calculation

        width_multiplier, height_multiplier = up_scale.scale_resolution(self.displayType) \
            if self.displayType in up_scale.resolution_multipliers else (1, 1)
        # Dialog box positioning
        self.BOX_WIDTH  =  int(width_multiplier  * self.BOX_WIDTH_BASE)
        self.BOX_HEIGHT =  int(height_multiplier * self.BOX_HEIGHT_BASE)
        self.BOX_WIDTH -= 400

        self.BOX_X = (self.display_width - self.BOX_WIDTH) // 2
        self.BOX_Y = (self.display_height - self.BOX_HEIGHT) // 2

        button_x = self.BOX_X + self.BOX_WIDTH // 2 - 120
        button_y = self.BOX_Y + self.BOX_HEIGHT - 110

        self.is_hovered = False

        buttonWidthBase = 120
        buttonHeightBase = 40

        w_mult, h_mult = up_scale.resolution_multipliers[self.displayType]
        button_width = int(buttonWidthBase * w_mult)
        button_height = int(buttonHeightBase * h_mult)
        self.button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    @staticmethod
    def wrap_text(text, font, max_width):
        """
        Splits a given text into multiple lines that fit within a specified maximum width.

        This method ensures that the text is wrapped correctly such that each line does not exceed
        the maximum allowed width. Words are carefully added to lines, but if a single word exceeds
        the maximum width, it breaks mid-word to the next line. The computation of text width is
        handled using the provided font.

        Parameters:
        text : str
            The input text that needs to be wrapped across multiple lines.
        font
            The font object used to measure the width of the text for wrapping.
        max_width : int
            The maximum allowable width for each line.

        Returns:
        list
            A list of strings where each entry is a line of text respecting the maximum width.
        """
        words = text.split(" ")
        lines = []
        current_line = ""
        current_width = 0

        for word in words:
            word_width = font.size(word)[0]

            # If adding this word would exceed max_width, force new line first
            if current_width + word_width + font.size(" ")[0] > max_width:
                lines.append(current_line.strip())  # Commit current line before adding new word
                current_line = word
                current_width = word_width
            else:
                current_line += " " + word if current_line else word
                current_width += word_width + font.size(" ")[0]

            # **Strict Width Check:** Break mid-word if even a single character causes overflow
            while font.size(current_line)[0] > max_width:
                trimmed_word = current_line[:-1]  # Remove last character
                lines.append(trimmed_word.strip())  # Commit trimmed line
                current_line = current_line[len(trimmed_word):]  # Start new line
                current_width = font.size(current_line)[0]  # Reset tracking

        lines.append(current_line.strip())  # Commit last line
        return lines

    # Ellipsis function for filename truncation
    @staticmethod
    def truncate_text(text, font, max_width):
        """
        Truncates a given text to fit within a specified maximum width while adding an ellipsis if truncated.

        This method modifies the provided text string and ensures that its rendered width, when calculated
        using the given font, does not exceed the specified maximum width. If truncation occurs, an ellipsis
        ("...") is appended to the end of the resulting text.

        Parameters:
            text (str): The original text to be truncated.
            font: The font object used to calculate the text's rendered width.
            max_width (int): The maximum allowable width in pixels for the text.

        Returns:
            str: The truncated text with an ellipsis if the original text exceeded the maximum width.
        """
        if font.size(text)[0] <= max_width:
            return text

        truncated = text
        while font.size(truncated + "...")[0] > max_width and len(truncated) > 5:
            truncated = truncated[:-1]

        return truncated + "..."

    @staticmethod
    def truncate_path(path, max_length=60):
        """
        Truncates a given file path to ensure it fits within a maximum character limit. The truncation
        preserves the beginning and the end of the file path, replacing the middle part with ellipses
        if the path exceeds the specified maximum length.

        Args:
            path (str): The file path to be truncated.
            max_length (int): The maximum allowable length of the truncated path.

        Returns:
            str: The truncated file path that fits within the specified length.
        """
        if len(path) <= max_length:
            return path
        else:
            return path[:30] + "..." + path[-27:]

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
        scaled_font_size = up_scale.scale_font(18, self.display_height)
        tooltip_font = pygame.font.Font( self.FONT_DIR + "Montserrat-Bold.ttf", scaled_font_size)
        tooltip_surface = tooltip_font.render(text, True, WHITE)
        tooltip_width, tooltip_height = tooltip_surface.get_size()

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

        disp_surface.blit(tooltip_surface, (x + 5, y + 3))
       #pygame.display.flip()

    # Tooltip function
    def draw_path_tooltip(self, disp_surface, text, x, y):
        """
        Renders a tooltip with a given text at specified coordinates on a surface. The tooltip
        is displayed as a rectangle with a blue background and contains the provided text.
        This function is commonly used to show descriptive text or hints on a graphical
        display when the user hovers over specific elements.

        Parameters:
            disp_surface (pygame.Surface): The surface on which the tooltip will be drawn.
            text (str): The text to display inside the tooltip.
            x (int): The x-coordinate of the tooltip's top-left corner.
            y (int): The y-coordinate of the tooltip's top-left corner.
        """
        #print("draw_tooltip()")
        #print(f"draw_path_tooltip text: {text}")
        tooltip_path_font = pygame.font.Font( self.FONT_DIR + "Montserrat-Regular.ttf", 18)
        tooltip_path_surface = tooltip_path_font.render(text, True, WHITE)
        tooltip_path_width, tooltip_path_height = tooltip_path_surface.get_size()

        pygame.draw.rect(disp_surface, pygame.color.THECOLORS['dodgerblue'], (x, y, tooltip_path_width + 10, tooltip_path_height + 6), border_radius=5)
        disp_surface.blit(tooltip_path_surface, (x + 5, y + 3))

    def draw_info_box(self):
        """
        Renders an information box onto a Pygame surface, displaying a gradient background,
        video filename, metadata, and an interactive OK button.

        Arguments:
            None

        Raises:
            None
        """
        is_hovered = self.is_hovered
        y_offset = 0
        path_surface = None
        # Create a surface to apply the gradient
        gradient_surface = pygame.Surface((self.BOX_WIDTH, self.BOX_HEIGHT), pygame.SRCALPHA)
        gradient_surface.set_colorkey((0, 255, 0))
        DrawVideoInfo.apply_gradient(
                                     gradient_surface,
                                     #DODGERBLUE,
                                     #DODGERBLUE4,
                                     #(0, 145, 255),
                                     #(0, 50, 90),
                                    (0, 0, 255),
                                    (0, 0, 100),
                                     self.BOX_WIDTH,
                                     self.BOX_HEIGHT,
                                     alpha_start=80,
                                     alpha_end=180
                                     )

        # Blit the gradient to the display
        self.display.blit(gradient_surface, (self.BOX_X, self.BOX_Y))

        # Draw Border on top of the gradient
        pygame.draw.rect(self.display,
                         DODGERBLUE,
                        (self.BOX_X, self.BOX_Y, self.BOX_WIDTH, self.BOX_HEIGHT),
                         4,
                         border_radius=8
                        )

        # Render filename
        truncated_filename = DrawVideoInfo.truncate_text(self.filename, self.font_filename, self.BOX_WIDTH - 40)
        self.filename_surface = self.font_filename.render(truncated_filename, True, HEADING_COLOR)
        self.filename_rect = self.filename_surface.get_rect(center=(self.BOX_X + self.BOX_WIDTH // 2, self.BOX_Y + 80))
        self.display.blit(self.filename_surface, self.filename_rect.topleft)

        # Render Wrapped Filepath Below Filename
       # Render Metadata Below Filepath
        y_offset += self.BOX_Y + 200
        column_spacing =  500
        column_spacing2 = 200
        for key, value in self.video_metadata.items():
            key_surface = self.font_info.render(f"{key}:", True, WHITE)
            value_surface = self.font_info.render(str(value), True, WHITE)
            self.display.blit(key_surface, (self.BOX_X + column_spacing2 + 20, y_offset))
            self.display.blit(value_surface, (self.BOX_X + 20 + column_spacing2 + column_spacing, y_offset))
            y_offset += 60

        # Render OK Button
        button_color = DODGERBLUE if is_hovered else DODGERBLUE4
        pygame.draw.rect(self.display, button_color, self.button_rect, border_radius=8)
        pygame.draw.rect(self.display, BLACK, self.button_rect, 1, border_radius=8)
        self.display.blit(self.check_icon, (self.button_rect.x + 40, self.button_rect.y + 18))
        ok_surface = self.font_button.render("OK", True, HEADING_COLOR if is_hovered else WHITE)
        self.display.blit(ok_surface, (self.button_rect.x + 90, self.button_rect.y + 8))

    @staticmethod
    def __load_metadata(video_path):
        """
        Loads metadata of a given video file by executing an `ffprobe` command.
        The method runs `ffprobe` in a subprocess to extract details about the
        video's format and streams in JSON format.

        Parameters:
            video_path (str): Path to the video file that needs metadata extraction.

        Returns:
            dict: A dictionary containing metadata of the video file as parsed
            from the JSON output of `ffprobe`.
        """
        # ffprobe -v quiet -show_streams -show_format -print_format json video
        command = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", video_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        return json.loads(result.stdout)

    @staticmethod
    def get_metadata(video_path):
        """
        Retrieves and processes metadata for a given video file.

        This method extracts detailed metadata from the specified video file
        using FFprobe, including file size, duration, resolution, aspect ratio,
        format, bitrate, frames per second, and audio stream information. The
        collected metadata is formatted into a dictionary for further use. If
        there are issues with extracting or processing metadata, an empty
        dictionary will be returned.

        Args:
            video_path (str): Path to the video file for which metadata is to
                              be retrieved.

        Returns:
            dict: A dictionary containing metadata about the video. Keys may
                  include:
                  - "Size": File size in KB and MB.
                  - "Length": Video duration in formatted string.
                  - "Resolution": Video resolution (width x height).
                  - "Aspect Ratio": Aspect ratio of the video.
                  - "Format": Codec name of the video stream.
                  - "Bitrate": Video bitrate in kbps.
                  - "Frames Per Second": Frame rate of the video.
                  - "Audio Format": Codec name of the audio stream, if available.
                  - "Audio Bitrate": Audio bitrate in kbps, if available.
                  - "Sample Rate": Audio sample rate in Hz, if available.
                  - "Channels": Number of channels in the audio stream, if available.

        Raises:
            None: This method does not raise errors but returns an empty
                  dictionary and prints an error message if there is an issue
                  during the metadata extraction or processing.
        """
        try:
            # Extract video metadata using FFprobe
            command = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", video_path
            ]
            result = subprocess.run(command, capture_output=True, text=True)
            video_info = json.loads(result.stdout)
            # Extract basic details
            file_size = int(video_info["format"]["size"]) // 1024  # bytes to KB
            duration = float(video_info["format"]["duration"])
            video_bitrate = int(video_info["format"]["bit_rate"])
            # Find the video stream
            video_stream = next(s for s in video_info["streams"] if s["codec_type"] == "video")
            # Look for audio streams; if none exist, set defaults
            audio_streams = [s for s in video_info["streams"] if s["codec_type"] == "audio"]
            if audio_streams:
                audio_stream = audio_streams[0]  # Use the first available audio stream
                audio_format = audio_stream["codec_name"]
                audio_bitrate = audio_stream.get("bit_rate", "Unknown")
                audio_rate = audio_stream["sample_rate"]
                channels = audio_stream["channels"]
            else:
                audio_format = "None"
                audio_bitrate = "None"
                audio_rate = "None"
                channels = "None"
            # Calculate key properties
            resolution = f"{video_stream['width']} x {video_stream['height']}"
            aspect_ratio = round(video_stream["width"] / video_stream["height"], 5)
            video_format = video_stream["codec_name"]
            # Compute frames per second
            fps_parts = video_stream["r_frame_rate"].split("/")
            fps_num = float(fps_parts[0])
            fps_dem = float(fps_parts[1])
            fps = round(fps_num / fps_dem, 2) if fps_dem > 0 else fps_num
            # Format the metadata (note: DrawVideoInfo.format_seconds should be defined elsewhere)
            videoMetadata = {
                "Size": f"{file_size} KB ({file_size // 1024} MB)",
                "Length": f"{DrawVideoInfo.format_seconds(int(duration))}",
                "Resolution": resolution,
                "Aspect Ratio": aspect_ratio,
                "Format": video_format,
                "Bitrate": f"{video_bitrate / 1000} kbps",
                "Frames Per Second": fps,
                "Audio Format": audio_format,
                "Audio Bitrate": (f"{int(audio_bitrate) / 1000} kbps" if audio_bitrate != "None" else audio_bitrate),
                "Sample Rate": (f"{audio_rate} Hz" if audio_rate != "None" else audio_rate),
                "Channels": channels
            }
            return videoMetadata
        except Exception as e:
            # For quick-and-dirty error handling, print the error and return an empty dictionary.
            print(f"Error retrieving metadata for {video_path}: {e}")
            return {}

    @staticmethod
    def format_seconds(seconds):
        """
        Formats a given time in seconds into a string representation
        of hours, minutes, and seconds in the format HH:MM:SS.

        This utility method is useful for converting a duration in seconds into
        a readable time format.

        Args:
            seconds (int): The total number of seconds to format.

        Returns:
            str: A formatted string representing the time in HH:MM:SS format.
        """
        hours, remainder = divmod(seconds, 3600)  # Separate hours
        minutes, seconds = divmod(remainder, 60)  # Separate minutes and seconds

        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    @staticmethod
    def apply_gradient(surface, color_start, color_end, width, height, alpha_start=50, alpha_end=200):
        """
        Applies a vertical gradient to a given surface by transitioning the color and
        alpha values across the specified height range.

        This method creates a gradient effect by drawing horizontal lines for each
        y-coordinate, blending colors from the given starting color and alpha to the
        ending color and alpha.

        Parameters:
            surface (Surface): The surface where the gradient will be applied.
            color_start (tuple[int, int, int]): The starting RGB color as a tuple of three integers.
            color_end (tuple[int, int, int]): The ending RGB color as a tuple of three integers.
            width (int): The width of the gradient in pixels.
            height (int): The height of the gradient in pixels.
            alpha_start (int, optional): The starting alpha value, default value is 50.
            alpha_end (int, optional): The ending alpha value, default value is 200.

        Raises:
            ValueError: Raised if any of the provided RGB values are outside the valid
            range [0, 255].
        """
        for y in range(height):
            ratio = y / height
            new_color = (
                int(color_start[0] * (1 - ratio) + color_end[0] * ratio),  # Red
                int(color_start[1] * (1 - ratio) + color_end[1] * ratio),  # Green
                int(color_start[2] * (1 - ratio) + color_end[2] * ratio),  # Blue
                int(alpha_start * (1 - ratio) + alpha_end * ratio)  # Alpha blending
            )
            pygame.draw.line(surface, new_color, (0, y), (width, y))

