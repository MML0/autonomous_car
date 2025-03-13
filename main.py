import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
def resize_with_aspect_ratio(frame, target_height=720):
    h, w = frame.shape[:2]
    aspect_ratio = w / h
    new_width = int(target_height * aspect_ratio)
    return cv2.resize(frame, (new_width, target_height))

def draw_overlay(frame):
    overlay = frame.copy()
    h, w = frame.shape[:2]
    cv2.rectangle(overlay, (50, 50), (w-50, h-50), (0, 255, 0), 2)
    cv2.putText(overlay, "Overlay Text", (60, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    return overlay

def draw_trapezoid(frame, src_points):
    pts = src_points.reshape((-1, 1, 2)).astype(np.int32)
    cv2.polylines(frame, [pts], isClosed=True, color=(0, 0, 255), thickness=2)

def correct_perspective(frame, src_points):
    h, w = frame.shape[:2]
    dst_points = np.array([
        [100, 100], [w-100, 100], [w-100, h-100], [100, h-100]
    ], dtype=np.float32)
    
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    return cv2.warpPerspective(frame, matrix, (w, h))


def fined_shaer_angel(img):
    max = 0
    best_angle = 0
    for i in range(-20,20,1):
        h, w = img.shape[:2]
        a_up = 200
        h_side = 0.7
        src_points = np.array([
            [w//4 + a_up + i, (h_side*h)//1], [3*w//4 - a_up +50 + i , (h_side*h)//1], [w-10, h-10], [10, h-10]  # Example trapezoid points
        ], dtype=np.float32)
        

        frame = correct_perspective(img, src_points)

        h, w = frame.shape[:2]
        resized_frame = cv2.resize(frame, (w//3, h//3))
        h, w = resized_frame.shape[:2]
        # Crop the middle 2/3 of the frame from all sides
        h_crop = h//6  
        w_crop = w//7  
        resized_frame = resized_frame[h_crop:h-h_crop, w_crop:w-w_crop-10]

        vertical_profile = sum_pixels_vertically(resized_frame)
        # Calculate variance of vertical profile to measure "spikiness"
        peak = np.max(vertical_profile)
        # print(peak)
        if peak > max :
            best_angle = i
            max = peak
    return best_angle


def sum_pixels_vertically(img):
    h, w = img.shape[:2]
    vertical_sums = np.zeros(w)
    
    # Sum all pixel values (BGR) from top to bottom for each column
    for x in range(w):
        vertical_sums[x] = np.sum(img[:, x])
        
    return vertical_sums
    

cap = cv2.VideoCapture("challenge_video.mp4")

if not cap.isOpened():
    print("Error: Cannot open video.")
    quit()

while cap.isOpened():
    tik = time.time()

    ret, frame = cap.read()
    if not ret:
        break
    
    
    frame = resize_with_aspect_ratio(frame)
    raw_frame = frame.copy()
    # frame = draw_overlay(frame)
    
    h, w = frame.shape[:2]
    a_up = 200
    h_side = 0.7
    src_points = np.array([
        [w//4 + a_up, (h_side*h)//1], [3*w//4 - a_up +50 , (h_side*h)//1], [w-10, h-10], [10, h-10]  # Example trapezoid points
    ], dtype=np.float32)
    
    draw_trapezoid(frame, src_points)

    # Create frames for different processing levels
    frame_level_1 = frame.copy()  # Original with overlay and trapezoid

    frame = correct_perspective(frame, src_points)

    frame_level_2 = frame.copy() 
    # Resize frame to half size


    h, w = frame_level_2.shape[:2]
    resized_frame = cv2.resize(frame_level_2, (w//2, h//2))
    h, w = resized_frame.shape[:2]
    # Crop the middle 2/3 of the frame from all sides
    h_crop = h//6  
    w_crop = w//7  
    resized_frame = resized_frame[h_crop:h-h_crop, w_crop:w-w_crop-10]
    # Get vertical sums array
    frame_level_3 = resized_frame.copy() 

    vertical_profile = sum_pixels_vertically(resized_frame)
    # Create a matplotlib figure for the vertical profile
    plt.figure(figsize=(8, 4))
    plt.plot(vertical_profile)
    plt.title('Vertical Pixel Sum Profile')
    plt.xlabel('Horizontal Position')
    plt.ylabel('Sum of Pixel Values')
    
    # Convert matplotlib figure to OpenCV image
    fig = plt.gcf()
    fig.canvas.draw()
    frame_level_4 = np.array(fig.canvas.renderer.buffer_rgba())
    frame_level_4 = cv2.cvtColor(frame_level_4, cv2.COLOR_RGBA2BGR)
    plt.close()


    angle = fined_shaer_angel(raw_frame)
    print(angle)
    # frame_level_2 = correct_perspective(frame.copy(), src_points)  # Perspective corrected
    # frame_level_4 = cv2.cvtColor(frame_level_2, cv2.COLOR_BGR2GRAY)  # Grayscale of corrected
    # frame_level_4 = cv2.Canny(frame_level_3, 100, 200)  # Edge detection
    




    # Resize all frames to 1/4 size
    h, w = frame.shape[:2]
    new_h, new_w = h//2, w//2
    frame_level_1 = cv2.resize(frame_level_1, (new_w, new_h))
    frame_level_2 = cv2.resize(frame_level_2, (new_w, new_h))
    frame_level_3 = cv2.resize(frame_level_3, (new_w, new_h))
    frame_level_4 = cv2.resize(frame_level_4, (new_w, new_h))
    
    # Combine frames into 2x2 grid
    top_row = np.hstack((frame_level_1, frame_level_2))
    bottom_row = np.hstack((frame_level_3, frame_level_4))
    combined_frame = np.vstack((top_row, bottom_row))
    
    # Replace the original frame with combined frame
    frame = combined_frame
    # cv2.imshow("Processed Video", frame)
    
    cv2.imshow("Processed Video", frame)
    
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
    
    tok = time.time()
    elapsed_time = (tok - tik) * 1000  # Convert to milliseconds
    fps = 1000 / elapsed_time  # Calculate FPS
    print(f"Time: {elapsed_time:.2f}ms, FPS: {fps:.2f}")


cap.release()
cv2.destroyAllWindows()

