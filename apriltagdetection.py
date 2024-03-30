CAM_PORT = 1
CAMERA_RESOLUTION = (640, 480)
CAMERA_FRAMERATE = 120
STREAMING_RESOLUTION = (160, 120)
FLIP_IMAGE = None # 0 for vertical flip, 1 for horizontal flip, -1 for flip both, None for do not flip
server_port = 8888

import cv2, threading, sys, cameras
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
frame = None
tags = None
detection_results = "<no results yet>"
frame_time_total = 0
frame_time_samplecount = 0
lock = threading.Lock()

def detect_once():
    global frame, frame_time_total, frame_time_samplecount, tags, detection_results
    # print("<-- capturing -->")
    dt = time()
    frame = camera.get_image()
    gray = camera.get_image_gray()
    if frame is None:
        return
    print("<-- pull image from camera time: " + str(int((time() - dt)*1000)) + "ms", end="; ")

    dt = time()
    tags = detector.detect(gray)
    print("detector time: " + str(int((time() - dt)*1000)) + "ms", end=", ")

    dt = time()
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
        area = (right - left) * (bottom - top)
        cv2.putText(frame, f"{tag.tag_id}", (int(center[0]-40), int(center[1])), cv2.FONT_HERSHEY_COMPLEX, 2.0, (100,200,200), 5)
        # detection_results += f"\n{tag.tag_id} {center[0]} {center[1]} {corners_pos[0][0]} {corners_pos[0][1]} {corners_pos[1][0]} {corners_pos[1][1]} {corners_pos[2][0]} {corners_pos[2][1]} {corners_pos[3][0]} {corners_pos[3][1]}"
        detection_results += f"{tag.tag_id} {center[0]} {center[1]} {area}/"
    if detection_results=="":
        detection_results = "no-rst"
    
    print("process result time: " + str(int((time() - dt)*1000)) + "ms -->")

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
    detection_thread.daemon = True
    detection_thread.start()

def stop_detection():
    global running
    running = False
    detection_thread.join()

def get_frame():
    lock.acquire()
    frame_resized = cv2.resize(frame, STREAMING_RESOLUTION)
    lock.release()
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
