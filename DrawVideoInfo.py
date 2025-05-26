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

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DODGERBLUE = (30, 144, 255)
DODGERBLUE4 = (16, 78, 139)

class DrawVideoInfo:
    def __init__(self, Display, Filepath, Filename, USER_HOME):
        self.display = Display
        self.display_width = self.display.get_width()
        self.display_height = self.display.get_height()
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

        # Load Fonts
        self.font_filename = pygame.font.Font(self.FONT_DIR + 'Montserrat-Bold.ttf', 32)
        self.font_info = pygame.font.Font(self.FONT_DIR + 'Montserrat-Regular.ttf', 26)  # Increased text spacing slightly
        self.font_filepath = pygame.font.Font(self.FONT_DIR + 'Montserrat-Regular.ttf', 22)
        self.font_button = pygame.font.Font(self.FONT_DIR + 'Montserrat-Bold.ttf', 24)
        # Load and scale checkmark icon
        self.check_icon = pygame.image.load(self.RESOURCES_DIR + 'checkmark.png').convert_alpha()
        self.check_icon = pygame.transform.scale(self.check_icon, (32, 32))

        # Calculate wrapped filepath lines
        self.filepath_wrap_width = 740  # Independent wrap width for filepath
        self.wrapped_filepath_lines = DrawVideoInfo.wrap_text(self.filepath, self.font_filepath, self.filepath_wrap_width)  # Apply new wrap width
        self.num_filepath_lines = len(self.wrapped_filepath_lines)

        # Get the metadata from self.filepath and parse it, stuff it into self.video_metadata
        self.video_metadata = DrawVideoInfo.get_metadata(self.filepath + self.filename)

        # Determine box height dynamically
        self.num_metadata_lines = len(self.video_metadata) + self.num_filepath_lines
        self.BOX_HEIGHT = 280 + (self.num_metadata_lines * 24)  # Increased line spacing in height calculation

        # Dialog box positioning
        self.BOX_WIDTH = 800
        self.BOX_X = (self.display_width - self.BOX_WIDTH) // 2
        self.BOX_Y = (self.display_height - self.BOX_HEIGHT) // 2

        # Button properties
        self.button_rect = pygame.Rect(self.BOX_X + self.BOX_WIDTH // 2 - 60, self.BOX_Y + self.BOX_HEIGHT - 60, 120, 40)  # Moved up slightly

    @staticmethod
    def wrap_text(text, font, max_width):
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
        if font.size(text)[0] <= max_width:
            return text

        truncated = text
        while font.size(truncated + "...")[0] > max_width and len(truncated) > 5:
            truncated = truncated[:-1]

        return truncated + "..."

    @staticmethod
    def truncate_path(path, max_length=60):
        if len(path) <= max_length:
            return path
        else:
            return path[:30] + "..." + path[-27:]

    # Tooltip function
    def draw_tooltip(self, disp_surface, text, x, y):
        #print("draw_tooltip()")
        tooltip_font = pygame.font.Font( self.FONT_DIR + "Montserrat-Regular.ttf", 18)
        tooltip_surface = tooltip_font.render(text, True, BLACK)
        tooltip_width, tooltip_height = tooltip_surface.get_size()

        pygame.draw.rect(disp_surface, pygame.color.THECOLORS['green'], (x, y, tooltip_width + 10, tooltip_height + 6), border_radius=5)
        disp_surface.blit(tooltip_surface, (x + 5, y + 3))
       #pygame.display.flip()

    # Tooltip function
    def draw_path_tooltip(self, disp_surface, text, x, y):
        #print("draw_tooltip()")
        #print(f"draw_path_tooltip text: {text}")
        tooltip_path_font = pygame.font.Font( self.FONT_DIR + "Montserrat-Regular.ttf", 18)
        tooltip_path_surface = tooltip_path_font.render(text, True, BLACK)
        tooltip_path_width, tooltip_path_height = tooltip_path_surface.get_size()

        pygame.draw.rect(disp_surface, pygame.color.THECOLORS['green'], (x, y, tooltip_path_width + 10, tooltip_path_height + 6), border_radius=5)
        disp_surface.blit(tooltip_path_surface, (x + 5, y + 3))



    def draw_info_box(self):
        y_offset = 0
        path_surface = None
        # Draw Dialog Box
        pygame.draw.rect(self.display, DODGERBLUE, (self.BOX_X, self.BOX_Y, self.BOX_WIDTH, self.BOX_HEIGHT), border_radius=10)
        pygame.draw.rect(self.display, DODGERBLUE4, (self.BOX_X, self.BOX_Y, self.BOX_WIDTH, self.BOX_HEIGHT), 2, border_radius=10)

        # Truncate and render filename (with tooltip support)
        truncated_filename = DrawVideoInfo.truncate_text(self.filename, self.font_filename, self.BOX_WIDTH - 40)
        self.filename_surface = self.font_filename.render(truncated_filename, True, BLACK)
        self.filename_rect = self.filename_surface.get_rect(center=(self.BOX_X + self.BOX_WIDTH//2, self.BOX_Y + 20))
        self.display.blit(self.filename_surface, self.filename_rect.topleft)
        # Render Wrapped Filepath Below Filename
        y_offset = self.BOX_Y + 50   # The Y coordinate of filepath

        '''
        for line in self.wrapped_filepath_lines:
            path_surface = self.font_filepath.render(line, True, BLACK)  # Now using independent font for filepath
            self.display.blit(path_surface, (self.BOX_X + 20, y_offset))
            y_offset += 24  # Increased spacing slightly
        '''
        truncated_path = DrawVideoInfo.truncate_path(self.filepath, max_length=60)
        path_surface = self.font_filepath.render(truncated_path, True, BLACK)
        self.path_rect = pygame.Rect(self.BOX_X + 20,
                                     y_offset,
                                     path_surface.get_width(),
                                     path_surface.get_height()
                                     )
        self.display.blit(
                          path_surface,
                          (self.BOX_X + 20, y_offset)
                          )
        #y_offset += 24

        # Render Metadata Below Filepath
        #y_offset += 20
        y_offset += 44  # instead of separate 24 + 20 updates.
        column_spacing = 350  # spacing between the descriptors and their data

        for key, value in self.video_metadata.items():
            key_surface = self.font_info.render(f"{key}:", True, BLACK)
            value_surface = self.font_info.render(value, True, BLACK)
            self.display.blit(key_surface, (self.BOX_X + 20, y_offset))
            self.display.blit(value_surface, (self.BOX_X + 20 + column_spacing, y_offset))
            y_offset += 30  # Increased spacing slightly

        # Render OK Button with proper spacing
        pygame.draw.rect(self.display, DODGERBLUE4, self.button_rect, border_radius=8)
        self.display.blit(self.check_icon, (self.button_rect.x + 10, self.button_rect.y + 4))
        ok_surface = self.font_button.render("OK", True, WHITE)
        self.display.blit(ok_surface, (self.button_rect.x + 50, self.button_rect.y + 5))

    @staticmethod
    def __load_metadata(video_path):
        """Extract video metadata using FFprobe"""
        # ffprobe -v quiet -show_streams -show_format -print_format json video
        command = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", video_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        return json.loads(result.stdout)

    @staticmethod
    def get_metadata(video_path):

        print(f"video_path: {video_path}")
        # extract video medatata using FFprobe
        command = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", video_path
        ]

        result = subprocess.run(command, capture_output=True, text=True)
        video_info = json.loads(result.stdout)

        # Extract details
        file_size = int(video_info["format"]["size"]) // 1024  # Convert bytes to KB
        duration = float(video_info["format"]["duration"])
        video_bitrate = int(video_info["format"]["bit_rate"])

        video_stream = next(s for s in video_info["streams"] if s["codec_type"] == "video")
        #audio_stream = next(s for s in video_info["streams"] if s["codec_type"] == "audio")
        audio_streams = [s for s in video_info["streams"] if s["codec_type"] == "audio"]
        if audio_streams:
            audio_stream = audio_streams[0]  # Safely retrieve the first audio stream
            audio_format = audio_stream["codec_name"]
            audio_bitrate = audio_stream.get("bit_rate", "Unknown")
            audio_rate = audio_stream["sample_rate"]
            channels = audio_stream["channels"]
        else:
            audio_format = "None"
            audio_bitrate = "None"
            audio_rate = "None"
            channels = "None"

        # Extract key properties
        resolution = f"{video_stream['width']} x {video_stream['height']}"
        aspect_ratio = round(video_stream["width"] / video_stream["height"], 5)
        video_format = video_stream["codec_name"]
        #fps = video_stream["r_frame_rate"].split("/")[0]
        #fps = float(video_stream["r_frame_rate"])
        fps_num = float(video_stream["r_frame_rate"].split("/")[0])
        fps_dem = float(video_stream["r_frame_rate"].split("/")[1])
        if fps_dem > 0:
            fps = round(float(fps_num / fps_dem), 2)
        else:
            fps = fps_num
        print(f"fps_num: {fps_num}, fps_dem {fps_dem}")

        # Print results
        print(f"Size: {file_size} KB, ({file_size // 1024} MB)")
        print(f"Length: {DrawVideoInfo.format_seconds(int(duration))}")
        print(f"Resolution: {resolution}")
        print(f"Aspect Ratio: {aspect_ratio}")
        print(f"Format: {video_format}")
        print(f"Bitrate: {video_bitrate / 1000} kbps")
        print(f"FPS: {fps}")
        print(f"Audio Format: {audio_format}")
        if audio_bitrate != "None":
            print(f"Audio Bitrate: {int(audio_bitrate)/1000} kbps")
        else:
            print(f"Audio Bitrate: {audio_bitrate}")
        if audio_rate != "None":
            print(f"Sample Rate: {audio_rate} Hz")
        else:
            print(f"Sample Rate: {audio_rate}")
        print(f"Channels: {channels}")
        print()

        videoMetadata = {
            "Size": f"{file_size} KB ({file_size // 1024} MB)",
            "Length": f"{DrawVideoInfo.format_seconds(int(duration))}",
            "Resolution": f"{resolution}",
            "Aspect Ratio": f"{aspect_ratio}",
            "Format": f"{video_format}",
            "Bitrate": f"{video_bitrate / 1000} kbps",
            "Frames Per Second": f"{fps}",
            "Audio Format": f"{audio_format}",
            "Audio Bitrate": (f"{int(audio_bitrate) / 1000} kbps" if audio_bitrate != "None" else f"{audio_bitrate}"),
            "Sample Rate":  (f"{audio_rate} Hz" if audio_rate != "None" else f"{audio_rate}"),
            "Channels": f"{channels}"
        }
        return videoMetadata

    @staticmethod
    def format_seconds(seconds):
        """
        Helper method to format seconds to HH:MM:SS format.
        :param seconds: Total duration in seconds
        :type seconds: int
        :return: Formatted duration string (HH:MM:SS)
        :rtype: str
        """
        hours, remainder = divmod(seconds, 3600)  # Separate hours
        minutes, seconds = divmod(remainder, 60)  # Separate minutes and seconds

        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

