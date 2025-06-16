#  edgeDetectPanel.py Copyright (c) 2025 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
# Class to display a control panel for adjusting --edge-Upper and edge-Lower-- values for use with --edge-detect.

import pygame
import numpy as np

DODGERBLUE = (30, 144, 255)
DODGERBLUE4 = (16, 78, 139)
WHITE = (255, 255, 255)

class edgeDetectPanel:
	def __init__(self, screen_width, screen_height, play_video=None):
		"""Initialize the panel with edge-Upper and edge-Lower controls"""
		# Panel dimensions and position
		self.panel_height = int(screen_height * 0.12)  # 15% of screen height
		self.panel_width = int(screen_width * 0.3)  # 30% of screen width
		self.panel_x = screen_width - self.panel_width - 20  # 20px padding from right
		self.panel_y = 20  # 20px from top

		# Store reference to PlayVideo instance
		self.play_video = play_video

		# Create the panel surface with an alpha channel
		self.surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
		self.rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
		self.surface.set_colorkey((0, 255, 0))
		pygame.draw.rect(
			self.surface,
			DODGERBLUE,
			(0, 0, self.panel_width, self.panel_height),
			1,
			border_radius=8
		)

		play_video.apply_gradient(self.surface,
		                         (0, 0, 200),
		                         (0, 0, 100),
		                         self.panel_width,
		                         self.panel_height,
		                         alpha_start=100,
		                         alpha_end=200
		                         )
		pygame.draw.rect(
			self.surface,
			DODGERBLUE,
			(0, 0, self.panel_width, self.panel_height),
			1,
			border_radius=8
		)


		# Slider dimensions
		slider_width = int(self.panel_width * 0.8)
		slider_height = 10
		slider_x = int((self.panel_width - slider_width) / 2)

		# Initialize sliders
		self.edge_upper_slider = {
			'rect': pygame.Rect(slider_x, 30, slider_width, slider_height),
			'knob': pygame.Rect(slider_x + slider_width // 2, 25, 20, 20),
			'value': 0,
			'dragging': False
		}

		self.edge_lower_slider = {
			'rect': pygame.Rect(slider_x, 80, slider_width, slider_height),
			'knob': pygame.Rect(slider_x + slider_width // 2, 75, 20, 20),
			'value': 0,
			'dragging': False
		}

		# Button rectangle
		self.reset_button_rect = None

		# Effect values
		self.edge_upper_level = 200
		self.edge_lower_level = 100
		#self.play_video.opts.edge_upper = self.edge_upper_level
		#self.play_video.opts.edge_lower = self.edge_lower_level
		#self.play_video.opts.edge_detect = True

		# State
		self.is_visible = False
		self.active_slider = None

	def draw(self, screen):
		"""Draw the control panel and its components"""
		if not self.is_visible:
			return

		# Draw the panel background
		screen.blit(self.surface, self.rect)

		# Draw sliders
		for slider, label, value_range in [
			(self.edge_upper_slider, "Edge Upper", (0, 255)),
			(self.edge_lower_slider, "Edge Lower", (0, 127))
		]:
			# Draw slider background
			pygame.draw.rect(screen, (100, 100, 100),
			                 (self.rect.x + slider['rect'].x,
			                  self.rect.y + slider['rect'].y,
			                  slider['rect'].width,
			                  slider['rect'].height))

			# Draw slider knob
			pygame.draw.rect(screen, DODGERBLUE4,
			                 (self.rect.x + slider['knob'].x,
			                  self.rect.y + slider['knob'].y,
			                  slider['knob'].width,
			                  slider['knob'].height))
			pygame.draw.rect(screen, DODGERBLUE,
			                 (self.rect.x + slider['knob'].x,
			                  self.rect.y + slider['knob'].y,
			                  slider['knob'].width,
			                  slider['knob'].height),2, border_radius=5)

			# Draw label and value
			font = pygame.font.Font(None, 24)
			label_text = font.render(f"{label}: {slider['value']}", True, DODGERBLUE)
			screen.blit(label_text,
			            (self.rect.x + slider['rect'].x,
			             self.rect.y + slider['rect'].y - 20))

		# Draw the reset button
		reset_button_rect = pygame.Rect(
			self.rect.x + self.panel_width // 2 - 40,
			self.rect.y + self.panel_height - 100,
			120, 45)


		pygame.draw.rect(screen, DODGERBLUE, reset_button_rect, border_radius=10)
		pygame.draw.rect(screen, DODGERBLUE4, reset_button_rect, 1, border_radius=10)

		reset_text = pygame.font.Font(None, 36).render("Reset", True, (255, 255, 255))
		screen.blit(reset_text, (reset_button_rect.x + 25, reset_button_rect.y + 12))

		# Store the button rect for hit testing
		self.reset_button_rect = reset_button_rect

	def handle_mouse_button_down(self, pos):
		"""Handle mouse button down event"""
		if not self.is_visible:
			return False

		relative_pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)

		# Check edge_upper slider
		if self.edge_upper_slider['knob'].collidepoint(relative_pos):
			self.active_slider = 'brightness'
			self.edge_upper_slider['dragging'] = True
			return True

		# Check edge_lower slider
		if self.edge_lower_slider['knob'].collidepoint(relative_pos):
			self.active_slider = 'edge-Lower'
			self.edge_lower_slider['dragging'] = True
			return True

		'''
		# Check if reset button was clicked
		if hasattr(self, 'reset_button_rect') and self.reset_button_rect.collidepoint(pos):
			self.reset_effects()
			return True
		'''
		return False

	def handle_mouse_button_up(self):
		"""Handle mouse button up event"""
		if self.active_slider:
			if self.active_slider == 'edge-Upper':
				self.edge_upper_slider['dragging'] = False
			else:
				self.edge_lower_slider['dragging'] = False
			self.active_slider = None

	def handle_mouse_motion(self, pos):
		"""Handle mouse motion for slider movement"""
		if not self.active_slider:
			return False

		relative_x = pos[0] - self.rect.x
		slider = (self.edge_upper_slider if self.active_slider == 'edge-Upper' else self.edge_lower_slider)

		# Calculate new position within bounds
		new_x = max(slider['rect'].left,
		            min(relative_x - slider['knob'].width / 2,
		                slider['rect'].right - slider['knob'].width))
		slider['knob'].x = new_x

		# Calculate value based on position
		value_range = (0, 255) if self.active_slider == 'edge-Upper' else (-127, 127)
		range_min, range_max = value_range
		pos_ratio = (new_x - slider['rect'].left) / (slider['rect'].width - slider['knob'].width)
		new_value = int(range_min + (range_max - range_min) * pos_ratio)

		# Only update if value changed
		if slider['value'] != new_value:
			slider['value'] = new_value
			if self.active_slider == 'edge-Upper':
				self.edge_upper_level = slider['value']
				# Update PlayVideo's opts.brightness if PlayVideo instance is available
				if self.play_video and hasattr(self.play_video, 'opts'):
					self.play_video.opts.edge_upper = self.edge_upper_level
					self.play_video.opts.adjust_video = True
					self.play_video.update_video_effects()
			else:
				self.edge_lower_level = 1 + (slider['value'] / 64.0)
				# Update PlayVideo's opts.edge_lower if PlayVideo instance is available
				if self.play_video and hasattr(self.play_video, 'opts'):
					# Convert our edge_lower value to the range expected by the video processor
					self.play_video.opts.edge_lower = slider['value']
					self.play_video.opts.edge_detect = True
					self.play_video.update_video_effects()

		return True

	def apply_effects(self, surface):

		edges = cv2.Canny(surface, 100, 200)
		return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

	def toggle_visibility(self):
		"""Toggle the control panel visibility"""
		self.is_visible = not self.is_visible

	def reset_effects(self):
		"""Reset both sliders to default positions"""
		# Reset brightness slider
		self.edge_upper_slider['knob'].x = self.edge_upper_slider['rect'].left + self.edge_uppser_slider['rect'].width // 2
		self.edge_upper_slider['value'] = 0
		self.edge_upper_level = 0

		# Reset edge_lower slider
		self.edge_lower_slider['knob'].x = self.edge_lower_slider['rect'].left + self.edge_lower_slider['rect'].width // 2
		self.edge_lower_slider['value'] = 0
		self.edge_lower_level = 1.0

		# Turn off video adjustment if both are at default values
		if self.play_video and hasattr(self.play_video, 'opts'):
			self.play_video.opts.edge_upper = 0
			self.play_video.opts.edge_lower = 0
			self.play_video.opts.edge_detect = False
			self.play_video.update_video_effects()

