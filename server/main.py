from time import sleep
import apriltagdetection, streamingserver, fieldnavigation

for apriltag_camera in apriltagdetection.apriltag_cameras:
    apriltag_camera.start_detections()
streamingserver.start_streaming_server()
while True:
    try:
        fieldnavigation.pull_odometry_data_from_networktable()
        fieldnavigation.process_results(apriltagdetection.CAMERA_RESOLUTION, apriltagdetection.apriltag_cameras, apriltagdetection.camera_profiles)
        
        fieldnavigation.send_results_to_networktable()
        sleep(0.02)
    except KeyboardInterrupt:
        print("<-- user interrupt, shutting down... -->")
        
        break
    except Exception as e:
        print("<-- error occued in main thread: -->")
        print(e)
        print("<-- shutting down due to error -->")

        break
    
for apriltag_camera in apriltagdetection.apriltag_cameras:
    apriltag_camera.stop_detection()
streamingserver.stop_streaming_server()
print("<-- program exits... -->")