CAM_PORT = 1
CAMERA_RESOLUTION = (640, 480)
CAMERA_FRAMERATE = 60
STREAMING_RESOLUTION = (160, 120)
FLIP_IMAGE = -1 # 0 for vertical flip, 1 for horizontal flip, -1 for flip both, None for do not flip

# crosshair setting
CROSSHAIR_LENGTH = 30
CROSSHAIR_COLOR = (0, 255, 0)
CROSSHAIR_THICKNESS = 2

import cv2, threading, sys, cameras, MathUtils.tagdistancecalculator as tagdistancecalculator, fieldnavigation
import numpy as np
from time import time, sleep
# import apriltag
import pupil_apriltags as apriltag # for windows

print("<-- creating apriltag camera -->")
camera = cameras.USBCamera(CAM_PORT, CAMERA_RESOLUTION, CAMERA_FRAMERATE, FLIP_IMAGE)
detector = None
if sys.platform.startswith('linux'):
    detector = apriltag.Detector(apriltag.DetectorOptions(families='tag36h11', nthreads=1))
else:
    detector = apriltag.Detector(families='tag36h11', nthreads=1)
print("<-- apriltag camera and detector ready -->")

running = True
frame = cameras.no_result
frame_resized = cameras.no_result
tags = []
detection_results = "<no results yet>"
frame_time_total = 0
frame_time_samplecount = 0
lock = threading.Lock()

def detect_once():
    global frame, frame_resized, frame_time_total, frame_time_samplecount, tags, detection_results
    # print("<-- capturing -->")
    dt = time()
    frame = camera.get_image()
    gray = camera.get_image_gray()
    # print("<-- pull image from camera time: " + str(int((time() - dt)*1000)) + "ms", end="; ")

    dt = time()
    tags = detector.detect(gray)
    # print("detector time: " + str(int((time() - dt)*1000)) + "ms", end=", ")
    
    dt = time()
    # mark apriltags and add detection results
    detection_results = ""
    for tag in tags:
        corners_pos = []
        left = top = float("inf")
        right = bottom = 0
        for corner in tag.corners:
            corner_pos = tuple(corner.astype(int))
            corners_pos.append(corner_pos)
            left = min(corner_pos[0], left)
            top = min(corner_pos[1], top)
            right = max(corner_pos[0], right)
            bottom = max(corner_pos[1], bottom)
            cv2.circle(frame, corners_pos[-1], 4, (255,0,0), 2)
            
        for side in range(4):
            cv2.line(frame, corners_pos[side-1], corners_pos[side], (0, 255, 0), 3)
        center = tag.center

        # print("tag center: ", tag.center)
        
        # print(f"<-- tag {tag.tag_id} have realtive position {tagdistancecalculator.get_relative_position_to_robot(40, tag.center[0]-CAMERA_RESOLUTION[0]/2, tag.center[1]-CAMERA_RESOLUTION[1]/2)}")

        area = (right - left) * (bottom - top)
        cv2.putText(frame, f"{tag.tag_id}", (int(center[0]-40), int(center[1])), cv2.FONT_HERSHEY_COMPLEX, 2.0, (100,200,200), 5)
        # detection_results += f"\n{tag.tag_id} {center[0]} {center[1]} {corners_pos[0][0]} {corners_pos[0][1]} {corners_pos[1][0]} {corners_pos[1][1]} {corners_pos[2][0]} {corners_pos[2][1]} {corners_pos[3][0]} {corners_pos[3][1]}"
        detection_results += f"{tag.tag_id} {center[0]} {center[1]} {area}/"

    if detection_results=="":
        detection_results = "no-rst"

   
    # resize to straming resolution
    frame_resized = cv2.resize(frame, STREAMING_RESOLUTION)
    # draw crosshair
    frame_center = (STREAMING_RESOLUTION[0] // 2, STREAMING_RESOLUTION[1]//2)
    cv2.line(frame_resized, (frame_center[0] - CROSSHAIR_LENGTH, frame_center[1]), (frame_center[0] + CROSSHAIR_LENGTH, frame_center[1]), CROSSHAIR_COLOR, CROSSHAIR_THICKNESS)
    cv2.line(frame_resized, (frame_center[0], frame_center[1] - CROSSHAIR_LENGTH), (frame_center[0], frame_center[1] + CROSSHAIR_LENGTH), CROSSHAIR_COLOR, CROSSHAIR_THICKNESS)

    
    # print("process result time: " + str(int((time() - dt)*1000)) + "ms -->")

def generate_forever():
    camera.start_capture()
    global frame_time_total, frame_time_samplecount, lock
    t = time()
    print("generate frames activated")
    while running:
        # print("<-- acquiring lock -->")
        lock.acquire()
        
        detect_once()

        lock.release()

        sleep(max(0, 1/CAMERA_FRAMERATE-0.001-(time()-t)))
        frame_time_total += time() - t
        frame_time_samplecount += 1
        t = time()
    camera.stop_capture()


detection_thread = threading.Thread(target=generate_forever)
def start_detections():
    print("<-- starting apriltag detections... -->")
    detection_thread.daemon = True
    detection_thread.start()
    print("<-- apriltag detections running... -->")

def stop_detection():
    global running
    running = False
    detection_thread.join()

def get_frame():
    return frame_resized

def get_tags():
    return tags

def get_results() -> str:
    return detection_results + "\n"

def get_fps() -> int:
    global frame_time_total, frame_time_samplecount
    if frame_time_total == 0:
        return -1
    fps = round(frame_time_samplecount / frame_time_total)
    frame_time_total = 0
    frame_time_samplecount = 0
    return fps
