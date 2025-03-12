import cv2
import numpy as np

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





cap = cv2.VideoCapture("10 min count up.mp4")

if not cap.isOpened():
    print("Error: Cannot open video.")
    quit()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = resize_with_aspect_ratio(frame)
    frame = draw_overlay(frame)
    
    h, w = frame.shape[:2]
    src_points = np.array([
        [w//4, h//2], [3*w//4, h//2], [w-50, h-50], [50, h-50]  # Example trapezoid points
    ], dtype=np.float32)
    
    draw_trapezoid(frame, src_points)
    frame = correct_perspective(frame, src_points)
    
    cv2.imshow("Processed Video", frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

