#  edgesSobel.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Function to implement the Sobel edge detection filter using CUDA if available, or CPU otherwise.
#
import cv2
import numpy as np
#
def apply_edges_sobel(image):
    """
    Applies the Sobel edge detection filter using CUDA if available, otherwise CPU.
    """

    if not hasattr(apply_edges_sobel, '_cuda_edges_sobel_detect_available'):
        # pylint: disable=protected-access
        apply_edges_sobel._cuda_edges_sobel_detect_available = cv2.cuda.getCudaEnabledDeviceCount() > 0
        if apply_edges_sobel._cuda_edges_sobel_detect_available:    # pylint: disable=protected-access
            print("CUDA Edges-Sobel-Detection filter initialized")
        else:
            print("CUDA Edges-Sobel-Detection filter not available\nFalling back to CPU")

    if hasattr(apply_edges_sobel, '_cuda_edges_sobel_detect_available'):
        try:
            # Upload to GPU
            gpu_image = cv2.cuda_GpuMat()
            gpu_image.upload(image)
            # Convert to grayscale
            gray_gpu = cv2.cuda.cvtColor(gpu_image, cv2.COLOR_BGR2GRAY)
            try:
                sobel_filter = cv2.cuda.createSobelFilter(cv2.CV_8UC1, cv2.CV_8UC1, 1, 0, ksize=3)
                sobel_gpu = sobel_filter.apply(gray_gpu)
            except cv2.error as e:
                print(f"Failed during Sobel filter creation/application: {str(e)}")
                raise
            # Convert back to BGR
            result_bgr = cv2.cuda.cvtColor(sobel_gpu, cv2.COLOR_GRAY2BGR)
            # Download result
            result = result_bgr.download()
            return result
        # pylint: disable=broad-exception-caught
        except Exception as e:  # pylint: disable=unused-variable
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
            sobel = np.uint8(np.absolute(sobel))
            return cv2.cvtColor(sobel, cv2.COLOR_GRAY2BGR)
    return cv2.cvtColor(sobel, cv2.COLOR_GRAY2BGR)
