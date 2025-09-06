#  cmdLineOpts.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
import argparse
import os
#from matplotlib.rcsetup import validate_bool
from Bcolors import Bcolors

import cmdLineHelp as chl


bc = Bcolors()

def cmdLineOptions():
    """
    Parses command-line arguments for a video player CLI application.

    This function defines and handles all possible command-line options and arguments required to customize the behavior of
    a video player CLI, including video playback preferences, audio settings, system configurations, and file management
    options. These options allow users to control playback modes, select audio tracks, specify display settings, manage
    playlists, and much more.

    Returns
    -------
    argparse.Namespace
        Namespace object containing parsed command-line arguments as attributes, with their corresponding values.

    Raises
    ------
    SystemExit
        If parsing arguments fails or if required arguments are missing.

    Sections
    --------
    - **Video Playback Options**
      Includes arguments to loop videos, shuffle playback, disable GIFs, enable FFprobe, set video readers,
      interpolation methods, loop delays, playback speeds, title displays, and on-screen display counters.

    - **Audio Settings**
      Allows users to mute audio, select audio tracks, disable audio, and choose between Pygame or Pyaudio backends.

    - **System Settings**
      Includes verbose mode, specifying displays, status bar settings, and monitor listing functionalities.

    - **File Handling**
      Configures file and directory management, such as ignoring `.ignore` files, preventing recursion, printing video lists,
      or handling `.ignore` files.

    - **Mutually Exclusive Group**
      Enforces the requirement of providing either directories for media scanning, playlists for loading, or monitor listings
      before continuing.

    Notes
    -----
    Certain arguments, such as `--loop`, `--mute`, `--noAudio`, among others, are simple flags, whereas others like `--reader`,
    `--playSpeed`, and `--Paths` expect specific values or input types. The function uses default values for optional
    arguments and enforces validation for required or mutually exclusive arguments.

    Examples
    --------
    This section was intentionally excluded as per the requirements.
    """
    READER_MAPPING = {
        "auto":    0,
        "ffmpeg":  1,
        "opencv":  2,
        "imageio": 3,
        "decord":  4
    }

    parser = argparse.ArgumentParser(
        description=f"{bc.BOLD}{bc.Blue_f}PyV - Video Player CLI{bc.RESET}",
        formatter_class=argparse.RawTextHelpFormatter
        )

    # Requred Group
    required = parser.add_argument_group(chl.group["required_group"])
    # **Mutually exclusive group** ensures Paths is required unless --Files, --loadPlayList OR --listActiveMonitors is used
    group = required.add_mutually_exclusive_group(required=True)
    group.add_argument("--Paths", nargs="+", type=validate_user_dirs, default=None, help=chl.help["Paths"])
    group.add_argument("--Files", nargs="+", type=validate_user_files, default=None, help=chl.help["Files"])
    group.add_argument("--loadPlayList", type=validate_playList, help=chl.help["loadPlayList"])
    group.add_argument("--listActiveMonitors", nargs="?", const=True, help=chl.help["listActiveMonitors"])

    # 🎬 Video Playback Group
    video_group = parser.add_argument_group(chl.group["video_group"])
    video_group.add_argument("--loop", action="store_true", help=chl.help["loop"])
    video_group.add_argument("--shuffle", action="store_true", help=chl.help["shuffle"])
    video_group.add_argument("--disableGIF", action="store_true",help=chl.help["disableGIF"])
    video_group.add_argument("--enableFFprobe", action="store_true", help=chl.help["enableFFprobe"])
    video_group.add_argument("--reader", type=str, choices=list(READER_MAPPING.keys()), default="auto", help=chl.help["reader"])
    video_group.add_argument("--interp", type=str, choices=["area", "cubic", "linear", "nearest", "lanczos4"], default="cubic" ,help=chl.help["interp"])
    video_group.add_argument("--loopDelay" , type=int, default=1,  help=chl.help["loopDelay"])
    video_group.add_argument("--playSpeed", type=restricted_float_or_int, default=1.0, help=chl.help["playSpeed"] )
    video_group.add_argument("--dispTitles", type=str, choices=["all", "portrait", "landscape"], default=None, help=chl.help["dispTitles"])
    video_group.add_argument("--enableOSDcurpos", action="store_true", help=chl.help["enableOSDcurpos"])
    video_group.add_argument("--showFilename", action="store_true", help=chl.help["showFilename"])

    # Brightness & Contrast Group
    brightness_group = parser.add_argument_group(chl.group["brightness_group"])
    brightness_group.add_argument('--adjust-video', action='store_true', help=chl.help["adjust_video"])
    brightness_group.add_argument('--brightness', type=int, default=0,   help=chl.help["brightness"])
    brightness_group.add_argument('--contrast', type=int, default=0,    help=chl.help["contrast"])


    # 🔊 Audio Settings Group
    audio_group = parser.add_argument_group(chl.group["audio_group"])
    audio_group.add_argument("--mute", action="store_true", help=chl.help["mute"])
    audio_group.add_argument("--aTrack", type=int, default=0,help=chl.help["aTrack"])
    audio_group.add_argument("--usePygameAudio", action="store_true", help=chl.help["usePygameAudio"])

    # 🖥️ System & Display Settings
    system_group = parser.add_argument_group(chl.group["system_group"])
    system_group.add_argument("--verbose", action="store_true", help=chl.help["verbose"])
    system_group.add_argument("--display", type=str,  help=chl.help["display"])
    system_group.add_argument("--consoleStatusBar", action="store_true", help=chl.help["consoleStatusBar"])

    # 📂 File & Directory Management
    file_group = parser.add_argument_group(chl.group["file_group"])
    file_group.add_argument("--noIgnore", action="store_true", help=chl.help["noIgnore"])
    file_group.add_argument("--noRecurse", action="store_true", help=chl.help["noRecurse"])
    file_group.add_argument("--separateDirs", action="store_true", help=chl.help["separateDirs"])
    file_group.add_argument("--printVideoList", action="store_true", help=chl.help["printVideoList"])
    file_group.add_argument("--printIgnoreList", action="store_true", help=chl.help["printIgnoreList"])

    # Post-Processing Group
    pp_group =  parser.add_argument_group(chl.group["pp_group"])
    pp_group.add_argument("--laplacian", action="store_true", help=chl.help["sharpen"])
    pp_group.add_argument("--blur", action="store_true", help=chl.help["blur"])
    pp_group.add_argument("--median-blur", action="store_true", help=chl.help["median"])
    pp_group.add_argument("--gaussian-blur", action="store_true", help=chl.help["gaussian"])
    pp_group.add_argument("--noise", action="store_true", help=chl.help["noise"])
    pp_group.add_argument("--cel-shading", action="store_true", help=chl.help["cel_shading"])
    pp_group.add_argument("--comic", action="store_true", help=chl.help["comic"])
    #
    pp_group.add_argument('--thermal', action='store_true', help=chl.help["thermal"])
    pp_group.add_argument('--emboss', action='store_true', help=chl.help["emboss"])
    pp_group.add_argument('--dream', action='store_true', help=chl.help["dream"])
    pp_group.add_argument('--pixelate', action='store_true', help=chl.help["pixelate"])
    pp_group.add_argument('--neon', action='store_true', help=chl.help["neon"])
    pp_group.add_argument("--fliplr", action="store_true", help=chl.help["fliplr"])
    pp_group.add_argument("--flipup", action="store_true", help=chl.help["flipup"])

    # Watercolor Group
    watercolor_group =  parser.add_argument_group(chl.group["watercolor_group"])
    watercolor_group.add_argument('--watercolor', action='store_true', help=chl.help["watercolor"])
    watercolor_group.add_argument('--watercolor-scale', type=float, default=0.5, help=chl.help["watercolor_scale"])
    watercolor_group.add_argument('--watercolor-quality', type=str, default='medium', choices=['fast', 'medium', 'high'], help=chl.help["watercolor_quality"])

    # Oil Painting Group
    oil_painting_group =  parser.add_argument_group(chl.group["oil_painting_group"])
    oil_painting_group.add_argument('--oil-painting', action='store_true', help=chl.help["oil_painting"])
    oil_painting_group.add_argument('--oil-size', type=int, default=7, help=chl.help["oil_size"])
    oil_painting_group.add_argument('--oil-dynamics', type=int, default=1, help=chl.help["oil_dynamics"])

    # Pencil Sketch Group
    pencil_group =  parser.add_argument_group(chl.group["pencil_group"])
    pencil_group.add_argument('--pencil-sketch', action='store_true', help=chl.help["pencil_sketch"])
    pencil_group.add_argument('--sketch-detail', type=int, default=21, help=chl.help["sketch_detail"])
    pencil_group.add_argument('--sketch-block-size', type=int, default=9, help=chl.help["sketch_block_size"])
    pencil_group.add_argument('--sketch-c-value', type=int, default=2,  help=chl.help["sketch_c_value"])
    pencil_group.add_argument('--sketch-intensity', type=float, default=0.7, help=chl.help["sketch_intensity"])
    pencil_group.add_argument('--edge-weight', type=float, default=0.3,  help=chl.help["sketch_edge_weight"])

    # Create a group for color-related settings
    color_settings = parser.add_argument_group(chl.group["color_settings_group"])
    # Create a mutually exclusive group for base color effects (greyscale, sepia)
    base_color_group = color_settings.add_mutually_exclusive_group()
    base_color_group.add_argument('--greyscale', action='store_true', help=chl.help['greyscale'])
    base_color_group.add_argument('--sepia', action='store_true', help=chl.help['sepia'])
    # Create a mutually exclusive group for color modifications
    color_mod_group = color_settings.add_mutually_exclusive_group()
    color_mod_group.add_argument('--vignette', action='store_true', help=chl.help['vignette'])
    color_mod_group.add_argument('--saturation', type=float,  help=chl.help['saturation'])

    # Edge Detection Group
    edge_group = parser.add_argument_group(chl.group["edge_group"])
    edge_group.add_argument('--edge-detect', action='store_true', help=chl.help["edge_detect"])
    edge_group.add_argument('--edge-lower', type=int, default=100, help=chl.help["edge_lower"])
    edge_group.add_argument('--edge-upper', type=int, default=200, help=chl.help["edge_upper"])

    # Comic-Sharp effect parameters
    comic_group = parser.add_argument_group(chl.group["comic_group"])
    comic_group.add_argument('--comic-sharp', action='store_true', help=chl.help["comic_sharp"])
    comic_group.add_argument('--comic-sharp-amount', type=float, default=0.5, help=chl.help["comic_sharp_amount"])
    comic_group.add_argument('--bilateral-d', type=int, choices=[1,3,5,7,9,11,13,15], default=5, help=chl.help["bilateral_d"])
    comic_group.add_argument('--bilateral-color', type=int, default=60, help=chl.help["bilateral_color"])
    comic_group.add_argument('--bilateral-space', type=int, default=60, help=chl.help["bilateral_space"])
    comic_group.add_argument('--edge-low', type=int, default=40, help=chl.help["edge_low"])
    comic_group.add_argument('--edge-high', type=int, default=140, help=chl.help["edge_high"])
    comic_group.add_argument('--color-quant', type=int, default=20, help=chl.help["color_quant"])


    args = parser.parse_args()

    # Convert string input to a corresponding integer value for --reader argument
    args.reader_val_int = int(READER_MAPPING.get(args.reader, READER_MAPPING["auto"]))  # Default to "Auto" if unset
    #args.loadPlayListFlag = False
    args.key_mute_flag = False
    args.loop_flag = False
    args.actualDuration = 0
    # Add some needed flags for other filters that are not here
    args.apply_denoising = False
    args.apply_contrast_enhancement = False
    args.apply_sharpening = False
    #

    # Sepia arguments
    #sepia presets 'classic', 'warm', 'cool', 'vintage'
    args.SepiaPresetList = ['classic', 'warm','cool','vintage']
    args.sepia_preset = args.SepiaPresetList[2]
    #intensity from 0.0 to 1.0
    args.sepia_intensity = 1.0
    args.apply_sepia = False

    # laplacian Boost
    # args.sharpen = the actuall cli argument
    args.apply_laplacian = False
    # 1 to 5
    args.laplacian_kernel_size = 1
    # 1 to 10 (divide by ten, its really 0.1 to 1.0)
    args.laplacian_boost_strength = 9.5

    args.apply_artistic_filters = False
    args.apply_oil_painting = False

    args.apply_edges_sobel = False
    args.apply_edge_detect = False
    args.apply_inverted = False

    args.apply_adjust_video = False

    # args.last_preset is the last bilateral filter preset used that wasnt 'OFF'
    args.last_bilateral_preset = None
    args.apply_bilateral_filter = False
    args.CUDA_bilateral_filter = False
    args.show_bilateral_filter = False

    # saturation
    args.apply_saturation = False
    args.saturation_factor = 1.0
    #
    # use with --playSpeed
    args.playSpeed_last = 0
    args.playSpeed_last_set = False
    # --loadPlayList
    if args.loadPlayList is None:
        args.loadPlayListFlag = False
    else:
        args.loadPlayListFlag = True

    # --Files
    if args.Files is None:
        args.loadFilesFlag = False
    else:
        args.loadFilesFlag = True

    # --oil-painting
    oil_painting_params = ['oil_size', 'oil_dynamics']
    if not args.oil_painting and any(getattr(args,param, None) != parser.get_default(param) for param in oil_painting_params):
        parser.error("The parameters --oil-size and --oil-dynamics require --oil-painting to be set")

    # --watercolor
    watercolor_params = ['watercolor_scale', 'watercolor_quality']
    if not args.watercolor and any(getattr(args, param, None) != parser.get_default(param) for param in watercolor_params):
        parser.error("The parameters --watercolor-scale and --watercolor-quality require --watercolor to be set")

    # --pencil-sketch
    pencil_params = ['sketch_detail', 'sketch_block_size', 'sketch_c_value', 'sketch_intensity', 'edge_weight']
    if not args.pencil_sketch and any(getattr(args, param, None) != parser.get_default(param)
                                      for param in pencil_params):
        parser.error("The parameters --sketch-detail, --sketch-block-size, --sketch-c-value, "
                     "--sketch-intensity, and --edge-weight require --pencil-sketch to be set")

    # --edge-detect
    if (args.edge_lower != 100 or args.edge_upper != 200) and not args.edge_detect:
        parser.error('--edge-lower and --edge-upper require --edge-detect')
    if args.edge_detect:
        if args.edge_lower >= args.edge_upper:
            parser.error('--edge-lower must be less than --edge-upper')
        if args.edge_lower < 0 or args.edge_upper > 255:
            parser.error('Edge detection thresholds must be between 0 and 255')


    # Additional validation to ensure no combination of base effects with color modifications
    if (args.greyscale or args.sepia) and (args.saturation is not None or args.vignette):
        parser.error('Cannot combine greyscale/sepia with saturation or vignette effects')

    if args.saturation is not None and (args.saturation < 0.0 or args.saturation > 2.0):
        parser.error('Saturation must be between 0.0 and 2.0')

    # --comic-sharp
    comic_sharp_params = ['bilateral_d', 'bilateral_color', 'bilateral_space', 'edge_low', 'edge_high', 'color_quant','comic_sharp_amount']
    if not args.comic_sharp and any(getattr(args,param,None) != parser.get_default(param) for param in comic_sharp_params):
        parser.error("The parameters --bilateral-d, --bilateral-color, --bilateral-space, --edge-low, --edge-high, --color-quant, and --comic-sharp-amount require --comic-sharp to be set")

    if args.bilateral_color < 10 or args.bilateral_color > 200:
        parser.error('bilateral-color must be between 10 and 200')
    if args.bilateral_space < 10 or args.bilateral_space > 200:
        parser.error('bilateral-space must be between 10 and 200')
    if args.edge_low < 0 or args.edge_low > 255:
        parser.error('edge-low must be between 0 and 255')
    if args.edge_high < 0 or args.edge_high > 255:
        parser.error('edge-high must be between 0 and 255')
    if args.edge_low >= args.edge_high:
        parser.error('edge-low must be less than edge-high')
    if args.color_quant < 1 or args.color_quant > 64:
        parser.error('color-quant must be between 1 and 64')
    if args.comic_sharp_amount < 0.1 or args.comic_sharp_amount > 1.0:
        parser.error('comic-sharp-amount must be between 0.1 and 1.0')

    return args

# Validate that the user-supplied path/playlist exists.
def validate_playList(playlist):
    if not os.path.isfile(os.path.expanduser(playlist)):
        raise argparse.ArgumentTypeError(f"Error: {bc.Red_f}'{playlist}'{bc.Light_Yellow_f} was not found.{bc.RESET}")
    return playlist

# Validate user supplied media directories
def validate_user_dirs(path):
    """Checks if a given path is a valid directory."""
    if path is None:
        raise argparse.ArgumentTypeError(f"Error: {bc.Light_Yellow_f}At least one valid directory must be supplied.{bc.RESET}")
    if not os.path.isdir(os.path.expanduser(path)):
        raise argparse.ArgumentTypeError(f"Error: {bc.Red_f}'{path}'{bc.Light_Yellow_f} is not a valid directory.{bc.RESET}")

    return os.path.expanduser(path)

# Validate user supplied media files
def validate_user_files(FilePath):
    """Checks if a given path is a valid file."""
    if FilePath is None:
        raise argparse.ArgumentTypeError(f"Error: {bc.Light_Yellow_f}At least one valid file must be supplied.{bc.RESET}")

    expanded_path = os.path.expanduser(FilePath)
    if not os.path.isfile(expanded_path):
        raise argparse.ArgumentTypeError(f"Error: {bc.Red_f}'{FilePath}'{bc.Light_Yellow_f} is not a valid file.{bc.RESET}")

    return expanded_path

# --playSpeed
# Create an argument parser
def restricted_float_or_int(x):
    try:
        x = float(x)  # Convert input to float first
    except ValueError:
        raise argparse.ArgumentTypeError(f"{bc.Red_f}{x}{bc.Light_Yellow_f} is not a valid number{bc.RESET}")

    # Ensure the value is either a whole number or a float within range
    if x < 0.5 or x > 5.0:
        raise argparse.ArgumentTypeError(f"{bc.Light_Yellow_f}Value must be between{bc.Green_f} 0.5{bc.Light_Yellow_f} and{bc.Green_f} 5.0{bc.Light_Yellow_f}, but got{bc.Red_f} {x}{bc.RESET}")

    if x.is_integer():  # Convert integer-like floats to ints (e.g., 2.0 → 2)
        return int(x)

    return x  # Return as float if it's a decimal
