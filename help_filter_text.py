#  help_text.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Help text for the help dialog box
#
# Help text
HELP_TEXT_LEFT = """SIMPLE FILTERS
[ u ] = Sharpening-1 filter
[ ! ] = Laplacian Boost (CUDA)

[ @ ] = Blur filter
[ ( ] = Gaussian-blur filter (CUDA)
[ ) ] = Median-blur filter (CUDA)

[ g ] = Greyscale (CUDA)
[ * ] = Sepia filter (CUDA)
[ k ] = Edge Sobel (CUDA)
[ v ] = Noise filter
[ / ] = Denoise filter
[ $ ] = Embossing filter
[ % ] = Thermal filter



[ , ] = Flip Left-Right
[ . ] = Flip Up-Down
"""

HELP_TEXT_RIGHT = """ENHANCEMENTS
[ ; ] = Contrast enhancement (CUDA)
[ : ] = Neon enhancement
[ ' ] = Vignette enhancement
[ " ] = Pixelate enhancement
[ < ] = Cel-Shading enhancement
[ ^ ] = Dream enhancement
[ & ] = Comic enhancement
[ ` ] = Artistic enhancement

COMPLEX FILTERS
[ c ] = Brightness/Contrast panel
[ E ] = Apply Edge det. (CUDA)
[ e ] = Edge detection panel
[ f ] = CUDA Bilateral filter panel
[ x ] = Cycle thru bilat. flt. presets
[ z ] = Oil Painting panel

  [   = Disable all filters
"""

