#  greyScale.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Function to apply greyscale to a video frame using GPU acceleration if available, or CPU otherwise.
#
#
import cv2

def greyscale(image):
    """Convert image to grayscale, maintaining 3-channel format for PyGame compatibility"""
    if not hasattr(greyscale, '_cuda_grey_available'):
        greyscale._cuda_grey_available = cv2.cuda.getCudaEnabledDeviceCount() > 0
        if greyscale._cuda_grey_available:
            # print(" CUDA Grayscale conversion available")
            print("Using CUDA grayscale filter")
        else:
            print("CUDA grayscale filter not available\nFalling back to CPU")
    try:
        if greyscale._cuda_grey_available:
            gpu_frame = cv2.cuda_GpuMat()
            gpu_frame.upload(image)
            gray_gpu = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2GRAY)
            # Convert back to 3 channels using CUDA
            gray_3ch = cv2.cuda.cvtColor(gray_gpu, cv2.COLOR_GRAY2BGR)
            return gray_3ch.download()

        # CPU fallback
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    except cv2.error:
        greyscale._cuda_grey_available = False
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
