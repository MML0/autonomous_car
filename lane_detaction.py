import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
def resize_with_aspect_ratio(frame, target_height=300):
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
    
    # Create mask for outside regions
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    
    # Create points for left and right polygons
    h, w = frame.shape[:2]
    left_poly = np.array([[0,0], [0,h], 
                         [src_points[3][0],src_points[3][1]], [src_points[0][0],src_points[0][1]]], dtype=np.int32)
    right_poly = np.array([[w,0], [src_points[1][0],src_points[1][1]], 
                          [src_points[2][0],src_points[2][1]], [w,h]], dtype=np.int32)
    
    # Fill the polygons with white (255)
    cv2.fillPoly(mask, [left_poly], 255)
    cv2.fillPoly(mask, [right_poly], 255)
    
    # Apply black to frame using mask
    frame[mask == 255] = [0, 0, 0]
    


    h, w = frame.shape[:2]
    dst_points = np.array([
        [100, 100], [w-100, 100], [w-100, h-100], [100, h-100]
    ], dtype=np.float32)
    
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    return cv2.warpPerspective(frame, matrix, (w, h))

lastrange_i = [-10,10]
lastrange_j = [-10,10]
def fined_shaer_angel(img,src_points):
    global lastrange_i ,lastrange_j 

    max_i = 0
    max_j = 0
    best_angle = [0,0]
    for i in range(lastrange_i[0],lastrange_i[1],2):
      for j in range(lastrange_j[0],lastrange_j[1],2):
        h, w = img.shape[:2]

        # src_points[0][0] += i  # Adjust x-coordinate of first point
        # src_points[1][0] += i  # Adjust x-coordinate of second point

        # up_side = int(0.22*w)
        # offset = 10
        # h_side = 0.55
        src_points = np.array([
            [w//2 - up_side//2 +offset + i, (h_side*h)//1], [w//2 + up_side//2 + offset+ j , (h_side*h)//1], [w-10, h-10], [10, h-10]  # Example trapezoid points
        ], dtype=np.float32)
    


        frame = correct_perspective(img, src_points)

        resized_frame = crop_to_center(frame)

        # vertical_profile = sum_pixels_vertically(resized_frame)
        vertical_profile = np.sum(np.sum(resized_frame, axis=2), axis=0)
        # Calculate variance of vertical profile to measure "spikiness"
        peak_i = np.max(vertical_profile[:len(vertical_profile)//2-10]) 
        peak_j = np.max(vertical_profile[len(vertical_profile)//2+10:])
        # peak = np.var(vertical_profile[:])
        # print(peak)

        # vertical_profile = np.sum(np.sum(resized_frame, axis=2), axis=0)
        # # Smooth the profile before taking derivative
        # vertical_profile = np.convolve(vertical_profile, np.ones(2)/2, mode='same')
        # # Take derivative and threshold to 4 or 0
        # vertical_profile = np.diff(vertical_profile)
        # vertical_profile = np.convolve(vertical_profile, np.ones(7)/7, mode='same')
        # vertical_profile = np.abs(vertical_profile)
    
        # peak_i = np.sum(vertical_profile[20:len(vertical_profile)//2-20]) 
        # peak_j = np.sum(vertical_profile[len(vertical_profile)//2+20:])
        # # peak = np.var(vertical_profile[:])
        # # print(peak)


        if peak_i > max_i:
            max_i = peak_i
            best_angle[0] = i
        if peak_j > max_j:
            max_j = peak_j
            best_angle[1] = j

    lastrange_i = [best_angle[0]-3,best_angle[0]+3]
    lastrange_j = [best_angle[1]-3,best_angle[1]+3]

    # Reset ranges if they exceed abs(20) we dont need it i think insted detekt suden changes in roud angle
    max_range_triger = w//4
    if abs(lastrange_i[0]) > max_range_triger or abs(lastrange_i[1]) > max_range_triger:
        lastrange_i = [-10, 10]
        print('triger !!!',max_range_triger)
    if abs(lastrange_j[0]) >max_range_triger or abs(lastrange_j[1]) > max_range_triger:
        lastrange_j = [-10, 10]
        print('triger !!!',max_range_triger)



    return best_angle

def crop_to_center(frame):
    h, w = frame.shape[:2]
    # Crop the middle 2/3 of the frame from all sides
    h_crop = int(h*0.3)
    w_crop = int(w*0.3)
    resized_frame = frame[h_crop+10:h-h_crop, w_crop+5:w-w_crop-5]
    return resized_frame

def process_frame(frame,debug_mode=True):
    tik = time.time()

    global up_side ,h_side ,offset
    frame = resize_with_aspect_ratio(frame)
    raw_frame = frame.copy()
    # frame = draw_overlay(frame)
    
    h, w = frame.shape[:2]
    # chalenge video 1
    # up_side = int(0.16*w)
    # offset = 4
    # h_side = 0.68
    
    # lane video 2
    up_side = int(0.194*w)
    offset = -4
    h_side = 0.78
    src_points = np.array([
        [w//2 - up_side//2 +offset, (h_side*h)//1], [w//2 + up_side//2 + offset , (h_side*h)//1], [w-10, h-10], [10, h-10]  # Example trapezoid points
    ], dtype=np.float32)
    


    angle = fined_shaer_angel(raw_frame,src_points)
    print(angle,sum(angle))

    end_time = time.time()
    execution_time = end_time - tik

    if not debug_mode:
        return angle


    draw_trapezoid(frame, src_points)

    # Create frames for different processing levels
    frame_level_1 = frame.copy()  # Original with overlay and trapezoid

    frame = correct_perspective(frame, src_points)

    frame_level_2 = frame.copy() 
    # Resize frame to half size


    resized_frame = crop_to_center(frame)
    # Get vertical sums array
    frame_level_3 = resized_frame.copy() 

    # vertical_profile = sum_pixels_vertically(resized_frame)
    vertical_profile = np.sum(np.sum(resized_frame, axis=2), axis=0)
    
    
    # # Smooth the profile before taking derivative
    # vertical_profile = np.convolve(vertical_profile, np.ones(3)/3, mode='same')
    # # Take derivative and threshold to 4 or 0
    # vertical_profile = np.diff(vertical_profile)
    # vertical_profile = np.convolve(vertical_profile, np.ones(7)/7, mode='same')
    # vertical_profile = np.abs(vertical_profile)
    



    i = angle[0]
    j = angle[1] 
    src_points = np.array([
        [w//2 - up_side//2 +offset + i, (h_side*h)//1], [w//2 + up_side//2 + offset+ j , (h_side*h)//1], [w-10, h-10], [10, h-10]  # Example trapezoid points
    ], dtype=np.float32)
    
    frame = correct_perspective(raw_frame, src_points)

    resized_frame = crop_to_center(frame)

    vertical_profile_2 = np.sum(np.sum(resized_frame, axis=2), axis=0)

    # Create a matplotlib figure for the vertical profile
    plt.figure(figsize=(8, 4))
    plt.plot(vertical_profile, label='Profile 1')
    plt.plot(vertical_profile_2, label='Profile 2')
    plt.title('Vertical Pixel Sum Profile')
    plt.xlabel('Horizontal Position')
    plt.ylabel('Sum of Pixel Values')
    plt.legend()
    
    # Convert matplotlib figure to OpenCV image
    fig = plt.gcf()
    fig.canvas.draw()
    frame_level_4 = np.array(fig.canvas.renderer.buffer_rgba())
    frame_level_4 = cv2.cvtColor(frame_level_4, cv2.COLOR_RGBA2BGR)
    plt.close()


    # cv2.imshow("Processed Video2", resized_frame)
    frame_level_5 = resized_frame.copy() 




    # frame_level_2 = correct_perspective(frame.copy(), src_points)  # Perspective corrected
    # frame_level_4 = cv2.cvtColor(frame_level_2, cv2.COLOR_BGR2GRAY)  # Grayscale of corrected
    # frame_level_4 = cv2.Canny(frame_level_3, 100, 200)  # Edge detection

    frame_level_6 = frame_level_1.copy()
    # Draw lines connecting lower and upper points with angle adjustments
    # Left line
    cv2.line(frame_level_6, 
             (int(src_points[3][0]+10), int(src_points[3][1])),  # Bottom left point
             (int(src_points[0][0]+angle[0]*5), int(src_points[0][1])),  # Top left point + angle[0] shift
             (0, 255, 100), 5)  # Green color, 2px thickness
    
    # Right line
    cv2.line(frame_level_6,
             (int(src_points[2][0]-10), int(src_points[2][1])),  # Bottom right point  
             (int(src_points[1][0]+angle[1]*5), int(src_points[1][1])),  # Top right point + angle[1] shift
             (0, 255, 100), 5)  # Green color, 2px thickness

    
    # Resize all frames to 1/4 size
    h, w = frame.shape[:2]
    new_h, new_w = h//2, w//2
    frame_level_1 = cv2.resize(frame_level_1, (new_w, new_h))
    frame_level_2 = cv2.resize(frame_level_2, (new_w, new_h))
    frame_level_3 = cv2.resize(frame_level_3, (new_w, new_h))
    frame_level_4 = cv2.resize(frame_level_4, (new_w, new_h))
    frame_level_5 = cv2.resize(frame_level_5, (new_w, new_h))
    frame_level_6 = cv2.resize(frame_level_6, (new_w, new_h))
    
    # Combine frames into 2x2 grid
    top_row = np.hstack((frame_level_1, frame_level_2,frame_level_3))
    bottom_row = np.hstack((frame_level_4,frame_level_6, frame_level_5))
    combined_frame = np.vstack((top_row, bottom_row))
    
    # Replace the original frame with combined frame
    frame = combined_frame
    # cv2.imshow("Processed Video", frame)
    
    cv2.imshow("Processed Video", frame)
    
    if cv2.waitKey(25) & 0xFF == ord('q'):
        quit()
    
    tok = time.time()
    elapsed_time = (tok - tik) * 1000  # Convert to milliseconds
    fps = 1000 / elapsed_time  # Calculate FPS
    print(f"Time: {elapsed_time:.2f}ms, FPS: {fps:.2f} , real FPS: {1/execution_time:.4f} ")
    return angle

if __name__ == "__main__":
        

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
        
        angle = process_frame(frame,debug_mode=True)

    cap.release()
    cv2.destroyAllWindows()

