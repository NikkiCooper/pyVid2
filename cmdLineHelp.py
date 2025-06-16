#  cmdLineHelp.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# help dictionary for argparse usage in cmdLineOpts.py
#
from Bcolors import Bcolors
bc = Bcolors()

#argparse parser.add_argument_group()
group = dict(
	required_group=f"{bc.BOLD}{bc.Light_Blue_f}Required. One of{bc.RESET}",
	video_group=f"{bc.BOLD}{bc.Blue_f}Video Playback Options{bc.RESET}",
	pp_group=f"{bc.BOLD}{bc.Light_Blue_f}Post-Processing Filter Options{bc.RESET}",
	watercolor_group=f"{bc.BOLD}{bc.Light_Blue_f}Watercolor Effect Options{bc.RESET}",
	oil_painting_group=f"{bc.BOLD}{bc.Light_Blue_f}Oil Painting Effect Options{bc.RESET}",
	pencil_group=f"{bc.BOLD}{bc.Light_Blue_f}Pencil Sketch Effect Options{bc.RESET}",
	color_settings_group=f"{bc.BOLD}{bc.Light_Blue_f}Color Effect Options. One of{bc.RESET}",
	edge_group=f"{bc.BOLD}{bc.Light_Blue_f}Edge Detection Options{bc.RESET}",
	comic_group=f"{bc.BOLD}{bc.Light_Blue_f}Comic Effect Options{bc.RESET}",
	brightness_group=f"{bc.BOLD}{bc.Light_Blue_f}Brightness/Contrast Options{bc.RESET}",
	audio_group=f"{bc.BOLD}{bc.Light_Blue_f}Audio Options{bc.RESET}",
	system_group=f"{bc.BOLD}{bc.Light_Blue_f}System Options{bc.RESET}",
	file_group=f"{bc.BOLD}{bc.Light_Blue_f}File Options{bc.RESET}"
)

# argparse help=""
help = dict(
	loop=f"{bc.Light_Yellow_f}Loop videos instead of exiting{bc.RESET}",
	shuffle=f"{bc.Light_Yellow_f}Play videos in random order{bc.RESET}",
	disableGIF=f"{bc.Light_Yellow_f}Disable playing .GIF files{bc.RESET}",
	enableFFprobe=f"{bc.Light_Yellow_f}Enable FFprobe when using openCV{bc.RESET}",
	reader=f"{bc.Light_Yellow_f}Use interpolation method for resizing frames.\n{bc.Magenta_f}Default: {bc.Green_f}cubic{bc.Magenta_f} (recommended){bc.RESET}",
	interp=f"{bc.Light_Yellow_f}Use interpolation method for resizing frames.\n{bc.Magenta_f}Default: {bc.Green_f}cubic{bc.Magenta_f} (recommended){bc.RESET}",
	loopDelay=f"{bc.Light_Yellow_f}The delay in seconds between each video.\n{bc.Magenta_f}Default:{bc.Green_f} 1{bc.Light_Yellow_f} sec{bc.Magenta_f} (recommended){bc.RESET}",
	playSpeed=f"{bc.Light_Yellow_f}Set playback speed ({bc.Green_f}0.5{bc.Light_Yellow_f} - {bc.Green_f}5.0{bc.Light_Yellow_f})\n{bc.Magenta_f}Default: {bc.Green_f}1.0{bc.RESET}",
	dispTitles=f"{bc.Light_Yellow_f}Where to display titles.{bc.RESET}",
	enableOSDcurpos=f"{bc.Light_Yellow_f}Enable {bc.White_f}OSD{bc.Light_Yellow_f} current position counter on startup.{bc.RESET}",
	#
	sharpen=f"{bc.Light_Yellow_f}Enable {bc.White_f}sharpening{bc.Light_Yellow_f} filter.{bc.RESET}",
	blur=f"{bc.Light_Yellow_f}Enable {bc.White_f}blurring{bc.Light_Yellow_f} filter.{bc.RESET}",
	gaussian=f"{bc.Light_Yellow_f}Enable {bc.White_f}gaussian blurring{bc.Light_Yellow_f} filter.{bc.RESET}",
	median=f"{bc.Light_Yellow_f}Enable {bc.White_f}median blurring{bc.Light_Yellow_f} filter.{bc.RESET}",
	noise=f"{bc.Light_Yellow_f}Enable {bc.White_f}noise{bc.Light_Yellow_f} filter.{bc.RESET}",
	cel_shading=f"{bc.Light_Yellow_f}Enable {bc.White_f}cell shading{bc.Light_Yellow_f} filter.{bc.RESET}",
	comic=f"{bc.Light_Yellow_f}Enable {bc.White_f}comic{bc.Light_Yellow_f} filter.{bc.RESET}",
	#
	thermal=f"{bc.Light_Yellow_f}Enable {bc.White_f}thermal{bc.Light_Yellow_f} filter.{bc.RESET}",
	emboss=f"{bc.Light_Yellow_f}Enable {bc.White_f}embossing{bc.Light_Yellow_f} filter.{bc.RESET}",
	dream=f"{bc.Light_Yellow_f}Enable {bc.White_f}dreamy{bc.Light_Yellow_f} filter.{bc.RESET}",
	pixelate=f"{bc.Light_Yellow_f}Enable {bc.White_f}pixelation{bc.Light_Yellow_f} filter.{bc.RESET}",
	neon=f"{bc.Light_Yellow_f}Enable {bc.White_f}neon{bc.Light_Yellow_f} filter.{bc.RESET}",
	fliplr=f"{bc.Light_Yellow_f}Enable {bc.White_f} flip-lr{bc.Light_Yellow_f} filter.\nFlips the video horizontally (left to right).{bc.RESET}",
	flipup=f"{bc.Light_Yellow_f}Enable {bc.White_f} flip-up{bc.Light_Yellow_f} filter.\nFlips the video vertically (upside down).{bc.RESET}",
	#
	watercolor=f"{bc.Light_Yellow_f}Enable {bc.White_f}watercolor effect{bc.Light_Yellow_f} filter {bc.Light_Blue_f}(slow).{bc.RESET}",
	watercolor_scale=f"{bc.Light_Yellow_f}Scale factor for processing ({bc.Green_f}0.25{bc.Light_Yellow_f} - {bc.Green_f}1.0{bc.Light_Yellow_f}), {bc.Magenta_f}lower = {bc.Green_f}faster{bc.Light_Yellow_f}\nRequires {bc.White_f}--watercolor.\n{bc.Magenta_f}Default: {bc.Green_f}0.5{bc.RESET}",
	watercolor_quality=f"{bc.Light_Yellow_f}Watercolor effect quality/speed trade-off.\nRequires {bc.White_f}--watercolor.\n{bc.Magenta_f}Default: {bc.Green_f}medium{bc.RESET}",
	#
	oil_painting=f"{bc.Light_Yellow_f}Enable {bc.White_f}oil painting effect{bc.Light_Yellow_f} filter.{bc.RESET}",
	oil_size=f"{bc.Light_Yellow_f}Oil painting neighborhood size ({bc.Green_f}5{bc.Light_Yellow_f} -{bc.Green_f} 15{bc.Light_Yellow_f})\nRequires {bc.White_f}--oil-painting.\n{bc.Magenta_f}Default:{bc.Green_f}7{bc.RESET}",
	oil_dynamics=f"{bc.Light_Yellow_f}Oil painting dynamic ratio ({bc.Green_f}1{bc.Light_Yellow_f}-{bc.Green_f}5{bc.Light_Yellow_f})\nRequires {bc.White_f}--oil-painting.\nDefault: {bc.Green_f}1{bc.RESET}",
	#
	pencil_sketch=f"{bc.Light_Yellow_f}Enable {bc.White_f}pencil sketch effect{bc.Light_Yellow_f} filter.{bc.RESET}",
	sketch_detail=f"{bc.Light_Yellow_f}Detail level for pencil sketch ({bc.Light_Blue_f}odd number{bc.Light_Yellow_f}, {bc.Green_f}higher{bc.Light_Yellow_f} ={bc.Magenta_f} less detail{bc.Light_Yellow_f})\nRequires {bc.White_f}--pencil-sketch.\n{bc.Magenta_f}Default: {bc.Green_f}21{bc.RESET}",
	sketch_block_size=f"{bc.Light_Yellow_f}Block size for edge detection ({bc.Light_Blue_f}odd number{bc.Light_Yellow_f}, {bc.Green_f}higher{bc.Light_Yellow_f} ={bc.Magenta_f} less detail{bc.Light_Yellow_f}, try:{bc.Green_f} 7{bc.Light_Yellow_f} - {bc.Green_f}15{bc.Light_Yellow_f})\nRequires {bc.White_f}--pencil-sketch\n{bc.Magenta_f}Default: {bc.Green_f}9{bc.RESET}",
	sketch_c_value=f"{bc.Light_Yellow_f}Threshold sensitivity ({bc.Green_f}higher{bc.Light_Yellow_f} ={bc.Magenta_f} more edges{bc.Light_Yellow_f},{bc.Light_Yellow_f} try:{bc.Green_f} 1{bc.Light_Yellow_f} - {bc.Green_f}5{bc.Light_Yellow_f})\nRequires {bc.White_f}--pencil-sketch.\n{bc.Magenta_f}Default: {bc.Green_f}2{bc.RESET}",
	sketch_intensity=f"{bc.Light_Yellow_f}Intensity of the sketch effect ({bc.Green_f}0{bc.Light_Yellow_f}.{bc.Green_f}0{bc.Light_Yellow_f} - {bc.Green_f}1{bc.Light_Yellow_f}.{bc.Green_f}0{bc.Light_Yellow_f})\nRequires {bc.White_f}--pencil-sketch.\n{bc.Magenta_f}Default: {bc.Green_f}0.7{bc.RESET}",
	sketch_edge_weight=f"{bc.Light_Yellow_f}Weight of edges in final image ({bc.Green_f}0{bc.Light_Yellow_f}.{bc.Green_f}0{bc.Light_Yellow_f} - {bc.Green_f}1{bc.Light_Yellow_f}.{bc.Green_f}0{bc.Light_Yellow_f})\nRequires {bc.White_f}--pencil-sketch.\n{bc.Magenta_f}Default: {bc.Green_f}0.3{bc.RESET}",
	#
	greyscale=f"{bc.Light_Yellow_f}Convert video to greyscale.\n{bc.BOLD}{bc.Cyan_f}Cannot be used with {bc.White_f}--sepia{bc.Light_Yellow_f},{bc.White_f} --vignette{bc.Light_Yellow_f} or{bc.White_f} --saturation{bc.Light_Yellow_f}.{bc.RESET}",
	sepia=f"{bc.Light_Yellow_f}Apply sepia tone effect.\n{bc.BOLD}{bc.Cyan_f}Cannot be used with {bc.White_f}--greyscale{bc.Light_Yellow_f},{bc.White_f} --vignette{bc.Light_Yellow_f} or{bc.White_f} --saturation{bc.Light_Yellow_f}.{bc.RESET}",
	vignette=f"{bc.Light_Yellow_f}Apply vignette effect.\n{bc.BOLD}{bc.Cyan_f}Cannot be used with {bc.White_f}--greyscale{bc.Light_Yellow_f} or {bc.White_f}--sepia.{bc.RESET}",
	saturation=f"{bc.Light_Yellow_f}Adjust color saturation ({bc.Green_f}0.0{bc.Light_Yellow_f} - {bc.Green_f}2.0{bc.Light_Yellow_f}).\n{bc.BOLD}{bc.Cyan_f}Cannot be used with {bc.White_f}--greyscale{bc.Light_Yellow_f} or {bc.White_f}--sepia.{bc.RESET}",
	#
	edge_detect=f"{bc.Light_Yellow_f}Enable {bc.White_f}edge{bc.Light_Yellow_f} detection filter.{bc.RESET}",
	edge_lower=f"{bc.Light_Yellow_f}Lower threshold {bc.Green_f}0{bc.Light_Blue_f} <= {bc.Green_f}EDGE_LOWER{bc.Light_Blue_f} < {bc.Green_f}EDGE_UPPER{bc.Light_Yellow_f}\nRequires {bc.White_f}--edge-detect\n{bc.Magenta_f}Default: {bc.Green_f}100{bc.RESET}",
	edge_upper=f"{bc.Light_Yellow_f}Upper threshold {bc.Green_f}0{bc.Light_Blue_f} <= {bc.Green_f}EDGE_UPPER{bc.Light_Blue_f} <= {bc.Green_f}255{bc.Light_Yellow_f}\nRequires {bc.White_f}--edge-detect.\n{bc.Magenta_f}Default: {bc.Green_f}200{bc.RESET}",
	#
	comic_sharp=f"{bc.Light_Yellow_f}Enable {bc.White_f}comic sharpening filter.{bc.RESET}",
	comic_sharp_amount=f"{bc.Light_Yellow_f}Comic sharpening amount ({bc.Green_f}0.0{bc.Light_Yellow_f} - {bc.Green_f}1.0{bc.Light_Yellow_f}).\nRequires {bc.White_f}--comic-sharp.{bc.RESET}",
	bilateral_d=f"{bc.Light_Yellow_f}Bilateral filter diameter.\nRequires {bc.White_f}--comic-sharp.\n{bc.Magenta_f}Default: {bc.Green_f}5{bc.RESET}",
	bilateral_color=f"{bc.Light_Yellow_f}Bilateral filter color sigma ({bc.Green_f}10{bc.Light_Yellow_f} - {bc.Green_f}200{bc.Light_Yellow_f}).\nRequires {bc.White_f}--comic-sharp.\n{bc.Magenta_f}Default: {bc.Green_f}60{bc.RESET}",
	bilateral_space=f"{bc.Light_Yellow_f}Bilateral filter space sigma ({bc.Green_f}10{bc.Light_Yellow_f} - {bc.Green_f}200{bc.Light_Yellow_f}).\nRequires {bc.White_f}--comic-sharp.\n\n{bc.Magenta_f}Default: {bc.Green_f}60{bc.RESET}",
	edge_low=f"{bc.Light_Yellow_f}Lower threshold for edge detection ({bc.Green_f}0{bc.Light_Blue_f} <= {bc.Green_f}EDGE_LOW{bc.Light_Blue_f} < {bc.Green_f}EDGE_HIGH{bc.Light_Yellow_f}).\nRequires {bc.White_f}--comic-sharp.\n{bc.Magenta_f}Default: {bc.Green_f}40{bc.RESET}",
	edge_high=f"{bc.Light_Yellow_f}Upper threshold for edge detection ({bc.Green_f}0{bc.Light_Blue_f} <= {bc.Green_f}EDGE_HIGH{bc.Light_Blue_f} <= {bc.Green_f}255{bc.Light_Yellow_f}).\nRequires {bc.White_f}--comic-sharp.\n{bc.Magenta_f}Default: {bc.Green_f}140{bc.RESET}",
	color_quant=f"{bc.Light_Yellow_f}Color quantization factor ({bc.Green_f}1{bc.Light_Yellow_f} - {bc.Green_f}64{bc.Light_Yellow_f}).\nRequires {bc.White_f}--comic-sharp.\n{bc.Magenta_f}Default: {bc.Green_f}20{bc.RESET}",
	#
	adjust_video=f"{bc.Light_Yellow_f}Adjust video contrast and brightness.\n{bc.BOLD}{bc.Cyan_f}Cannot be used with {bc.White_f}--saturation{bc.Light_Yellow_f}.{bc.RESET}",
	brightness=f"{bc.Light_Yellow_f}Adjust brightness ({bc.Green_f}-100{bc.Light_Yellow_f} to{bc.Green_f} 100{bc.Light_Yellow_f})\nRequires {bc.White_f} --adjust-video.\n{bc.Magenta_f}Default: {bc.Green_f}0{bc.RESET}",
	contrast=f"{bc.Light_Yellow_f}Adjust contrast ({bc.Green_f}-127{bc.Light_Yellow_f} to{bc.Green_f} 127{bc.Light_Yellow_f})\nRequires {bc.White_f} --adjust-video.\n{bc.Magenta_f}Default: {bc.Green_f}0{bc.RESET}",
	#
	mute=f"{bc.Light_Yellow_f}Mute all audio globally.{bc.RESET}",
	aTrack=f"{bc.Light_Yellow_f}Select a specific audio track.\n{bc.Magenta_f}Default: {bc.Green_f}0{bc.RESET}",
	usePygameAudio=f"{bc.Light_Yellow_f}Use Pygame or Pyaudio.\n{bc.Magenta_f}Default: {bc.Green_f}Pyaudio{bc.RESET}",
	#
	verbose=f"{bc.Light_Yellow_f}Enable verbose output.{bc.RESET}",
	display=f"{bc.Light_Yellow_f}Enable output on a specific display.\n{bc.Magenta_f}Default: {bc.Green_f}The currenty active display{bc.RESET}",
	consoleStatusBar=f"{bc.Light_Yellow_f}Enables a debug status bar in the console.{bc.RESET}",
	#
	noIgnore=f"{bc.Light_Yellow_f}Do not honor {bc.Green_f}.ignore{bc.Light_Yellow_f} files.{bc.RESET}",
	noRecurse=f"{bc.Light_Yellow_f}Do not recurse into subfolders specified by {bc.White_f}--Paths.{bc.RESET}",
	printVideoList=f"{bc.Light_Yellow_f}Print a list of available videos to the console.{bc.RESET}",
	printIgnoreList=f"{bc.Light_Yellow_f}Search for {bc.Green_f}.ignore{bc.Light_Yellow_f} files in subfolders specified by {bc.White_f}--Paths.{bc.RESET}",
	#
	Paths=f"{bc.Light_Yellow_f}Directories to scan for playable media.\n{bc.Magenta_f}Specify: {bc.Green_f}<Path> <Path> <Path> ...{bc.RESET}",
	Files=f"{bc.Light_Yellow_f}Load & play supported media.\n{bc.Magenta_f}Specify: {bc.Green_f}<File> <File> <File> ...{bc.RESET}",
	loadPlayList=f"{bc.Light_Yellow_f}Load and play a playlist from a file.\n{bc.Magenta_f}Specify:{bc.Green_f} /path/PlaylistName{bc.RESET}",
	listActiveMonitors=f"{bc.Light_Yellow_f}Lists detected active monitors, then exits.\nUse as a helper function to {bc.White_f}--display.\n{bc.Magenta_f}Ignore{bc.White_f}[LISTACTIVEMONITORS]{bc.RESET}"
)