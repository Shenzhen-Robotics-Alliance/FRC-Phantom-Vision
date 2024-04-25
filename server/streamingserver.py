WEB_PORT = 5800
NETWORKTABLE_PORT = 5801

from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from time import time, sleep
from urllib.parse import ParseResult, urlparse
from MathUtils.LinearAlgebra import *
import cv2, threading, os, apriltagdetection

SERVER_ROOT = os.path.split(os.path.realpath(__file__))[0]
print("server root: ", SERVER_ROOT)

def get_request_param(parsed_path:ParseResult, param_name:str) -> float:
    if param_name not in parsed_path.query:
        return 0
    return float(parsed_path.query[param_name])

# MJPEG Streaming Server
class StreamingHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"<--client visited {self.path} -->")
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/":
            # Return the main page (index.html)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # with open('/home/ironn-maple/index.html', 'rb') as f:
            with open(os.path.join(SERVER_ROOT, 'webpages', 'index.html'), 'rb') as f:
                content = f.read()
            self.wfile.write(content)
        elif parsed_path.path == '/fps':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            message = "Apriltag Detections FPS: "
            for i in range(len(apriltagdetection.apriltag_cameras)):
                message += f'cam{i} {apriltagdetection.apriltag_cameras[i].get_fps()}, '
            print("Returning FPS to webpage: ", message)
            self.wfile.write( str(message).encode())
        elif parsed_path.path == '/video_feed':
            cam_id = 0
            if 'camera_id' in parsed_path.params:
                cam_id = parsed_path.params['camera_id']

            if cam_id < 0 or cam_id >= len(apriltagdetection.apriltag_cameras):
                self.send_404()
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while apriltagdetection.apriltag_cameras[cam_id].running:
                try:
                    frame = apriltagdetection.apriltag_cameras[cam_id].get_frame()
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame_bytes = buffer.tobytes()
                    self.send_frame(frame_bytes)
                    # sleep(0.02)
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                    print("client disconnected")
                    return
        elif parsed_path.path == '/tag_boxes':
            cam_id = 0
            if 'camera_id' in parsed_path.params:
                cam_id = parsed_path.params['camera_id']

            if cam_id < 0 or cam_id >= len(apriltagdetection.apriltag_cameras):
                self.send_404()
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while apriltagdetection.apriltag_cameras[cam_id].running:
                try:
                    self.wfile.write(apriltagdetection.apriltag_cameras[cam_id].get_results().encode())
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                    print("client disconnected")
                    return
        else:
            self.send_404()

    def send_404(self):
        # Respond with a 404 Not Found status and custom message
            self.send_response(404)  # Send 404 Not Found status
            self.send_header('Content-Type', 'text/html')  # Specify the content type as HTML
            self.end_headers()
            self.wfile.write(b"<html><head><title>Not Found</title></head><body><h1>Page not found</h1></body></html>")
    def send_frame(self, frame):
        boundary = b'frame'
        headers = (
            b'Content-Type: image/jpeg\r\n',
            b'Content-Length: ' + str(len(frame)).encode() + b'\r\n\r\n'
        )
        self.wfile.write(b'--' + boundary + b'\r\n' + b''.join(headers) + frame + b'\r\n')

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass
httpd = ThreadedHTTPServer(('0.0.0.0', WEB_PORT), StreamingHandler)
server_thread = threading.Thread(target=httpd.serve_forever)
server_thread.daemon = True

def start_streaming_server():
    # Start the HTTP server in a separate thread
    print("<-- starting inspector server... -->")
    server_thread.start()
    print("<-- inspector server started -->")

def stop_streaming_server():
    print("<-- shutting down streaming server -->")
    httpd.shutdown()
    server_thread.join()
    print("<-- streaming server shutdown complete -->")