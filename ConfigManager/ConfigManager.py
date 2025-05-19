#!/usr/bin/env python

import pygame
import configparser
import os

class ConfigManager:
    def __init__(self, config_file=None):
        self.config_file = config_file or os.path.expanduser("~/.config/pyVid/pyVid.ini")
        #self.config = configparser.ConfigParser()       # By default configparser is case insensitive and converts all keys to lower case.
        self.config = configparser.RawConfigParser()    # Init the case sensitive configparser
        self.config.optionxform = str  # Prevents automatic lowercase conversion
        self.load_config()

    def print_config(self):
        """Print all configuration values."""
        for section in self.config.sections():
            print(f"[{section}]")
            for key, value in self.config[section].items():
                print(f"{key} = {value}")
            print()  # Adds spacing between sections

    def load_config(self):
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            print("Config file not found, using defaults.")

    def auto_convert_value(self, value):
        """Convert config values to their proper types (int, float, bool, tuple, or named color)."""
        if value.lower() in {"true", "false"}:  # Boolean conversion
            return value.lower() == "true"
        try:
            if "," in value:  # Tuple conversion (comma-separated)
                return tuple(map(int, value.split(",")))
            return int(value)  # Integer conversion
        except ValueError:
            pass  # If conversion fails, continue to next step

        try:
            return pygame.Color(value)  # Named color conversion
        except ValueError:
            return value  # Default: return as string

    def get_section_as_dict(self, section):
        """Retrieve all key-value pairs from a section as a properly typed dictionary."""
        if section in self.config:
            return {key: self.auto_convert_value(value) for key, value in self.config[section].items()}
        else:
            print(f"Section '{section}' not found.")
            return {}

    def get_resolved_value(self, section, key):
        """Retrieve a config value and resolve placeholders."""
        value = self.config.get(section, key)
        for ref_key in self.config[section]:
            value = value.replace(f"{{{ref_key}}}", self.config.get(section, ref_key))
        return value

    def get_color(value):
        """Convert named colors or tuples into RGB."""
        if "," in value:  # If it's a tuple (like "20,20,20,150")
            return tuple(map(int, value.split(",")))
        try:
            return pygame.Color(value)  # Named color conversion
        except ValueError:
            print(f"Warning: '{value}' is not a recognized color.")
            return (255, 255, 255)  # Default to white if invalid

    def get(self, section, key, fallback=None):
        """Retrieve a config value with optional fallback."""
        return self.config.get(section, key, fallback=fallback)

    def set(self, section, key, value):
        """Set a config value and save changes."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()

    def save_dict_to_ini(self, section, data_dict):
        """Save a dictionary back to the `.ini` file while preserving key case."""
        if section not in self.config:
            self.config[section] = {}

        for key, value in data_dict.items():
            self.config.set(section, key, str(value))  # Ensure values are stored as strings

        self.save_config()

    def save_config(self):
        """Save configuration to file."""
        with open(self.config_file, "w") as configfile:
            self.config.write(configfile)

# Example usage
config = ConfigManager()
#config.set("General", "fullscreen", "True")
#print(config.get("General", "fullscreen"))  # Output: True
config.print_config()

'''
volume = float(config.get("Audio", "volume", fallback=0.20))
print(f"volume: {round(volume, 2)}")



general_settings = config.get_section_as_dict("General")
audio_settings = config.get_section_as_dict("Audio")

print(f"General Settings: {general_settings}")
print()
print(f"Audio Settings: {audio_settings}")

ScreenShotPath = config.get("Paths", "ScreenShots").strip('"')  # Removes surrounding quotes
print(f"ScreenShotPath: {os.path.expanduser(ScreenShotPath)}")

progress_bg = config.get_resolved_value("ProgressBar", "progress_bg")
print(f"progress_bg: {progress_bg}")
print()
print()

progress_bar_settings = config.get_section_as_dict("ProgressBar")
osd_settings = config.get_section_as_dict("OSD")

print("ProgressBar Settings:", progress_bar_settings)
print()
print("OSD Settings:", osd_settings)
'''

# In order to save to the ini file:
config.set("File", "noIgnore", "True")
config.set("File", "noRecurse", "True")
config.save_config()
'''
print()
print()
# Modify some settings within a dictionary
progress_bar_settings = config.get_section_as_dict("ProgressBar")
progress_bar_settings["progress_alpha"] = 175  # Update value
progress_bar_settings["progress_bg"] = "30,30,30,175"  # Modify background color

# Save the dictionary back to the `.ini` file
config.save_dict_to_ini("ProgressBar", progress_bar_settings)

print("Updated configuration saved!")
'''

'''
file_settings = {
    "noIgnore": "True",
    "noRecurse": "True",
}

config.save_dict_to_ini("File", file_settings)

print("Case-sensitive config saved!")
'''