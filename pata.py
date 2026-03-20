import cv2
import numpy as np
import time
import os

# ==========================================
# 1. การตั้งค่าระบบ
# ==========================================
TARGET_H, TARGET_W = 1080, 540 
STRETCH_RATIO = 2.5 
LOCKED_FOCUS_VALUE = 350
WAIT_BEFORE_SCAN = 1.0     
DISPLAY_DURATION = 2.0  # ลดเวลาแสดงผลลง จะได้สแกนใบต่อไปได้ไวขึ้น

REQUIRED_PIXELS = 586      
LOWER_GREEN = np.array([35, 40, 40])
UPPER_GREEN = np.array([85, 255, 255])

# สร้างโฟลเดอร์เก็บ Dataset สำหรับสอน AI
DATASET_DIR = 'Dataset_Cans'
if not os.path.exists(DATASET_DIR): 
    os.makedirs(DATASET_DIR)

print("--------------------------------------------------")
print(f"🤖 AI DATA COLLECTION MODE STARTED 🤖")
print(f"Saving all scanned images to: ./{DATASET_DIR}/")
print("--------------------------------------------------")

# ==========================================
# 2. ลูปการทำงานหลัก (สแกนแล้วเซฟเลย ไม่ต้องประมวลผล)
# ==========================================
cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) 
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560); cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0); cap.set(cv2.CAP_PROP_FOCUS, LOCKED_FOCUS_VALUE)

unwrapped_img = None; is_scanning = False; scan_finished = False
ready_start_time = 0; is_waiting = False
scan_count = 0

while True:
    if cap.grab(): ret, frame = cap.retrieve()
    else: break
    if not ret: break

    h, w = frame.shape[:2]; cx, cy = w // 2, h // 2
    roi = frame[max(0, cy-10):min(h, cy+10), max(0, cx-10):min(w, cx+10)]
    avg_hsv = cv2.cvtColor(np.uint8([[np.mean(roi, axis=(0, 1)).astype(np.uint8)]]), cv2.COLOR_BGR2HSV)[0][0]
    is_center_green = (LOWER_GREEN[0] <= avg_hsv[0] <= UPPER_GREEN[0])

    if not is_center_green and not is_scanning and not scan_finished:
        if not is_waiting: is_waiting = True; ready_start_time = time.time()
        if time.time() - ready_start_time >= WAIT_BEFORE_SCAN:
            unwrapped_img = None; is_scanning = True; is_waiting = False

    if is_scanning:
        slit = np.mean(frame[:, cx : cx + 2], axis=1, keepdims=True).astype(np.uint8)
        if unwrapped_img is None: unwrapped_img = slit
        else:
            if unwrapped_img.shape[1] < REQUIRED_PIXELS:
                unwrapped_img = np.hstack((unwrapped_img, slit))

        if unwrapped_img.shape[1] >= REQUIRED_PIXELS:
            # ยืดภาพให้ได้สัดส่วน
            final_img = cv2.resize(unwrapped_img, (int(unwrapped_img.shape[1] * STRETCH_RATIO), TARGET_H), interpolation=cv2.INTER_LANCZOS4)
            
            # 🚨 เซฟรูปลงโฟลเดอร์ Dataset ทันที! 🚨
            scan_count += 1
            timestamp = int(time.time())
            filename = os.path.join(DATASET_DIR, f"can_scan_{timestamp}_{scan_count}.jpg")
            cv2.imwrite(filename, final_img)
            print(f"✅ Saved image #{scan_count} -> {filename}")
            
            is_scanning = False; scan_finished = True; finish_time = time.time() 

    if scan_finished:
        if (time.time() - finish_time >= DISPLAY_DURATION):
            scan_finished = False; unwrapped_img = None
            try:
                cv2.destroyWindow('AI Data Collection')
            except: pass
        else:
            # โชว์รูปที่สแกนเสร็จให้ดูแว๊บนึง
            cv2.namedWindow('AI Data Collection', cv2.WINDOW_NORMAL)
            cv2.imshow('AI Data Collection', final_img)

    # หน้าจอมอนิเตอร์การทำงาน
    monitor = cv2.resize(frame, (960, 540))
    m_color = (0, 255, 0) if is_scanning else (0, 255, 255) if is_waiting else (0, 0, 255)
    cv2.drawMarker(monitor, (480, 270), m_color, cv2.MARKER_CROSS, 40, 2)
    cur_px = 0 if unwrapped_img is None else unwrapped_img.shape[1]
    
    cv2.putText(monitor, f"COLLECTED: {scan_count} IMAGES", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(monitor, f"SCAN PX: {cur_px}/{REQUIRED_PIXELS}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.imshow('Cylindrical Scan System', monitor)

    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release(); cv2.destroyAllWindows()