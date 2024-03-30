import cv2, sys, threading
from time import time

no_result = cv2.imread("./webpages/no_result.png")
class USBCamera:
    def __init__(self, portID:int, resolution:tuple, frame_rate:int, flip_code):
        if sys.platform.startswith('linux'):
            self.cap = cv2.VideoCapture(portID, cv2.CAP_V4L2)
        else:
            self.cap = cv2.VideoCapture(portID)

        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J','P','G'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0]) # width
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1]) # height
        self.cap.set(cv2.CAP_PROP_FPS, frame_rate) 
        self.flip_code = flip_code

        self.image = no_result
        self.gray = cv2.cvtColor(no_result, cv2.COLOR_BGR2GRAY)
        self.cap_thread = threading.Thread(target=self.capture_forever)
        self.stopped = False
    
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

                self.gray = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)

                if time() - fps_last_calculated > 1:
                    fps = round(frames_count / (time()-fps_last_calculated))
                    frames_count = 0
                    fps_last_calculated = time()
                frames_count += 1
                cv2.putText(self.image, f"CAP FPS: {fps}", (30,30), cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 255, 0), 1)
        except KeyboardInterrupt:
            return

    def start_capture(self):
        self.cap_thread.start()

    def stop_capture(self):
        self.stopped = True
        self.cap_thread.join()
        self.cap.release()

    def get_image(self):
        return self.image

    def get_image_gray(self):
        return self.gray
