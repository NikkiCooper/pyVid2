#!/bin/bash

#
# pyVid2 installation script.
# Run this script under the user pyVid2 will be run under.
# Run this script from the directory it is located in.
#
fonts_src_path="`pwd`/fonts/"
fonts_dest_path="$HOME/.local/share/pyVid/fonts"

echo "PyVid2 installation script"
if [ ! -d "$fonts_dest_path" ]; then
  echo "Creating: ${fonts_dest_path}"
  mkdir -p  "$fonts_dest_path"
  rc=$?
  if [[ $rc -ne 0 ]]; then
    echo "${fonts_dest_path} could not be created for some reason."
    echo "The return code received was: ${rc}"
    echo 'Investigate why and try again.'
    exit 10
  fi
fi
if [ ! -d "${fonts_src_path}" ]; then
  echo "The source fonts directory ${fonts_src_path} not found."
  echo 'Ensure this script is run from the PyVid2 installation root directory'
  exit 20
fi
cd "${fonts_src_path}"
cp -a * -t "${fonts_dest_path}"
rc=$?
if [ $rc -ne 0 ]; then
  echo "Could not copy fonts from ${fonts_src_path} to ${fonts_dest_path}"
  echo "The return code received was: ${rc}"
  exit 30
fi

echo 'Installation successful!  Enjoy :-)'




