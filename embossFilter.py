#  embossFilter.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Function to apply the emboss effect to a video frame using GPU acceleration if available, or CPU otherwise.


import cv2
import numpy as np


def cuda_emboss(frame):
    """
    Applies the Emboss filter using CUDA acceleration if available.
    Creates a 3D effect by emphasizing directional edges.
    """
    if not hasattr(cuda_emboss, '_cuda_available'):
        cuda_emboss._cuda_available = cv2.cuda.getCudaEnabledDeviceCount() > 0
        cuda_emboss._filter = None
        if cuda_emboss._cuda_available:
            print("CUDA Emboss Filter initialized")
            # Create the emboss kernel
            kernel = np.array([[-2, -1, 0],
                               [-1, 1, 1],
                               [0, 1, 2]], dtype=np.float32)
            # Create filter once and cache it
            cuda_emboss._filter = cv2.cuda.createLinearFilter(
                cv2.CV_8UC1,  # srcType - single channel
                cv2.CV_8UC1,  # dstType - single channel
                kernel  # kernel matrix
            )
        else:
            print("CUDA Emboss Filter not available\nFalling back to CPU")

    if cuda_emboss._cuda_available:
        try:
            # Upload image to GPU
            gpu_frame = cv2.cuda_GpuMat()
            gpu_frame.upload(frame)

            # Convert to grayscale
            gpu_gray = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2GRAY)

            # Apply emboss filter
            filtered = cuda_emboss._filter.apply(gpu_gray)

            # Convert back to BGR
            filtered_bgr = cv2.cuda.cvtColor(filtered, cv2.COLOR_GRAY2BGR)

            # Create offset matrix same size as filtered_bgr
            h, w = frame.shape[:2]
            offset = cv2.cuda_GpuMat()
            offset.upload(np.full((h, w, 3), 128, dtype=np.uint8))

            # Add offset using addWeighted
            result = cv2.cuda.addWeighted(filtered_bgr, 1.0, offset, 1.0, 0.0)

            return result.download()

        except cv2.error as e:
            print(f"CUDA operation failed, falling back to CPU: {str(e)}")
            # Fallback to CPU version
            kernel = np.array([[-2, -1, 0],
                               [-1, 1, 1],
                               [0, 1, 2]])
            return cv2.filter2D(frame, -1, kernel) + 128

    # CPU version
    kernel = np.array([[-2, -1, 0],
                       [-1, 1, 1],
                       [0, 1, 2]])
    return cv2.filter2D(frame, -1, kernel) + 128