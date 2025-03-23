import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
import lane_detaction
# Use screen capture instead of video file
from PIL import ImageGrab

# cap = cv2.VideoCapture("challenge_video.mp4")
cap = cv2.VideoCapture("LaneVideo.mp4")

if not cap.isOpened():
    print("Error: Cannot open video.")
    quit()

while cap.isOpened():
    tik = time.time()

    ret, frame = cap.read()
    if not ret:
        break
    
    # screen = ImageGrab.grab() 
    # frame = np.array(screen)
    # # correct rgb bgr
    # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    # #crop 1/4 top left from h,w shape
    # h,w = frame.shape[:2]
    # frame = frame[0:h//2,0:w//2]

    angle = lane_detaction.process_frame(frame,debug_mode=True)
    # angle = lane_detaction.process_frame(frame,debug_mode=False)
    print(angle,sum(angle))

    end_time = time.time()
    execution_time = end_time - tik


    i = angle[0]
    j = angle[1] 

    cv2.imshow("raw frame", frame)
    
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
    
    tok = time.time()
    elapsed_time = (tok - tik) * 1000  # Convert to milliseconds
    fps = 1000 / elapsed_time  # Calculate FPS
    print(f"Time: {elapsed_time:.2f}ms, FPS: {fps:.2f} , real FPS: {1/execution_time:.4f} ")


cap.release()
cv2.destroyAllWindows()

