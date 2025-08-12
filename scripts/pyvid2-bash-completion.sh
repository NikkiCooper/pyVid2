#!/bin/bash
# Bash Completion Script for pyv2 (PyVid2 CLI) - v0.1
# Source this file in your terminal for live testing:
# $ source /path/to/pyvid2-bash-completion.sh

_pyv2_complete() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Core argument groups
    local required_opts="--Paths --Files --loadPlayList --listActiveMonitors"
    local video_opts="--loop --shuffle --disableGIF --enableFFprobe --reader --interp --loopDelay --playSpeed --dispTitles --enableOSDcurpos"
    local audio_opts="--mute --aTrack --usePygameAudio"
    local system_opts="--verbose --display --consoleStatusBar"
    local file_opts="--noIgnore --noRecurse --separateDirs --printVideoList --printIgnoreList"
    local filter_opts="--sharpen --blur --median-blur --gaussian-blur --noise --cel-shading --comic --thermal --emboss --dream --pixelate --neon --fliplr --flipup"

    local all_opts="$required_opts $video_opts $audio_opts $system_opts $file_opts"

    # Value suggestions for select flags
    case "$prev" in
        --Paths|--Files)
            COMPREPLY=( $(compgen -d -- "$cur") )  # suggest directories for both
            return 0
            ;;
        --loadPlayList)
            COMPREPLY=( $(compgen -f -- "$cur") )  # suggest files
            return 0
            ;;
        --reader)
            COMPREPLY=( $(compgen -W "auto ffmpeg opencv imageio dcord" -- "$cur") )
            return 0
            ;;
        --interp)
            COMPREPLY=( $(compgen -W "area cubic linear nearest lanczos4" -- "$cur") )
            return 0
            ;;
        --dispTitles)
            COMPREPLY=( $(compgen -W "all portrait landscape" -- "$cur") )
            return 0
            ;;
        --display)
            COMPREPLY=( $(compgen -W "0 1 2 3" -- "$cur") )
            return 0
            ;;
        # For numeric values, you can skip completion or suggest common ones
        --loopDelay|--playSpeed)
            COMPREPLY=( $(compgen -W "0.5 1.0 1.5 2.0 2.5 3.0" -- "$cur") )
            return 0
            ;;
        *)
            COMPREPLY=( $(compgen -W "$all_opts" -- "$cur") )
            ;;
    esac
}

complete -F _pyv2_complete pyv2
