#  upScale.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
#  Constants used to scale pygame windows to various sized displays

# Base resolution (WUXGA)
BASE_WIDTH, BASE_HEIGHT = 1920, 1200

# Target resolutions
resolutions = {
	"WUXGA":   (1920, 1200),
	"FHD":     (1920, 1080),
    "QHD":     (2560, 1440),
    "WQXGA":   (3200, 1600),
    "4K_UHD":  (3840, 2160)
}

thumbnails = {
    "WUXGA":    (256, 144),     # 1920x1200
    "FHD":      (256, 144),     # 1920x1080
    "QHD":      (341, 192),     # 2560x1440
    "WQXGA":    (341, 192),     # 2560x1600
    "4K_UHD":   (512, 288)      # 3840x2160
}

# Target multipliers
resolution_multipliers = {
    "WUXGA": (1.00, 1.00),
    "QHD": (1.33, 1.20),
    "WQXGA": (1.67, 1.33),
    "4K_UHD": (2.00, 1.80)
}

# Get the display type, i.e. 4K_UHD
def get_display_type(resolution):
    """
    Determines the display type based on the provided resolution.

    The function takes a resolution as input and searches for a matching
    resolution in a predefined dictionary of resolutions. If a match is
    found, the corresponding display type is returned. If no match is
    found, the function returns None.

    Parameters:
        resolution (tuple): The resolution for which the display type needs
            to be determined.

    Returns:
        str: The display type corresponding to the provided resolution, if
            found.
        None: If the resolution does not match any known display type.
    """
    for display_type, res in resolutions.items():
        if res == resolution:
            return display_type
    return None

def scale_resolution(display_type):
    """
    Scales the resolution multipliers based on the display type.

    This function retrieves the width and height multipliers associated 
    with the provided display type from the 'resolution_multipliers' 
    dictionary. It then returns these multipliers as a tuple.

    Parameters:
    display_type : str
        The type of display for which the resolution multipliers 
        are to be scaled. Should correspond to a key in the 
        'resolution_multipliers' dictionary.

    Returns:
    tuple
        A tuple containing the width multiplier (float) and the height 
        multiplier (float) for the given display type.
    """
    width_multiplier, height_multiplier = resolution_multipliers[display_type]
    return width_multiplier, height_multiplier

def scale_thumbnails(display_type):
    """
    Retrieves the resolution for a given display type or provides a default resolution
    if the display type is not found.

    Parameters:
        display_type (Any): The key for the desired display type resolution.

    Returns:
        Tuple[int, int]: The resolution dimensions (width, height) for the given
        display type or default resolution (256, 144).
    """
    return thumbnails.get(display_type, (256, 144)) # default to WUXGA

def get_scaling_factor(target_display_height):
    """
    Calculates the scaling factor based on the target display height.

    This function determines a scaling factor by comparing a given target display
    height to a predefined base height. It is useful for scaling elements
    proportionally to fit a target display size.

    Args:
        target_display_height (float): The target height of the display.

    Returns:
        float: The scaling factor derived from the target height and base height.
    """
    return target_display_height / BASE_HEIGHT

def scale_font(original_font_size, target_display_height):
    """
    Scales the given font size based on the target display height, ensuring the 
    calculated font size does not drop below 1 pixel.

    Parameters:
    original_font_size : int
        The original font size to be scaled.
    target_display_height : int
        The height of the target display to calculate the scaling factor.

    Returns:
    int
        The scaled font size, adjusted based on the target display height, 
        with a minimum size of 1 pixel.
    """
    scaling_factor = get_scaling_factor(target_display_height)
    return max(1, int(original_font_size * scaling_factor))  # Ensure font size doesn’t drop below 1px

def get_scaled_fonts(original_font_sizes, target_display_height):
    """
    Calculates scaled font sizes based on a scaling factor determined by the target 
    display height. The function applies the scaling factor to a list of original font 
    sizes and returns a new list of scaled font sizes.

    Arguments:
        original_font_sizes: list of int
            A list representing the original font sizes to be scaled.
        target_display_height: int
            The height of the target display for which the scaling factor is determined.

    Returns:
        list of int
            A list containing the scaled font sizes, calculated by applying the scaling 
            factor to the input font sizes.
    """
    scaling_factor = get_scaling_factor(target_display_height)
    return [int(size * scaling_factor) for size in original_font_sizes]



