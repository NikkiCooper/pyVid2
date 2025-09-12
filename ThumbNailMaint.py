#   ThumbNailMaint.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Thumbnail maintence class

import os
import pygame
import subprocess
import cachetools
import upScale as up_scale

class ThumbNailMaint:
    """
    Manages the creation, caching, and retrieval of video thumbnails.

    This class handles thumbnail generation from video files, including scaling
    based on a specified display type. Thumbnails are cached for faster subsequent
    access. FFmpeg is used for thumbnail extraction, and the class supports GIF
    and standard video formats. Cached thumbnails are saved to a pre-configured
    directory on the filesystem.
    """
    def __init__(self,DisplayType,cacheDir):
        """
        Initializes a class instance for managing display type and cache directory.

        Attributes:
            displayType: The type of display being managed.
            CACHE_DIR: Directory path used for caching purposes.
            thumbnail_cache: Cache used to store thumbnail data with a limited
                size.

        Args:
            Display: Object that contains the display type information.
            cacheDir: Directory path for cache storage.
        """
        self.displayType = DisplayType
        self.CACHE_DIR = cacheDir
        self.thumbnail_cache = cachetools.LRUCache(maxsize=25)
        self.thumbnail_cache = {}

    def create_thumbnail(self, video_path):
        """
        Generates a thumbnail image from a video file.

        This function creates a thumbnail image for a given video file, supporting both
        GIF and standard video formats. It scales the thumbnail size based on the
        `displayType` attribute, either using predefined dimensions or default fallback
        dimensions. FFmpeg is used to extract the thumbnail, and the result is saved in
        the pre-configured cache directory.

        Attributes:
            CACHE_DIR: str
                The directory where the generated thumbnail will be stored.
            displayType: Any
                Used to determine the scaling factor for the thumbnail dimensions.

        Args:
            video_path: str
                The path to the video file from which the thumbnail will be generated.

        Returns:
            str
                The file path to the saved thumbnail image.

        Raises:
            ValueError: If the provided video path is invalid or display type configuration
                is incorrect.
            OSError: If there are issues creating the cache directory, running FFmpeg,
                or if the thumbnail file fails to be created.
            Exception: For any unexpected errors encountered during thumbnail generation.
        """
        try:
            if not video_path or not os.path.exists(video_path):
                raise ValueError(f"Invalid video path: {video_path}")

            thumbnail_path = os.path.join(self.CACHE_DIR, os.path.splitext(os.path.basename(video_path))[0] + ".jpg")

            try:
                # Scale up based on display resolution
                thumb_width, thumb_height = up_scale.scale_thumbnails(self.displayType) \
                    if self.displayType in up_scale.thumbnails else (256, 144)
                scale = f"scale={thumb_width}:{thumb_height}:flags=lanczos"

                # **Check if the file is a GIF**
                if video_path.lower().endswith(".gif"):
                    ffmpeg_cmd = [
                        "ffmpeg", "-hide_banner", "-loglevel", "error",
                        "-i", video_path, "-vf", scale, "-q:v", "2",
                        "-frames:v", "1", "-update", "1", thumbnail_path
                    ]
                else:
                    # **For standard video files**
                    ffmpeg_cmd = [
                        "ffmpeg", "-hide_banner", "-loglevel", "error",
                        "-i", video_path, "-ss", "00:00:05", "-vframes", "1",
                        "-vf", scale, "-q:v", "2", "-update", "1", thumbnail_path
                    ]

                # ** Ensure cache directory exists **
                os.makedirs(self.CACHE_DIR, exist_ok=True)

                # Run ffmpeg and check return code
                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    raise OSError(f"FFmpeg failed: {result.stderr}")

                # Verify thumbnail was created
                if not os.path.exists(thumbnail_path):
                    raise OSError("Thumbnail file was not created")

                return thumbnail_path

            except AttributeError as e:
                raise ValueError(f"Invalid display type configuration: {str(e)}")
            except subprocess.SubprocessError as e:
                raise OSError(f"Error running ffmpeg: {str(e)}")

        except (OSError, ValueError) as e:
            # Re-raise these exceptions as they already have appropriate messages
            raise
        except Exception as e:
            # Catch any other unexpected errors
            raise Exception(f"Unexpected error creating thumbnail: {str(e)}") from e

    def load_thumbnail(self, video_path):
        """
        Loads a video thumbnail, generating it if not available, and caches the result for faster access later.
        Handles scaling of thumbnails according to the display type provided during runtime.

        Parameters:
            video_path: str
                The path to the video file for which the thumbnail is to be retrieved or generated.

        Returns:
            pygame.Surface or None
                The thumbnail as a pygame surface object if successful, or None if the operation fails.
        """
        if video_path in self.thumbnail_cache:
            return self.thumbnail_cache[video_path]  # ✅ Return cached thumbnail immediately

        thumbnail_path = os.path.join(self.CACHE_DIR, os.path.splitext(os.path.basename(video_path))[0] + ".jpg")

        # **Generate thumbnail if missing**
        if not os.path.exists(thumbnail_path):
            thumbnail_path = self.create_thumbnail(video_path)
            if not os.path.exists(thumbnail_path):
                print(f"Failed to create thumbnail: {thumbnail_path}")
                return None

        try:
            # **Load the image**
            image_surface = pygame.image.load(thumbnail_path)
            thumb_width, thumb_height = up_scale.scale_thumbnails(self.displayType) \
                if self.displayType in  up_scale.thumbnails else (256, 144)
            image_surface = pygame.transform.scale(image_surface, (thumb_width, thumb_height))
        except pygame.error as e:
            print(f"Error loading thumbnail: {e}")
            return None
        # **Store in cache for faster access**
        self.thumbnail_cache[video_path] = image_surface
        return image_surface
