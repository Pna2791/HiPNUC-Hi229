import pygame
import numpy as np
import sys
from hipnuc_module import Hipnuc_module
import time
import numpy as np
import sys, torch
from datetime import datetime
from fairmotion.ops import conversions

class IMUSet:
    def __init__(self, port='COM6', baud=460800):
        path = 'config_wireless.json'
        
        self.sensor_wireless = Hipnuc_module(port, baud, path)
        print(port, 'Config Done!')

        print('='*80)


    def clear(self):
        self.sensor_wireless.module_data_fifo.queue.clear()


    def close(self):
        self.sensor_wireless.close()

    def get_module_data(self):
        data = self.sensor_wireless.get_module_data(1)
        
        id = data['id']
        id = [x[''] for x in id]

        acc = data['acc']
        acc = [np.array([X['X'], X['Y'], X['Z']], dtype=np.float32) for X in acc]

        quat = data['quat']
        quat = [np.array([X['X'], X['Y'], X['Z'], X['W']], dtype=np.float32) for X in quat]

        return (id, acc, quat)


pygame.init()

# Window size
window_width = 400
window_height = 300

# Text lines
array_data = np.array([1.23, 2.34, 3.45])
line1 = str(array_data)
line2 = "IMU is acc with 4 dims"
line3 = "Third line with 3 dims"

# Font settings
font_size = 30  # Larger font size
font_color = (255, 255, 255)  # White

# Create the window
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Centered Text")

# Load font
font = pygame.font.SysFont(None, font_size)

# Get text size
text1_width, text1_height = font.size(line1)
text2_width, text2_height = font.size(line2)
text3_width, text3_height = font.size(line3)

# Calculate the position to center the text
center_x1 = (window_width - text1_width) // 2
center_y1 = (window_height - (text1_height + text2_height + text3_height)) // 2
center_x2 = (window_width - text2_width) // 2
center_y2 = center_y1 + text1_height
center_x3 = (window_width - text3_width) // 2
center_y3 = center_y2 + text2_height

sensors = IMUSet('COM6')
# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sensors.close()
            sys.exit()

    window.fill((0, 0, 0))  # Fill the window with black

    # Render the text
    id, acc, quat = sensors.get_module_data()
    line1 = str(np.round(acc[0], 2))
    line2 = str(np.round(quat[0], 2))
    line3 = str(np.round(conversions.Q2E(quat[0], order='xyz', degrees=True)))
    text_surface1 = font.render(line1, True, font_color)
    text_surface2 = font.render(line2, True, font_color)
    text_surface3 = font.render(line3, True, font_color)

    # Blit the text on the window at the center positions
    window.blit(text_surface1, (center_x1, center_y1))
    window.blit(text_surface2, (center_x2, center_y2))
    window.blit(text_surface3, (center_x3, center_y3))

    pygame.display.update()

