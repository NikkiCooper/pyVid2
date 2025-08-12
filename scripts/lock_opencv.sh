#!/bin/bash

# =============================================================================
# 📦 Dummy OpenCV Lock Script
#
# Prevent pip from upgrading or reinstalling manually compiled CUDA-enabled
# versions of opencv-python and opencv-contrib-python by installing dummy
# packages with matching versions.
#
# ✅ Requirements:
#   - This script must be run inside an activated Python virtual environment.
#   - The correct versions of both packages must already be installed.
#
# 💡 Usage:
#   ./lock_opencv.sh 4.13.0-dev
#
# If no version string is passed, the script will explain what to do and exit.
# =============================================================================

# — Check for a version string —
if [[ -z "$1" ]]; then
    echo "❌ ERROR: No version string provided."
    echo "🔧 Usage: $0 <version-string>    e.g.,  $0 4.13.0-dev"
    echo
    echo "💬 This script installs dummy packages to lock opencv version in pip."
    echo "💬 Prevents pip from upgrading or reinstalling manually compiled CUDA-enabled"
    echo "💬 versions of opencv-python and opencv-contrib-python by installing dummy"
    echo "💬 packages with matching versions."
    echo
    echo "✅ Requirements:"
    echo "  - This script must be run inside an activated Python virtual environment."
    echo "  - The correct versions of both packages must already be installed in said virtual environment."
    exit 1
fi

# Extract version from argument
OPENCV_VERSION="$1"

# Create a temp directory under /tmp and ensure cleanup on exit
TEMP_DIR=$(mktemp -d -t dummy_opencv-XXXX)
trap "rm -rf $TEMP_DIR" EXIT
cd "$TEMP_DIR" || exit 1

# 🔧 Create and install dummy opencv-contrib-python
cat > setup.py <<EOF
from setuptools import setup
setup(
    name="opencv-contrib-python",
    version="$OPENCV_VERSION",
    description="Dummy package to satisfy pip dependency",
    packages=[],
)
EOF

pip install .

# 🔧 Create and install dummy opencv-python
cat > setup.py <<EOF
from setuptools import setup
setup(
    name="opencv-python",
    version="$OPENCV_VERSION",
    description="Dummy package to satisfy pip dependency",
    packages=[],
)
EOF

pip install .
