#  applyContrastEnhancement.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Function to apply  contrast ehancement to a video frame using GPU acceleration if available, or CPU otherwise.
#
#
import cv2

"""
Function to apply contrast enhancement to a video frame using GPU acceleration if available, or CPU otherwise.

This function uses CUDA for accelerated contrast enhancement when supported. If CUDA is not available
or fails during execution, it falls back to a CPU-based implementation for a simple contrast stretching
operation.

Parameters
----------
image : numpy.ndarray
    Input video frame for which the contrast enhancement needs to be applied.

Returns
-------
numpy.ndarray
    The contrast-enhanced image.

Raises
------
cv2.error
    Raised in case of errors during CUDA-based operations.
"""
def apply_contrast_enhancement(image):
    if not hasattr(apply_contrast_enhancement, '_cuda_contrast_available'):
        apply_contrast_enhancement._cuda_contrast_available = cv2.cuda.getCudaEnabledDeviceCount() > 0
        if apply_contrast_enhancement._cuda_contrast_available:
            print("CUDA Contrast Enhancement initialized")
        else:
            print("CUDA Contrast Enhancement not available\nFalling back to CPU")

    if apply_contrast_enhancement._cuda_contrast_available:
        try:
            # Upload to GPU
            gpu_image = cv2.cuda_GpuMat()
            gpu_image.upload(image)

            # Convert to grayscale for luminance analysis
            gpu_gray = cv2.cuda.cvtColor(gpu_image, cv2.COLOR_BGR2GRAY)
            minVal, maxVal, minLoc, maxLoc  = cv2.cuda.minMaxLoc(gpu_gray)

            if maxVal - minVal > 0:
                # Create lookup table for contrast adjustment
                alpha = 255.0 / (maxVal - minVal)
                beta = -minVal * alpha

                # Apply contrast adjustment using addWeighted
                gpu_result = cv2.cuda.addWeighted(gpu_image, alpha, gpu_image, 0, beta)
                return gpu_result.download()
            return image

        except cv2.error as e:
            # Fallback to CPU if CUDA fails
            apply_contrast_enhancement._cuda_contrast_available = False
            print(f"CUDA failed, falling back to CPU: {str(e)}")
            # Simple contrast stretching on CPU
            min_val = image.min()
            max_val = image.max()
            if max_val - min_val > 0:
                return cv2.convertScaleAbs(image, alpha=255.0 / (max_val - min_val), beta=-min_val * 255.0 / (max_val - min_val))
            return image

    # CPU version - simple contrast stretching
    min_val = image.min()
    max_val = image.max()
    if max_val - min_val > 0:
        return cv2.convertScaleAbs(image, alpha=255.0 / (max_val - min_val), beta=-min_val * 255.0 / (max_val - min_val))
    return image
