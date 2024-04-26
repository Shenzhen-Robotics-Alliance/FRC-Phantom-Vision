import math

first_col_height = 4-2
spacing = 3.5
camera_pitch = math.radians(30)

top_left = (-spacing * 3.5, first_col_height + spacing * 4)

tag_pos = [None]
for row in range(8):
    for col in range(5):
        tag_pos.append((top_left[0] + row * spacing, top_left[1] - col * spacing))
        print(tag_pos[-1])

import apriltagdetection, cv2

apriltagdetection.STREAMING_RESOLUTION = (1024, 768)
apriltagdetection.start_detections()

i = 0
horizontal_ratios_samples, vertical_ratios_samples, pixel_x_samples, pixel_y_samples = [], [], [], []
try:
    while True:
        print("<-- please aim the camera at row", i , " (counting from button to top) -->")
        frame = apriltagdetection.get_frame()
        cv2.imshow('Camera Calibration', frame)

        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            print("<-- esc pressed, exiting... -->")
            break
        elif key == ord('s'):
            camera_distance_to_paper = (first_col_height + i * spacing) / math.sin(camera_pitch)
            tags = apriltagdetection.get_tags()
            print("<-- results detected: ", end="")
            for tag in tags:
                print(f"id {tag.tag_id} center {tag.center}", end="; ")

                projection_surface_distance = math.cos(camera_pitch) * (camera_distance_to_paper + tag_pos[tag.tag_id][1] * math.tan(camera_pitch))
                tag_pitch = math.atan(tag_pos[tag.tag_id][1] / camera_distance_to_paper)
                vertical_ratios_samples.append(math.tan(tag_pitch-camera_pitch))
                horizontal_ratios_samples.append(tag_pos[tag.tag_id][0] / projection_surface_distance)
                
                pixel_x_samples.append(tag.center[0] - apriltagdetection.CAMERA_RESOLUTION[0]/2)
                pixel_y_samples.append(tag.center[1] - apriltagdetection.CAMERA_RESOLUTION[1]/2)
                
            print(" -->")
            cv2.putText(frame, "FRAME CAPTURED", (30,200), cv2.FONT_HERSHEY_COMPLEX, 3, (0, 0, 255), 1)
            cv2.imshow('Camera Calibration', frame)
            cv2.waitKey(1000)

            i += 1
            if i == 4:
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
vertical_ratios_samples = np.array(vertical_ratios_samples)
pixel_x_samples = np.array(pixel_x_samples)
pixel_y_samples = np.array(pixel_y_samples)

def regression_line(x_samples, y_samples, title, x_label, y_label):
    # Calculate regression coefficients
    slope, intercept, rvalue, _, _ = linregress(x_samples, y_samples)

    # Construct the regression line
    x_values = np.linspace(min(pixel_x_samples), max(pixel_x_samples), 100)
    y_values = slope * x_values + intercept
    
    # Plot the data points and regression line
    plt.clf()
    plt.scatter(x_samples, y_samples, label='Camera Pixel')
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
regression_line(pixel_y_samples, vertical_ratios_samples, "Camera Vertical Param", "Pixel Y", "(Vertical Displacement / Distance) Ratio")

'''
<-- Horizontal Params: -->
Projection Ratio=0.0019083090502545134, Bias=0.0005214582385315181
R^2: 0.999817916421933
<-- Vertical Params: -->
Projection Ratio=-0.0018938381148259048, Bias=-0.011943913024578173
R^2: 0.9965217801193813
WARINING!!! results not trustable!
'''