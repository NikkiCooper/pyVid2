#  blurFilters.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Functions to apply either a Media-Blur or a Gaussian-Blur to a video frame using GPU acceleration if available, or CPU otherwise.
#

import cv2

def median_blur(image, kernel_size=3):
    if not hasattr(median_blur, '_cuda_median_blur_available'):
        median_blur._cuda_median_blur_available = cv2.cuda.getCudaEnabledDeviceCount() > 0
        median_blur._cuda_median_blur_filter = None
        if median_blur._cuda_median_blur_available:
            print("CUDA Median-Blur Filter initialized")
        else:
            print("CUDA Median-Blur Filter not available\nFalling back to CPU")

    if median_blur._cuda_median_blur_available:
        try:
            # Create filter only once
            if median_blur._cuda_median_blur_filter is None:
                median_blur._cuda_median_blur_filter = cv2.cuda.createMedianFilter(cv2.CV_8UC3, kernel_size)

            gpu_image = cv2.cuda_GpuMat()
            gpu_image.upload(image)

            result = median_blur._cuda_median_blur_filter.apply(gpu_image)
            return result.download()

        except cv2.error:
            # Fallback to CPU if CUDA fails
            median_blur._cuda_median_blur_available = False
            print("CUDA failed, falling back to CPU")
            return cv2.medianBlur(image, 5)

    return cv2.medianBlur(image, 5)

def gaussian_blur(frame, kernel_size=(5, 5), sigma_X=0):
    """
    Apply Gaussian Blur to an image frame with CUDA acceleration if available.

    Args:
        frame: The input image frame to be blurred.
        kernel_size (tuple[int, int], optional): The size of the Gaussian kernel.
            Default is (5, 5).

    Returns:
        numpy.ndarray: The blurred image.
    """
    # Initialize class variables if they don't exist
    if not hasattr(gaussian_blur, '_cuda_blur_available'):
        gaussian_blur._cuda_blur_available = cv2.cuda.getCudaEnabledDeviceCount() > 0
        gaussian_blur._cuda_blur_filter = None
        if gaussian_blur._cuda_blur_available:
            print("CUDA Gaussian Filter initialized")

    if gaussian_blur._cuda_blur_available:
        try:
            # Create filter only once
            if gaussian_blur._cuda_blur_filter is None:
                gaussian_blur._cuda_blur_filter = cv2.cuda.createGaussianFilter(
                    cv2.CV_8UC3, cv2.CV_8UC3, kernel_size, sigma1=sigma_X
                )

            gpu_frame = cv2.cuda_GpuMat()
            gpu_frame.upload(frame)
            result = gaussian_blur._cuda_blur_filter.apply(gpu_frame)
            return result.download()

        except cv2.error:
            # Fallback to CPU if CUDA fails
            gaussian_blur._cuda_blur_available = False
            print("CUDA failed, falling back to CPU")
            return cv2.GaussianBlur(frame, kernel_size, sigmaX=sigma_X)

    return cv2.GaussianBlur(frame, kernel_size, sigmaX=sigma_X)
