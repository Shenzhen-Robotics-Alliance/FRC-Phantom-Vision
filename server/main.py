from time import sleep
import apriltagdetection, streamingserver, fieldnavigation

apriltagdetection.start_detections()
streamingserver.start_streaming_server()
while True:
    try:
        fieldnavigation.pull_odometry_data_from_networktable()
        fieldnavigation.process_results(apriltagdetection.tags, apriltagdetection.CAMERA_RESOLUTION)
        fieldnavigation.send_results_to_networktable()
    except KeyboardInterrupt:
        print("<-- user interrupt, shutting down... -->")
        apriltagdetection.running = False
        apriltagdetection.stop_detection()
        streamingserver.stop_streaming_server()
        break

print("<-- program exits... -->")