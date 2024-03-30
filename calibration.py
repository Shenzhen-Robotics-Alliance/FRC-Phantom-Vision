first_col_height = 4
spacing = 3.5
camera_distance_to_paper = 30

top_left = (-spacing * 3.5, first_col_height + spacing * 4)

tag_pos = []
for col in range(5):
    for row in range(8):
        tag_pos.append((top_left[0] + col * spacing, top_left[1] - row * spacing))
        print(tag_pos[-1])

import apriltagdetection

apriltagdetection.detect_once()

for i 