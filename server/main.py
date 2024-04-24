from time import sleep
import apriltagdetection, streamingserver, fieldnavigation

apriltagdetection.camera0.start_detections()
streamingserver.start_streaming_server()
while True:
    try:
        fieldnavigation.pull_odometry_data_from_networktable()
        fieldnavigation.process_results(apriltagdetection.camera0.tags, apriltagdetection.CAMERA_RESOLUTION)
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
    
apriltagdetection.camera0.stop_detection()
streamingserver.stop_streaming_server()
print("<-- program exits... -->")