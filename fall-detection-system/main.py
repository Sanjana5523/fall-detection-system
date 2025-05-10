import collections
import os
import time
import logging
import cv2
import psutil
import numpy as np
import torch
import imutils
from ultralytics import YOLO
from pushbullet import Pushbullet

# Pushbullet API Key for Mobile Notifications 
API_KEY = "o.HR52igQXqgUImQ17L45PKmGSiNqEXyHw"  
pb = Pushbullet(API_KEY)

# Load YOLOv8 for Activity Monitoring and Fall Detection
device = "cuda" if torch.cuda.is_available() else "cpu"
yolo_model = YOLO("yolo-Weights/activity-model-v8s.pt").to(device)
if device == "cuda":
    yolo_model = yolo_model.half()

# Setup logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
def check_video_file(video_path):
    return os.path.exists(video_path) and video_path.endswith(('.mp4', '.avi', '.mov'))

def main(video_path):
    if not check_video_file(video_path):
        logging.error("Invalid or missing video file.")
        return
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error("Failed to open video file.")
        return
    
    track_hist = collections.defaultdict(list)
    start_time = time.time()
    CPU_THRESH, DUR_THRESH = 80.0, 600.0
    
    act_map = {0: "Standing", 1: "sleeping", 2: "sitting"}
    act_dict = {key: {"start_time": 0, "duration": 0} for key in act_map.values()}
    act_dict["prev"] = None
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            logging.info("End of video file or error reading frame.")
            break
        elapsed_time = time.time() - start_time
        frame = imutils.resize(frame, width=800)
        
        results = yolo_model.track(frame, persist=True)
        if results and results[0].boxes.id is not None:
            activity = results[0].boxes.cls.cpu().numpy().astype(int)[0]
            curr = act_map.get(activity, "unknown")
            
            if curr == "unknown":
                label = "Detecting..."
            else:
                label = curr
                
                if act_dict[curr]["start_time"] == 0:
                    act_dict[curr]["start_time"] = round(elapsed_time, 2)
                
            cv2.putText(frame, f"Activity: {label}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        fall_detected = False
        if results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.int().cpu().tolist()
            
            for (x1, y1, x2, y2) in boxes:
                h, w = y2 - y1, x2 - x1
                if h - w <= 0:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, "Fall Detected!", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    fall_detected = True
                else:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        if fall_detected:
            pb.push_note("Fall Detection Alert", "A fall has been detected! Please check immediately!")
            print("Fall Detected")
        
        cv2.imshow("Activity Monitoring & Fall Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    video_file_path = "C:/Users/ganji/OneDrive/Desktop/fall-detection-system/demovideos/fall.mp4"
    main(video_file_path)
