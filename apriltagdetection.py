CAM_PORT = 0
CAMERA_RESOLUTION = (640, 480)
CAMERA_FRAMERATE = 60
STREAMING_RESOLUTION = (160, 120)
FLIP_IMAGE = -1 # 0 for vertical flip, 1 for horizontal flip, -1 for flip both, None for do not flip
server_port = 8888

import cv2
import numpy as np
from time import time, sleep
# import apriltag
import pupil_apriltags as apriltag # for windows
import threading

# cap = cv2.VideoCapture(CAM_PORT, cv2.CAP_V4L2) # camera port 0 for linux
cap = cv2.VideoCapture(CAM_PORT) # camera port 0 for windows
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J','P','G'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_RESOLUTION[0]) # width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_RESOLUTION[1]) # height
cap.set(cv2.CAP_PROP_FPS, CAMERA_FRAMERATE) 
# detector = apriltag.Detector(apriltag.DetectorOptions(families='tag36h11', nthreads=1))
detector = apriltag.Detector(families='tag36h11', nthreads=1) # for windows
print("<-- camera and detector ready -->")

running = True
frame = None
detection_results = "<no results yet>"
frame_time_total = 0
frame_time_samplecount = 0
lock = threading.Lock()

def generate_frames():
    global frame, frame_time_total, frame_time_samplecount, detection_results, lock
    t = time()
    print("generate frames activated")
    while running:
        dt = time()
        print("<-- acquiring lock -->")
        lock.acquire()
        print("<-- capturing -->")
        ret, frame = cap.read()
        if frame is None:
            continue
        print("<-- capture time: " + str(int((time() - dt)*1000)) + "ms", end="; ")
        
        dt = time()
        if FLIP_IMAGE is not None:
            frame = cv2.flip(frame, FLIP_IMAGE)
        print("flip time: " + str(int((time() - dt)*1000)) + "ms", end="; ")

        dt = time()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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
            center = ((corners_pos[0][0] + corners_pos[1][0] + corners_pos[2][0] + corners_pos[3][0]) / 4, (corners_pos[0][1] + corners_pos[1][1] + corners_pos[2][1] + corners_pos[3][1]) / 4)
            area = (right - left) * (bottom - top) # TODO improve this algorithm
            # print(f"id: {tag.tag_id}, center: {center}, area: {area}")
            cv2.putText(frame, f"tag id{tag.tag_id}", (int(center[0]-120), int(center[1])), cv2.FONT_HERSHEY_COMPLEX, 2.0, (100,200,200), 5)
            # detection_results += f"\n{tag.tag_id} {center[0]} {center[1]} {corners_pos[0][0]} {corners_pos[0][1]} {corners_pos[1][0]} {corners_pos[1][1]} {corners_pos[2][0]} {corners_pos[2][1]} {corners_pos[3][0]} {corners_pos[3][1]}"
            detection_results += f"{tag.tag_id} {center[0]} {center[1]} {area}/"
        if detection_results=="":
            detection_results = "no-rst"
        
        lock.release()
        print("process result time: " + str(int((time() - dt)*1000)) + "ms -->")

        detection_results += "\n"
        frame_time_total += time()-t
        frame_time_samplecount += 1
        t = time()

        # Convert the frame to bytes
        new_frame_ready = True
        detection_results_ready = True

def generate_forever():
    try:
        generate_frames()
    except KeyboardInterrupt:
        lock.release()


detection_thread = threading.Thread(target=generate_forever)
def start_detections():
    detection_thread.daemon = True
    detection_thread.start()

def get_frame():
    lock.acquire()
    frame_resized = cv2.resize(frame, STREAMING_RESOLUTION)
    lock.release()
    return frame_resized

def get_results() -> str:
    detection_results

def get_fps() -> int:
    global frame_time_total, frame_time_samplecount
    if frame_time_total == 0:
        return -1
    fps = round(frame_time_samplecount / frame_time_total)
    frame_time_total = 0
    frame_time_samplecount = 0
    return fps