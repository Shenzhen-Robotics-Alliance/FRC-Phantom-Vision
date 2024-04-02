PORT = 8888

from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from time import time, sleep
from urllib.parse import ParseResult, urlparse
from MathUtils.LinearAlgebra import *
import apriltagdetection, cv2
import threading

def get_request_param(parsed_path:ParseResult, param_name:str) -> float:
    if param_name not in parsed_path.query:
        return 0
    return float(parsed_path.query[param_name])

robot_odometry_position = Vector2D()
robot_odometry_rotation = Rotation2D(0)

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
            with open('./webpages/index.html', 'rb') as f:
                content = f.read()
            self.wfile.write(content)
        elif parsed_path.path == '/fps':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            fps = apriltagdetection.get_fps()
            if fps == -1:
                self.wfile.write("waiting for camera to start".encode())
            else:
                print("Returning FPS to webpage: ", fps)
                self.wfile.write( ("Detector FPS: " + str(fps))  .encode())
        elif parsed_path.path == '/video_feed':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while apriltagdetection.running:
                try:
                    frame = apriltagdetection.get_frame()
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame_bytes = buffer.tobytes()
                    self.send_frame(frame_bytes)
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                    print("client disconnected")
                    return
        elif parsed_path.path == '/results':
            global robot_odometry_position, robot_odometry_rotation
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            robot_odometry_position = Vector2D([get_request_param(parsed_path, 'robot_odometry_x'),get_request_param(parsed_path, 'robot_odometry_y')])
            robot_odometry_rotation = Rotation2D(get_request_param(parsed_path, 'robot_odometry_rotation'))

            self.wfile.write(apriltagdetection.get_results().encode()) # TODO: return accurate result of robot position and gamepiece detections

        elif parsed_path.path == '/results_legacy':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            while apriltagdetection.running:
                try:
                    self.wfile.write(apriltagdetection.get_results().encode())
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                    print("client disconnected")
                    return
        else:
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

# Start the HTTP server in a separate thread
print("<-- starting inspector server... -->")
httpd = ThreadedHTTPServer(('0.0.0.0', PORT), StreamingHandler)
server_thread = threading.Thread(target=httpd.serve_forever)
server_thread.daemon = True
server_thread.start()
print("<-- inspector server started -->")

apriltagdetection.start_detections()
while True:
    try:
        sleep(0.05)
    except KeyboardInterrupt:
        print("<-- user interrupt, shutting down... -->")
        apriltagdetection.running = False
        httpd.shutdown()
        apriltagdetection.stop_detection()
        server_thread.join()
        break

print("<-- shutdown complete, program exits... --> ")
