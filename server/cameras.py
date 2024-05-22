import cv2, sys, threading, os
from time import time, sleep

SERVER_ROOT = os.path.split(os.path.realpath(__file__))[0]
no_result = cv2.imread(os.path.join(SERVER_ROOT, "./webpages/no_result.png"))

CAM_RES = (640, 480)
CAM_FPS = 60
class USBCamera:
    def __init__(self, portID:int, resolution:tuple, flip_code):
        if sys.platform.startswith('linux'):
            self.cap = cv2.VideoCapture(portID, cv2.CAP_V4L2)
        else:
            self.cap = cv2.VideoCapture(portID)

        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J','P','G'))
        self.resolution = resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_RES[0]) # width
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_RES[1]) # height
        self.cap.set(cv2.CAP_PROP_FPS, CAM_FPS) 
        self.flip_code = flip_code

        self.image = no_result
        self.image_resized = cv2.resize(no_result, resolution)
        self.gray = cv2.cvtColor(no_result, cv2.COLOR_BGR2GRAY)
        self.cap_thread = threading.Thread(target=self.capture_forever)
        self.stopped = False
        self.lock = threading.Lock()
        self.previous_frame_time = time()
    
    def capture_forever(self):
        fps = 0
        fps_last_calculated = 0
        frames_count = 0
        try:
            while not self.stopped:
                dt = time()
                ret, new_frame = self.cap.read()
                if not ret:
                    print("<-- no result from camera yet -->")
                    self.image = no_result
                    continue
                # print("<-- frame captured, time: " + str(int((time() - dt)*1000)) + "ms -->")
                if self.flip_code is not None:
                    self.image = cv2.flip(new_frame, self.flip_code)
                else:
                    self.image = new_frame

                if time() - fps_last_calculated > 1:
                    fps = round(frames_count / (time()-fps_last_calculated))
                    frames_count = 0
                    fps_last_calculated = time()
                frames_count += 1
                cv2.putText(self.image, f"CAP FPS: {fps}", (30,30), cv2.FONT_HERSHEY_COMPLEX, 1.8, (0, 255, 0), 1)
                self.previous_frame_time = time()
                
                self.lock.acquire()
                self.image_resized = cv2.resize(self.image, self.resolution)
                self.lock.release()
        except KeyboardInterrupt:
            return

    def start_capture(self):
        self.cap_thread.start()

    def stop_capture(self):
        self.stopped = True
        self.cap_thread.join()
        self.cap.release()

    def get_image(self):
        self.lock.acquire()
        self.lock.release()
        return self.image

    def get_image_gray(self):
        self.lock.acquire()
        self.lock.release()
        self.gray = cv2.cvtColor(self.image_resized, cv2.COLOR_BGR2GRAY)
        return self.gray