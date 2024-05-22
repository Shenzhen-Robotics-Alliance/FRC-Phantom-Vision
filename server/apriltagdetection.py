DETECTION_RESOLUTION = (320, 240)
DETECTION_RATE = 120
STREAMING_RESOLUTION = (320, 240)
FLIP_IMAGE = -1 # 0 for vertical flip, 1 for horizontal flip, -1 for flip both, None for do not flip

# crosshair setting
CROSSHAIR_LENGTH = 30
CROSSHAIR_COLOR = (0, 255, 0)
CROSSHAIR_THICKNESS = 2

import cv2, threading, sys, cameras, math
from time import time, sleep
# import apriltag
import pupil_apriltags as apriltag # for windows
from MathUtils.cameraprofiles import CameraProfile
from MathUtils.LinearAlgebra import *

class AprilTagCamera:
    def __init__(self, portID):
        print(f"<-- creating apriltag camera with port {portID} -->")
        self.camera = cameras.USBCamera(portID, DETECTION_RESOLUTION, FLIP_IMAGE)
        self.detector = None
        if sys.platform.startswith('linux'):
            self.detector = apriltag.Detector(apriltag.DetectorOptions(families='tag36h11', nthreads=1))
        else:
            self.detector = apriltag.Detector(families='tag36h11', nthreads=1)

        self.running = True
        self.frame = cameras.no_result
        self.frame_resized = cameras.no_result
        self.tags = []
        self.detection_results = "<no results yet>"
        self.frame_time_total = 0
        self.frame_time_samplecount = 0
        self.lock = threading.Lock()
        self.detection_thread = threading.Thread(target=self.generate_forever)
        self.portID = portID

    def detect_once(self):
        # print("<-- capturing -->")
        dt = time()
        frame = self.camera.get_image()
        gray = self.camera.get_image_gray()
        print(f"<-- camera {self.portID} pull image from camera time: {int((time() - dt)*1000)} ms", end="; ")

        dt = time()
        self.tags = self.detector.detect(gray)
        print(f"detector time: {int((time() - dt)*1000)} ms", end=", ")
        
        dt = time()
        # mark apriltags and add detection results
        self.detection_results = ""
        for tag in self.tags:
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
            self.detection_results += f"{tag.tag_id} {center[0]} {center[1]} {area}/"

        if self.detection_results=="":
            self.detection_results = "no-rst"

    
        # resize to straming resolution
        self.frame_resized = cv2.resize(frame, STREAMING_RESOLUTION)
        # draw crosshair
        self.frame_center = (STREAMING_RESOLUTION[0] // 2, STREAMING_RESOLUTION[1]//2)
        cv2.line(self.frame_resized, (self.frame_center[0] - CROSSHAIR_LENGTH, self.frame_center[1]), (self.frame_center[0] + CROSSHAIR_LENGTH, self.frame_center[1]), CROSSHAIR_COLOR, CROSSHAIR_THICKNESS)
        cv2.line(self.frame_resized, (self.frame_center[0], self.frame_center[1] - CROSSHAIR_LENGTH), (self.frame_center[0], self.frame_center[1] + CROSSHAIR_LENGTH), CROSSHAIR_COLOR, CROSSHAIR_THICKNESS)

        
        print(f"process result time: {int((time() - dt)*1000)}ms total delay: {(time()-self.camera.previous_frame_time) * 1000}ms-->")

    def generate_forever(self):
        self.camera.start_capture()
        t = time()
        print("generate frames activated")
        while self.running:
            # print("<-- acquiring lock -->")
            self.lock.acquire()
            
            self.detect_once()

            self.lock.release()

            sleep(max(0, 1/CAMERA_FRAMERATE-(time()-t)))
            # sleep(max(0, 0.005-(time()-t)))
            self.frame_time_total += time() - t
            self.frame_time_samplecount += 1
            print((time()-t)*1000)
            t = time()
        self.camera.stop_capture()

    def start_detections(self):
        print("<-- starting apriltag detections... -->")
        self.detection_thread.daemon = True
        self.detection_thread.start()
        print("<-- apriltag detections running... -->")

    def stop_detection(self):
        self.running = False
        self.detection_thread.join()

    def get_frame(self):
        return self.frame_resized

    def get_tags(self):
        return self.tags

    def get_results(self) -> str:
        return self.detection_results + "\n"

    def get_fps(self) -> int:
        if self.frame_time_total == 0:
            return -1
        fps = round(self.frame_time_samplecount / self.frame_time_total)
        self.frame_time_total = 0
        self.frame_time_samplecount = 0
        return fps

apriltag_cameras = [
    AprilTagCamera(0), 
    # AprilTagCamera(0)
]
camera_profiles = [
    CameraProfile(0.0015774, -0.001638, math.radians(30), 0.4, Vector2D([0, 0.35]), Rotation2D(0)), 
    # CameraProfile(0.0019083090502545134, -0.0018938381148259048, math.radians(30), 0.4, Vector2D([0, 0.35]), Rotation2D(math.pi))
]
print("<-- apriltag camera and detector ready -->")