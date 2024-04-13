from time import sleep
import apriltagdetection, streamingserver

apriltagdetection.start_detections()
streamingserver.start_streaming_server()
while True:
    try:
        sleep(0.05)
    except KeyboardInterrupt:
        print("<-- user interrupt, shutting down... -->")
        apriltagdetection.running = False
        apriltagdetection.stop_detection()
        streamingserver.stop_streaming_server()
        break

print("<-- program exits... -->")