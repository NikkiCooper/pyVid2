# 🎬 PyVid2 – A Video Playback Application

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen)](https://www.python.org/downloads/release/python-3100/)
![Community Standards](https://img.shields.io/badge/community--profile-100%25-green)

## 💋 <span style="color:DodgerBlue">Overview</span>

---
### **NOTE:**  This document is likely out of date relative to the Python code contained herein.

pyVid2 is a **Python application** It is mainly designed as a presentation application which may continuously play media
in an automated manner. The latest version is  _vesion 0.50_

pyVid2 is unique in that it only supports playing videos that it finds in user supplied directories.  The scan in pyVid2 is capable of finding tens of thousands of playable media in just seconds. The resulting internal playlist is limited only by how much ram is available. The speed of course depends upon the hardware PyVid2 is running on.  For now, pyVid2 is only in the testing phase.  There are many features missing or not working correctly. In short, pyVid2 is not yet ready for prime time.

## 🧸 <span style="color:DodgerBlue">Features</span>

- Supports multiple video reader backends: **Auto, FFmpeg, OpenCV, ImageIO, Decord**
- Optimized for really fast directory scanning **speed and efficiency**.
- Handles **recursive directory scanning** for playable media.
- Can play .GIF files (feature in development)
- Lots of flexibility with a host of command line arguments.
- Easy to use.

## 🖥️ <span style="color:DodgerBlue">Screenshots</span>

Here are some examples of pyVid2 in action:


![Default playback.](./assets/800x500/pyVid2No-OSD.jpg)
*Default playback.*

![Playback with OSD mode 1.](./assets/800x500/pyVid2OSD-1.jpg)
*Playback with OSD mode 1.*

![Playback with OSD mode 2 + video playback status bar (WIP)](./assets/800x500/PyVid2OSD-2.jpg)
*Playback with OSD mode 2 + video playback status bar (WIP).*

![Playback with video info splash. Definitely work in progress!](./assets/800x500/pyVid2Splash.jpg)
*Playback with video info splash. Definitely work in progress!*

![Video Metadata info](./assets/800x500/pyVid2Metadata.png)
*Some small visual improvements made to the video metadata window*

![Video Playback bar](./assets/800x500/pyVid2PlaybackBar.png)
*The very beginnings of a real video playback status bar.*

![Video Help Window](./assets/1024x640/pyVid2Help.png)
*New interactive help window*


<!--
![No OSD](./assets/800x500/pyVid2No-OSD.jpg)

**Default playback.**

![OSD 1](./assets/800x500/pyVid2OSD-1.jpg)

**Playback with OSD mode 1.**

![OSD 2](./assets/800x500/PyVid2OSD-2.jpg)
**Playback with OSD mode 2 plus status bar.**

![Splash](./assets/800x500/pyVid2Splash.jpg)

**Playback showing video info splash screen.**
-->

## 🚀 <span style="color:DodgerBlue">Quick Start</span>

```sh
git clone https://github.com/NikkiCooper/pyVid2.git
cd pyVid2
# Install the required Python libraries
pip install -r requirements.txt
# Install required fonts to ~/.local/share/pyVid/fonts
./install.sh
# Sample invocation
python pyvid2.py --loop --shuffle --Paths ~/Videos
```
## 🎛️ <span style="color:DodgerBlue">Command-Line Argument Overview</span>



---

### 🎬 <span style="color:DodgerBlue">Required Input Options</span>

| Argument                | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| `--Paths <Path>...`     | Directories to scan for playable media                                      |
| `--Files <File>...`     | Load and play supported media                                               |
| `--loadPlayList`        | Load and play a playlist file (`/path/PlaylistName`)                        |
| `--listActiveMonitors`  | Lists detected monitors, then exits (helper for `--display`)                |

---

### 🎞️ <span style="color:DodgerBlue">Video Playback Options</span>

| Argument              | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| `--loop`              | Loop videos instead of exiting                                               |
| `--shuffle`           | Play videos in random order                                                  |
| `--disableGIF`        | Disable `.gif` file playback                                                 |
| `--enableFFprobe`     | Enable FFprobe metadata analysis with OpenCV                                |
| `--reader`            | Choose video reader backend (`auto`, `ffmpeg`, `opencv`, `imageio`, `dcord`)|
| `--interp`            | Interpolation method (`area`, `cubic`, `linear`, `nearest`, `lanczos4`)     |
| `--loopDelay`         | Delay (in seconds) between videos. Default: `1`                             |
| `--playSpeed`         | Playback speed multiplier (`0.5`–`5.0`). Default: `1.0`                     |
| `--dispTitles`        | Show titles on: `all`, `portrait`, or `landscape` frames                    |
| `--enableOSDcurpos`   | Enable current playback position on-screen overlay                          |

---

### 🎛️ <span style="color:DodgerBlue">Brightness & Contrast Options</span>

| Argument              | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| `--adjust-video`      | Enables brightness/contrast controls (required for below)                  |
| `--brightness`        | Brightness level `-100` to `100`. Default: `0`                              |
| `--contrast`          | Contrast level `-127` to `127`. Default: `0`                                |

---

### 🔊 <span style="color:DodgerBlue">Audio Options</span>

| Argument              | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| `--mute`              | Mute all audio globally                                                     |
| `--aTrack`            | Select audio track (integer index). Default: `0`                           |
| `--usePygameAudio`    | Use Pygame instead of PyAudio backend                                      |

---

### 🖥️ <span style="color:DodgerBlue">System Options</span>

| Argument              | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| `--verbose`           | Enable verbose/debug output                                                 |
| `--display`           | Target specific display by index                                            |
| `--consoleStatusBar`  | Enables live status updates in terminal                                     |

---

### 🗂️ <span style="color:DodgerBlue">File Options</span>

| Argument               | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `--noIgnore`           | Ignore `.ignore` files entirely                                             |
| `--noRecurse`          | Prevent recursive scanning in `--Paths` subfolders                          |
| `--separateDirs`       | Separate screen-shots into Landscape and Portrait sub-folders               |                              
| `--printVideoList`     | Output list of all playable videos from scan                                |
| `--printIgnoreList`    | Show `.ignore` file results from subfolders                                 |


---

### 🧪 <span style="color:DodgerBlue">Post-Processing Filter Options</span>

| Argument              | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| `--sharpen`           | Apply sharpening to video                                                   |
| `--blur`              | Apply standard blur                                                         |
| `--median-blur`       | Enable median blur filtering                                                |
| `--gaussian-blur`     | Enable Gaussian blur                                                        |
| `--noise`             | Add noise for stylistic grain                                               |
| `--cel-shading`       | Enable cel (toon-style) shading                                             |
| `--comic`             | Apply comic-book effect                                                     |
| `--thermal`           | Simulate thermal/heat vision palette                                        |
| `--emboss`            | Emboss the video                                                            |
| `--dream`             | Apply dreamy, soft focus effect                                             |
| `--pixelate`          | Pixelate the video (low-res aesthetic)                                      |
| `--neon`              | Apply neon outlining effect                                                 |
| `--fliplr`            | Flip horizontally (left ↔ right)                                            |
| `--flipup`            | Flip vertically (up ↕ down)                                                 |

---

### 🌊 <span style="color:DodgerBlue">Watercolor Effect Options</span>

| Argument                    | Description                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| `--watercolor`              | Enable watercolor-style post-processing effect                              |
| `--watercolor-scale`        | Scale factor `0.25`–`1.0`. Lower = faster. Default: `0.5`                   |
| `--watercolor-quality`      | Quality/speed tradeoff: `fast`, `medium`, `high`. Default: `medium`         |

---

### 🖼️ <span style="color:DodgerBlue">Oil Painting Effect Options</span>

| Argument                    | Description                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| `--oil-painting`            | Enable oil painting filter                                                  |
| `--oil-size`                | Neighborhood size `5`–`15`. Default: `7`                                    |
| `--oil-dynamics`            | Dynamic blending ratio `1`–`5`. Default: `1`                                |


---

### ✏️ <span style="color:DodgerBlue">Pencil Sketch Parameters</span>  
(from `scripts/pencil-sketch-1`)

| Parameter               | Description                                                                 | Default |
|-------------------------|-----------------------------------------------------------------------------|---------|
| `--sketch-detail`       | Detail level (odd number, higher = less detail)                             | `21`    |
| `--sketch-block-size`   | Block size for edge detection (`7–15`, odd only)                            | `9`     |
| `--sketch-c-value`      | Threshold sensitivity (`1–5`, higher = more edges)                          | `2`     |
| `--sketch-intensity`    | Intensity of the sketch effect (`0.0–1.0`)                                  | `0.7`   |
| `--edge-weight`         | Weight of edges in final image (`0.0–1.0`)                                  | `0.3`   |

> 🧠 For context, see [`scripts/pencil-sketch-1`](scripts/pencil-sketch-1) for full heredoc documentation and sample CLI usage.

---

### 🎭 <span style="color:DodgerBlue">Color Effect Options (Mutually Exclusive)</span>

| Argument             | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| `--greyscale`        | Convert video to greyscale                                                  |
| `--sepia`            | Apply sepia tone effect                                                     |
| `--vignette`         | Add vignette darkening around frame edges                                   |
| `--saturation`       | Adjust color saturation (`0.0`–`2.0`). Default: N/A                         |

---

### ⚡ <span style="color:DodgerBlue">Edge Detection Options</span>

| Argument               | Description                                                                |
|------------------------|----------------------------------------------------------------------------|
| `--edge-detect`        | Enable edge detection filter                                               |
| `--edge-lower`         | Lower threshold (`0 <= value < upper`). Default: `100`                     |
| `--edge-upper`         | Upper threshold (`value <= 255`). Default: `200`                           |

---

### 🗯️ <span style="color:DodgerBlue">Comic Sharpening Filter Options</span>

| Argument                 | Description                                                              |
|--------------------------|--------------------------------------------------------------------------|
| `--comic-sharp`          | Enable comic-style sharpening pipeline                                  |
| `--comic-sharp-amount`   | Sharpening amount (`0.0–1.0`)                                            |
| `--bilateral-d`          | Bilateral filter diameter (`1–15`, odd only). Default: `5`              |
| `--bilateral-color`      | Bilateral color sigma (`10–200`). Default: `60`                         |
| `--bilateral-space`      | Bilateral space sigma (`10–200`). Default: `60`                         |
| `--edge-low`             | Lower threshold for comic edges. Default: `40`                          |
| `--edge-high`            | Upper threshold for comic edges. Default: `140`                         |
| `--color-quant`          | Color quantization factor (`1–64`). Default: `20`                       |

> 🎬 See example usage scripts in [`scripts/comic-sharp-1`](scripts/comic-sharp-1), [`-2`](scripts/comic-sharp-2), and [`-3`](scripts/comic-sharp-3)

---

### 🧪 <span style="color:DodgerBlue">Example Filter Demos</span>

| Script Name         | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `comic-sharp-1`     | Basic usage of `--comic-sharp` with default params                          |
| `comic-sharp-2`     | Intermediate setup with custom bilateral/edge tweaks                       |
| `comic-sharp-3`     | Advanced comic effect with color quant + sharpening                        |
| `pencil-sketch-1`   | Heredoc example + full CLI usage for pencil sketch                         |

---


### ✔️ <span style="color:DodgerBlue">Example Command-Line</span>

```sh
PyVid2 --loop --shuffle --enableFFprobe --Paths ~/SlideShows ~/MyVideos ~/mnt/MediaServer/Music \Videos
```

## 📚 <span style="color:DodgerBlue">Documentation</span>

### 🔖 <span style="color:DodgerBlue">Mutually exclusive arguments</span>
There are currently four command line arguments whose use are mutually exclusive of each other:
1. --Paths PATHS [PATHS ...]
2. --Files FILES [FILES ...] 
3. --loadPlayList LOADPLAYLIST
4. --listActiveMonitors

Due to how _argparse_ handles mutually exclusive argument groups, **--listActiveMonitors** is shown as requiring a parameter.
when using **--help** or **-h**.  Passing a parameter to **--listActiveMonitors** is not necesesary.
The **--Paths** argument is _always_ required unless using **--loadPlayList**, or in more rare cases
**--listActiveMonitors**.  Supply **--Paths** with as many _directories_ you want scanned for media as necessary.
In order to use **--loadPlayList**, an active pyVid2 playlist must be saved to a file after pyVid2 is up and running by
pressing the 'w' key. This writes pyVid2s running playlist to ```~/VideoPlayList-SIZE.txt```, where **_SIZE_** is the
number of entries in the list.  Example: ```~/VideoPlayList-454.txt``` indicates there are 454 entries in the list. The
default path used for the saved playlist is **~**, however, this can be changed by setting an environment variable.
See **Environment variables** below. 

**NOTE:**
~~For the moment, pyVid2 lacks the ability to specify specific videos on the command-line to play!  This is not by 
accident but rather by design. pyVid2 was not designed for this purpose.  pyVid2 was designed as a presentation video player
supporting huge playlists consisting of thousands of entries.~~ 

### 🔖 <span style="color:DodgerBlue">--noRecurse</span>
**--noRecurse** applies to _all_ paths supplied to the **--Paths** argument.  

### 🔖 <span style="color:DodgerBlue">--interp lanczos4</span>
When using **lanczos4** and **--playSpeed** with a playback speed > 1x, playback will experience some lost frames  unless
the hardware pyVid2 is running on is _very_ high end in performance.  This is due to the fact that **lanczos4**  by its
nature is very processor intensive.  PyVid2 defaults to ```interp=cubic```, which is suitable for most hardware.




### 🎬 <span style="color:DodgerBlue">Playback status bar</span>
The playback status bar is work in progress. It is automatically displayed when the mouse cursor is in the lower 15% of
the display. It accepts mouse button clicks too.  This includes the Playback speed and the Volume.  Left-clicking on the 
extreme left of the playback speed or the Volume decreases the values, Left-clicking on the extreme left of the playback
speed or the Volume decreases the values.  The Right-Mouse button also works, only in the opposite manner. 

![Playback status bar](./assets/Playback-1.jpg)

![Playback status bar](./assets/Playback.jpg)

As shown in the above illustration,  when the playback speed is anything other than [1X], the playback duration at that
speed is also displayed to the right of the -->.



### ⌨ <span style="color:DodgerBlue">Keyboard-commands</span>

There are a number of keyboard commands available while a video is playing:

- ░**d**░ = Debug: Print the value of all command line options to the console.
- ░**g**░ = Reshuffle video playlist in place.
- ░**h**░ = Help
- ░**i**░ = Show video metadata window. Click the **OK** button to clear. [work in progress] 
- ░**l**░ = Loop the currently playing video indefinately. This is a toggle.
- ░**m**░ = Toggle mute video.
- ░**n**░ = Advance to next video.
- ░**o**░ = Toggle OSD views. (3 states)
- ░**p**░ or **Space Bar** = Pause video.
- ░**q**░ or **ESC** = Quit the program
- ░**r**░ or **HOME** = Restart the currently playing video back to the beginning.
- ░**s**░ = Save Screenshot to ~/pyVidScreenShots
- ░**t**░ = Toggle mp4 Title display. (3 states)
- ░**w**░ = Save pyVid2s internal playlist to a file.
- ░ **+** ░ = (keypad) Increase playback speed by 0.50  (*max is 5.0*)
- ░ **-** ░ = (keypad) Decrease playback speed by 0.50  (*min is 0.50*)
- ░**END**░ = Seek to the end of video minus about 10 seconds (video_duration - 10) sec.
- ░**→**░ Seek *forward* 20 seconds.
- ░**←**░ Seek *backward* 20 seconds.
- ░**↑**░ Increase the volume by 10%.
- ░**↓**░ Decrease the volume by 10%.
- **Backspace** = Play previous video.
<!--
- ➡️  = Seek 20 seconds.
- ⬅️  = seek -20 seconds.
- ⬆️  = Increase the volume by 10%
- ⬇️  = Decrease the volume by 10%
-->
<!-- ░a░ ░b░ ░c░ ░d░ ░e░ ░f░ ░g░ ░h░ ░i░ ░j░ ░k░ ░l░ ░m░ ░n░ ░o░ ░p░ ░q░ ░r░ ░s░ ░t░ ░u░ ░v░ ░w░ ░x░ ░y░ ░z░ ░+░ ░-░ ░ ░!░ ░@░ ░ ░#░ ░$░ ░%░ ░&░ ░ ░*░ ░(░ ░ ░)░   ░_░ ░+░ ░~░ ░1░ ░2░ ░3░ ░4░ ░5░ ░6░ ░7░ ░8░ ░9░ ░0░ ░|░ ░→░ ░←░ ░↑░ ░↓░
░A░ ░B░ ░C░ ░D░ ░E░ ░F░ ░G░ ░H░ ░I░ ░J░ ░K░ ░L░ ░M░ ░N░ ░O░ ░P░ ░Q░ ░R░ ░S░ ░T░ ░U░ ░V░ ░W░ ░X░ ░Y░ ░Z░ -->

### 🖱️ <span style="color:DodgerBlue">Mouse</mouse>

- **Left Mouse Long Press** = Advance to next video.  Long press = Left mouse button pressed >= 1 second.
- **Right Mouse Long Press** = Play previous video.  Long press = Right mouse button pressed >= 1 second.
- **Middle Mouse Long Press** = Pause Video toggle.  Long Press = Mouse Wheel button pressed >= 1 second.
- **Wheel UP** = Seek ahead 5 seconds.
- **Wheel Down** = Seek backwards 5 seconds.

### 💻 <span style="color:DodgerBlue">OSD</span>

There are three modes for the **On Screen Display**. Pressing the ░**o**░ key 3 times will toggle through the three modes:

1. **Off**
2. ▶️ **HH:MM:SS / HH:MM:SS**
3. ▶️ **HH:MM:SS**

In the *2nd* mode, the **HH:MM:SS** to the far left is the ***current play position***. The one to the far right is the ***total video duration*** time.
The *3rd* mode behaves in a special manner.  When the ***current play position*** is approx. ***20 seconds*** from the video end, its default color will slowly fade to a much brighter one giving a visual indication the video is 20 seconds from completion.  Currently, the OSD timings are displayed in the color of **DodgerBlue**. When the color fading begins in *mode 3*, The OSD text color slowly fades until it reaches **HotPink** which denotes the end of the video had been reached. By default, the OSD is ***OFF*** when **pyVid2** is run. The command line argument ***--enableOSDcurpos*** enables OSD mode 3 at runtime.


### 💻 <span style="color:DodgerBlue">Portrait frame Detection</span>

Portrait frame detection determines whether a given image surface represents a "portrait" orientation by analyzing its pixel data. The method inspects specific regions on the left and right edges of the
image to verify if they contain predominantly black pixels (with a threshold applied for RGB channel values). The function relies on efficient pixel access and locks the input surface during processing. The portrait detection is based on specified areas and is useful for identifying images surrounded by black padding.  Note that this is highly experimental and is likely to not be useful to the vast majority of users.  In fact,it is likely to not even work at all!  Currently, **Display Video Title**,  **--dispTitle** and friends (see below), as well as screenshot saving when using the command line argument **--separateDirs** make use of this. When specifying **--separateDirs** on the command line and upon saving a screenshot, Portrait fame detection is enabled and saved screenshots will be placed in Landscape and Portrait subfolders.  This functionality has very limited usefulness and will likely **NOT** work for most people.   


### 💻 <span style="color:DodgerBlue">Display Video Title</span>

This command key (t) along with its command line interface counterpart **--dispTitle** deserves some explanation.
pyVid2 has some very specific use cases that probably will not be of much use to most users.  In the world of video, there is no such thing as 'portrait' (where the image height > image width) or 'landscape' (where the image width > image height). In video, each displayed frame is *always* the same size. That having been said, pyVid2 is a *presentation* video player.  Consider the usage case
of a photographer. He or she may wish to show-ase their work by rendering their photos into slideshow videos.  These videos will likely have different transition effects for each slide or photo.  In the world of photography, depending upon the subject, many photos will likely be taken in both portrait and landscape.  Thus, when these photos are rendered into a video slideshow, The resulting video will consist of photos representing both.  Other subjects might consist only of landscape photos or just portrait photos. **--dispTitle** can take one of three possible parameters.  These are:
- **all**       =  Display metadata title tag text on all frames
- **portrait**  =  Display metadata title tag text on detected portrait frames
- **landscape** =  Display metadata title tag text on landscape frames (likely all frames) 

The portrait detection algorithm is rather crude. There are so many cases where this will fail.  It is suggested to just use **all** and not worry about it. The command key (t) will toggle between the various possible states: **None**->**all**->**portrait**->**landscape**->**None**    

Note that the selection of any parameter other than **all* is likely not going to work as intended.  Customized metadata tags can be added to a mp4 video (and likely others) by using ffmpeg:
```sh
# The -c copy is very important as it will prevent having to transcode the entire video over again. 
ffmpeg -loglevel quiet -i video.mp4 -c copy -movflags use_metadata_tags -metadata title="Nikki and the girls on vacation in the Outback!" output.mp4
```
The new tag called **title** can be verified by using ffprobe:
```sh
ffprobe -loglevel quiet -show_format output.mp4  | grep TAG:title | cut --delimiter='=' -f2
Nikki and the girls on vacation in the Outback!
$
```





### 🔔 <span style="color:DodgerBlue">Ignore Files</span>

Ignore files take the form of **.ignore** The case does not matter.  Their purpose is to mark certain directories
in a directory tree structure as **ignored** whenever pyVid2 is scanning for media files. In linux, the typical way
to create an ignore file is: ```touch .ignore``` from the command-prompt. The following example illustrates the
concept:

```md
     +------------------+
     | Video_Repository |
     +------------------+
              |
              |
      +-------+--------+
      |                |
      |                |
 +----+-----+   +------+-------+
 |Music_Vids|   |SlideShow_Vids|
 +----------+   +--------------+
    .ignore      Slideshow1.mp4
    M1.mp4       Slideshow2.mp4
    M2.mp4       Slideshow3.mp4
    M3.mp3       Slideshow4.mp4
     ...              ...
```

In the above simplified example, if 'Video_Repository' is the directory pyVid2 is recursively scanning,
it will ignore all playable media in Music_Vids, while playing everything in SlideShow_Vids.  The usefulness of
*.ignore* files may not seem obvious with just 2 directories, but if Video_Repository had 100 subdirectories,
*.ignore* files can provide a quick and easy way to be able to view (and not to view) video content.  If pyVid2 is
given the **--printIgnoreList** command-line argument along with one or more directories to scan via **--Paths**, it will
produce a report in the console of all *.ignore* files found in the specified directory trees. For example: ```pyVid2 --printIgnoreList --Paths Video_Repository```.  By default, **pyVid2** honors all *.ignore* files it encounters. The command line argument **--noIgnore** will direct pyVid2 to ignore any *.ignore* files it encounters in any paths specified by the **--Paths** argument. **--noIgnore**  is global across all specified paths given to **--Paths**.  In other words,  to **pyVid2**,  it is an all or nothing proposition.

### ♻️ <span style="color:DodgerBlue">Environment Variables</span>

Command line arguments (if there are any) always take priority over any set environment variables.

- **PYGAME_DISPLAY=display** For multiple monitor setups. Sets the monitor to play media on.  Select 0|1|2 ...
- **SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS=0** For multi-monitor setups, this is necessary to avoid the video minimizing when it loses focus.
- **SAVE_PLAYLIST_PATH=path** Specifiy the path to save pyVids playlist to ('w' keyboard command)

Currently, there is only one command line argument that overrides any set environment variables:  **--display**.  For example: ```pyVid2 --display 2`` will start the video on monitor #2 on a three monitor setup.  Note that monitor numbers begin with 0.  By default, pyVid2 will render the video in the active monitor it is run in. Use **--listActiveMonitors** to retrieve a list of possible monitors to use with the **--display** argument.   

## 🛠️ <span style="color:DodgerBlue">Installation</span>

### ✅ <spam style="color:DodgerBlue">Requirements</spam>

- 🔗 [pygame>=2.6](https://www.pygame.org/download.shtml)
- 🔗 [cachetools>=75.8.0](https://pypi.org/project/cachetools/)
- 🔗 [setuptools>=5.5.2](https://pypi.org/project/setuptools/)
- 🔗 [pyvidplayer2>=0.9.26](https://pypi.org/project/pyvidplayer2/)

There are other requirements such as **_ffmpeg_** that will need to be installed via your Linux distributions 
package manager. Refer to your particular distributions documention for information how to accomplish that. 

```sh
git clone https://github.com/NikkiCooper/pyVid2.git
cd pyVid2
pip install -r requirements.txt
# Installs needed fonts to ~/.local/share/pyVid/fonts
./install.sh   
#run  ./pyvid2  from  this directory. 
./pyvid2 --help
```

## 💩 <span style="color:HotPink">Ubuntu Linux</span>

If pyVid2 doesn't run in your version of Ubuntu Linux, don't despair. Simply run pyVid2 in a
Python virtual environment using **venv**,  🔗  [Anaconda](https://www.anaconda.com/docs/getting-started/anaconda/install) or  🔗 [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install)

### 😺 Using venv (easiest, is included with Python)

```sh
# Create the environment 
python -m venv pyvidenv
# Activate the new environment
source pyvidenv/bin/activate
# Install pyVid2 required libraries
cd "pyVid2_installation_dir"
pip install -r requirements.txt
```

###  🐍 Using Anaconda or Miniconda (requires that Anaconda or Miniconda be installed)

```sh
# Update to latest
conda update conda
# Create the environment
conda create -n pyvidenv python=3.12
# Activate the new environment
conda activate pyvidenv
# Install pyVid2 required libraries
cd "pyVid2_installation_dir"
pip install -r requirements.txt
```

## ☠️ <span style="color:DodgerBlue">Issues</span>

- PyVid2 is work in progress and does not pretend to be anything other than a learning tool.
- There are some usability bugs, but these are quickly being squashed.
- Note that only Linux is supported currently.
- For now only fullscreen mode is supported.
- ~~There are issues with using the OSD when playing videos less than the width of the screen being played on.~~
- Under Ubuntu Linux 24.04 LTS there may be audio issues.  Use --usePygameAudio as a workaround.
- If you have issues let me know, I will try to help.
