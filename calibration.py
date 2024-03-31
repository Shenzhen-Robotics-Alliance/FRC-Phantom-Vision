first_col_height = 4
spacing = 3.5
camera_distances_to_paper = [20, 30, 40, 50]

top_left = (-spacing * 3.5, first_col_height + spacing * 4)

tag_pos = []
for col in range(5):
    for row in range(8):
        tag_pos.append((top_left[0] + col * spacing, top_left[1] - row * spacing))
        print(tag_pos[-1])

import apriltagdetection, cv2
from time import time, sleep

apriltagdetection.STREAMING_RESOLUTION = (1280, 720)
apriltagdetection.start_detections()

i = 0
horizontal_ratios_samples, vertical_ratios_samples, pixel_x_samples, pixel_y_samples = [], [], [], []
try:
    while True:
        print("<-- please put the paper", camera_distances_to_paper[i] , "cm away from camera -->")
        frame = apriltagdetection.get_frame()
        cv2.imshow('Camera Calibration', frame)

        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            print("<-- esc pressed, exiting... -->")
            break
        elif key == ord('s'):
            tags = apriltagdetection.get_tags()
            print("<-- results detected: ", end="")
            for tag in tags:
                print(f"id {tag.tag_id} center {tag.center}", end="; ")
                horizontal_ratios_samples.append(tag_pos[tag.tag_id][0] - apriltagdetection.CAMERA_RESOLUTION[0]/2 / camera_distances_to_paper[i])
                vertical_ratios_samples.append(tag_pos[tag.tag_id][1] - apriltagdetection.CAMERA_RESOLUTION[1]/2 / camera_distances_to_paper[i])
                pixel_x_samples.append(tag.center[0])
                pixel_y_samples.append(tag.center[1])
                
            print(" -->")
            cv2.putText(frame, "FRAME CAPTURED", (30,200), cv2.FONT_HERSHEY_COMPLEX, 3, (0, 0, 255), 1)
            cv2.imshow('Camera Calibration', frame)
            cv2.waitKey(1000)

            i += 1
            if i == len(camera_distances_to_paper):
                break
except KeyboardInterrupt:
    print("<-- interrupted by user -->")
    pass

cv2.destroyAllWindows()
apriltagdetection.stop_detection()


# use least-square regression line to find camera param

import numpy as np
from scipy.stats import linregress
import matplotlib.pyplot as plt
horizontal_ratios_samples = np.array(horizontal_ratios_samples)
vertical_ratios_samples = np.array(horizontal_ratios_samples)
pixel_x_samples = np.array(pixel_x_samples)
pixel_y_samples = np.array(pixel_y_samples)

def regression_line(x_samples, y_samples, title, x_label, y_label):
    # Calculate regression coefficients
    slope, intercept, rvalue, _, _ = linregress(x_samples, y_samples)

    # Construct the regression line
    x_values = np.linspace(min(pixel_x_samples), max(pixel_x_samples), 100)
    y_values = slope * x_values + intercept
    
    # Plot the data points and regression line
    plt.scatter(pixel_x_samples, horizontal_ratios_samples, label='Camera Pixel')
    plt.plot(x_values, y_values, color='red', label='Regression Line')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()

    print(f"Projection Ratio={slope}, Bias={intercept}")
    print(f"R^2: {rvalue ** 2}")

    if rvalue**2 < 0.998:
        print("WARINING!!! results not trustable!")
print("<-- Horizontal Params: -->")
regression_line(pixel_x_samples, horizontal_ratios_samples, "Camera Horizontal Param", "Pixel X", "(Horizontal Displacement / Distance) Ratio")
print("<-- Vertical Params: -->")
regression_line(pixel_y_samples, vertical_ratios_samples, "Camera Horizontal Param", "Pixel Y", "(Vertical Displacement / Distance) Ratio")