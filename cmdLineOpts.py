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

bc = Bcolors()

def cmdLineOptions():

    READER_MAPPING = {
        "auto":    0,
        "ffmpeg":  1,
        "opencv":  2,
        "imageio": 3,
        "dcord":   4
    }

    parser = argparse.ArgumentParser(
        description=f"{bc.BOLD}{bc.Blue_f}PyV - Video Player CLI{bc.RESET}",
        formatter_class=argparse.RawTextHelpFormatter
        )

    # 🎬 Video Playback Group
    video_group = parser.add_argument_group(f"{bc.BOLD}{bc.Blue_f}Video Playback Options{bc.RESET}")
    video_group.add_argument("--loop", action="store_true", help=f"{bc.Light_Yellow_f}Loop videos instead of exiting\n{bc.Magenta_f}Default: Don't loop{bc.RESET}")
    video_group.add_argument("--shuffle", action="store_true", help=f"{bc.Light_Yellow_f}Play videos in random order\n{bc.Magenta_f}Default: Don't shuffle{bc.RESET}")
    video_group.add_argument("--disableGIF", action="store_true",help=f"{bc.Light_Yellow_f}Disable playing .GIF files\n{bc.Magenta_f}Default: Play .GIFs{bc.RESET}")
    #video_group.add_argument("--scale", action="store_true", help=f"{bc.Light_Yellow_f}Scale the videos width while maintaining aspect ratio\n{bc.Magenta_f}Default: Don't scale{bc.RESET}")
    video_group.add_argument("--enableFFprobe", action="store_true", help=f"{bc.Light_Yellow_f}Enable FFprobe when using openCV\n{bc.Magenta_f}Default: Disabled{bc.RESET}")
    video_group.add_argument("--reader", type=str, choices=list(READER_MAPPING.keys()), default="auto", help=f"{bc.Light_Yellow_f}Specifies which video reading backend to use\n{bc.Magenta_f}Default: auto{bc.RESET}")
    video_group.add_argument("--interp", type=str, choices=["area", "cubic", "linear", "nearest", "lanczos4"], default="cubic" ,help=f"{bc.Light_Yellow_f}Use interpolation method for resizing frames\n{bc.Magenta_f}Default: Cubic (recommended){bc.RESET}")
    video_group.add_argument("--loopDelay" , type=int, default=1,  help=f"{bc.Light_Yellow_f}The delay in seconds between each video\n{bc.Magenta_f}Default: 1 sec (recommended){bc.RESET}")
    video_group.add_argument("--playSpeed", type=restricted_float_or_int, default=1.0, help=f"{bc.Light_Yellow_f}Set playback speed (0.5 - 5.0)\n{bc.Magenta_f}Default: 1.0{bc.RESET}")
    video_group.add_argument("--enableOSDcurpos", action="store_true", help=f"{bc.Light_Yellow_f}Enable OSD current position counter on startup.\n{bc.Magenta_f}Default: False{bc.RESET}")

    # 🔊 Audio Settings Group
    audio_group = parser.add_argument_group(f"{bc.BOLD}{bc.Blue_f}Audio Settings{bc.RESET}")
    audio_group.add_argument("--mute", action="store_true", help=f"{bc.Light_Yellow_f}Mute all audio globally\n{bc.Magenta_f}Default: Don't mute{bc.RESET}")
    audio_group.add_argument("--aTrack", type=int, default=0,help=f"{bc.Light_Yellow_f}Selects which audio track to use.\n{bc.Magenta_f}Default: 0{bc.RESET}")
    audio_group.add_argument("--noAudio", action="store_true", help=f"{bc.Light_Yellow_f}Specify if videos have audio tracks\n{bc.Magenta_f}Default: Assume videos _might_ have audio tracks{bc.RESET}")
    audio_group.add_argument("--usePygameAudio", action="store_true", help=f"{bc.Light_Yellow_f}Use Pygame or Pyaudio\n{bc.Magenta_f}Default: Pyaudio (False){bc.RESET}")

    # 🖥️ System & Display Settings
    system_group = parser.add_argument_group(f"{bc.BOLD}{bc.Blue_f}System Settings{bc.RESET}")
    system_group.add_argument("--verbose", action="store_true", help=f"{bc.Light_Yellow_f}Be verbose on errors and execeptions\n{bc.Magenta_f}Default: False{bc.RESET}")
    system_group.add_argument("--display", type=str, help=f"{bc.Light_Yellow_f}Enable output on a specific display\n{bc.Magenta_f}Default: The currenty active display{bc.RESET}")
    #system_group.add_argument("--listActiveMonitors", type=str, help=f"{bc.Light_Yellow_f}Lists active monitors detected on your computer.  Use as a helper func to --display.{bc.RESET}")
    system_group.add_argument("--consoleStatusBar", action="store_true", help=f"{bc.Light_Yellow_f}Enables a debug status bar in the console\n{bc.Magenta_f}Default: Disable console status bar{bc.RESET}")

    # 📂 File & Directory Management
    file_group = parser.add_argument_group(f"{bc.BOLD}{bc.Blue_f}File Handling{bc.RESET}")
    file_group.add_argument("--noIgnore", action="store_true", help=f"{bc.Light_Yellow_f}Do not honor .ignore files\n{bc.Magenta_f}Default: Honor .ignore files{bc.RESET}")
    file_group.add_argument("--noRecurse", action="store_true", help=f"{bc.Light_Yellow_f}Do not recurse into the specified directories\n{bc.Magenta_f}Default: Recurse into all specified directories{bc.RESET}")
    file_group.add_argument("--printVideoList", action="store_true", help=f"{bc.Light_Yellow_f}Print a list of available videos{bc.RESET}")
    file_group.add_argument("--printIgnoreList", action="store_true", help=f"{bc.Light_Yellow_f}Search for .ignore files in specified directories{bc.RESET}")

    # **Mutually exclusive group** ensures Paths is required unless --loadPlayList is used
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--Paths", nargs="+", type=validate_user_dirs, default=None, help=f"{bc.Light_Yellow_f}Directories to scan for playable media{bc.RESET}")
    group.add_argument("--loadPlayList", type=validate_playList, help=f"{bc.Light_Yellow_f}Load a playlist from a file\n{bc.Magenta_f}Specify: /path/PlaylistName{bc.RESET}")
    group.add_argument("--listActiveMonitors", nargs="?", const=True, help=f"{bc.Light_Yellow_f}Lists active monitors detected on your computer. Then exit.\nUse as a helper func to --display.{bc.RESET}")

    args = parser.parse_args()

    # Convert string input to corresponding integer value for --reader argument
    args.reader_val_int = int(READER_MAPPING.get(args.reader, READER_MAPPING["auto"]))  # Default to "Auto" if unset
    #args.loadPlayListFlag = False
    args.key_mute_flag = False
    args.loop_flag = False
    args.actualDuration = 0


    if args.loadPlayList is None:
        args.loadPlayListFlag = False
    else:
        args.loadPlayListFlag = True
    return args


# Validate that the user supplied path/playlist exists.
def validate_playList(playlist):
    if not os.path.isfile(os.path.expanduser(playlist)):
        raise argparse.ArgumentTypeError(f"Error: {bc.Red_f}'{playlist}'{bc.Light_Yellow_f} was not found.{bc.RESET}")
    return playlist

'''
# Validate that --listActiveMonitors is a bool
def validate_bool(value):
    return True
'''

# Validate user supplied media directories
def validate_user_dirs(path):
    """Checks if a given path is a valid directory."""
    if path is None:
        raise argparse.ArgumentTypeError(f"Error: {bc.Light_Yellow_f}At least one valid directory must be supplied.{bc.RESET}")
    if not os.path.isdir(os.path.expanduser(path)):
        raise argparse.ArgumentTypeError(f"Error: {bc.Red_f}'{path}'{bc.Light_Yellow_f} is not a valid directory.{bc.RESET}")

    return os.path.expanduser(path)

# Create an argument parser
def restricted_float_or_int(x):
    try:
        x = float(x)  # Convert input to float first
    except ValueError:
        raise argparse.ArgumentTypeError(f"{bc.Red_f}{x}{bc.Light_Yellow_f} is not a valid number{bc.RESET}")

    # Ensure value is either a whole number or a float within range
    if x < 0.5 or x > 5.0:
        raise argparse.ArgumentTypeError(f"{bc.Light_Yellow_f}Value must be between{bc.Green_f} 0.5{bc.Light_Yellow_f} and{bc.Green_f} 5.0{bc.Light_Yellow_f}, but got{bc.Red_f} {x}{bc.RESET}")

    if x.is_integer():  # Convert integer-like floats to ints (e.g., 2.0 → 2)
        return int(x)

    return x  # Return as float if it's a decimal
