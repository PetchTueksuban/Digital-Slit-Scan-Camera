import cv2
import numpy as np
import time

# --- CONFIGURATION  ---

TARGET_H, TARGET_W = 1080, 540 
current_slit_w = 0.5            
SCAN_DURATION = 21.0            
STRETCH_RATIO = 2.5             
LOCKED_FOCUS_VALUE = 300        
WAIT_BEFORE_SCAN = 1.0  # wait time in seconds before starting scan after detecting can placement

# HSV color range for detecting green background (adjust as needed)
LOWER_GREEN = np.array([35, 40, 40]) 
UPPER_GREEN = np.array([85, 255, 255])


# --- CAMERA SETUP ---

cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560) 
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FOCUS, LOCKED_FOCUS_VALUE)


# --- VARIABLES ---

unwrapped_img = None
is_scanning = False
scan_finished = False
start_time = 0
ready_start_time = 0  # time when the can was first detected for waiting
is_waiting = False    #status flag for waiting period before scanning starts

print(f">>> SYSTEM READY: วางแช่ไว้ {WAIT_BEFORE_SCAN} วิ เพื่อเริ่มสแกน")

while True:
    ret, frame = cap.read()
    if not ret: break

    h, w = frame.shape[:2]
    cx, cy = w // 2, h // 2
    
    # 1. ตรวจสอบพิกเซลเป้าเล็ง (เฉลี่ยพื้นที่ 20x20 รอบจุดกลางเพื่อความนิ่ง)
    roi = frame[max(0, cy-10):min(h, cy+10), max(0, cx-10):min(w, cx+10)]
    avg_color_bgr = np.mean(roi, axis=(0, 1)).astype(np.uint8)
    avg_hsv = cv2.cvtColor(np.uint8([[avg_color_bgr]]), cv2.COLOR_BGR2HSV)[0][0]
    
    is_center_green = (LOWER_GREEN[0] <= avg_hsv[0] <= UPPER_GREEN[0]) and \
                      (LOWER_GREEN[1] <= avg_hsv[1] <= UPPER_GREEN[1]) and \
                      (LOWER_GREEN[2] <= avg_hsv[2] <= UPPER_GREEN[2])

    # 2. หา Contour เพื่อทำ Perspective
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.bitwise_not(cv2.inRange(hsv, LOWER_GREEN, UPPER_GREEN))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8), iterations=2)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    can_present = False
    if contours:
        max_cnt = max(contours, key=cv2.contourArea)
        if cv2.contourArea(max_cnt) > 50000:
            can_present = True
            x_b, y_b, w_b, h_b = cv2.boundingRect(max_cnt)

    # 3. Logic ควบคุมสถานะ (Wait -> Scan -> Finish)
    
    # กรณีวางวัตถุทับเป้า (เป้าไม่เห็นสีเขียว)
    if can_present and not is_center_green and not is_scanning and not scan_finished:
        if not is_waiting:
            is_waiting = True
            ready_start_time = time.time()
        
        # หน่วงเวลาครบ 1 วินาทีตามที่ตั้งไว้
        if time.time() - ready_start_time >= WAIT_BEFORE_SCAN:
            unwrapped_img = None
            is_scanning = True
            is_waiting = False
            start_time = time.time()
            print(">>> [STARTED] Scanning...")
    else:
        # ถ้าขยับออกกลางคันขณะรอ ให้รีเซ็ตการรอ
        if not is_scanning:
            is_waiting = False

    # 4. กระบวนการสแกน (Scanning Process)
    if is_scanning:
        # ตัดภาพแบบ Perspective
        pts1 = np.float32([[x_b, y_b], [x_b+w_b, y_b], [x_b, y_b+h_b], [x_b+w_b, y_b+h_b]])
        pts2 = np.float32([[0, 0], [TARGET_W, 0], [0, TARGET_H], [TARGET_W, TARGET_H]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        corrected = cv2.warpPerspective(frame, matrix, (TARGET_W, TARGET_H), flags=cv2.INTER_LANCZOS4)
        
        # ดึงพิกเซลจากจุดกึ่งกลาง (Slit Scan)
        slit = corrected[:, (TARGET_W//2) : (TARGET_W//2) + 1].copy()
        if unwrapped_img is None:
            unwrapped_img = slit.astype(np.float32)
        else:
            unwrapped_img = np.hstack((unwrapped_img, slit.astype(np.float32)))

        # ครบเวลา 21 วินาที ให้บันทึกผล
        if (time.time() - start_time) >= SCAN_DURATION:
            print(">>> [SAVING] Processing final image...")
            raw_data = np.clip(unwrapped_img, 0, 255).astype(np.uint8)
            # ยืดภาพตามสัดส่วน STRETCH_RATIO (2.5)
            final_img = cv2.resize(raw_data, (int(raw_data.shape[1] * STRETCH_RATIO), TARGET_H), interpolation=cv2.INTER_LANCZOS4)
            cv2.imwrite(f"scan_final_{int(time.time())}.png", final_img)
            is_scanning = False
            scan_finished = True

    # reset when ready for next can
    if is_center_green and scan_finished:
        print(">>> [RESET] Waiting for next can...")
        scan_finished = False
        unwrapped_img = None

    # --- UI & MONITORING ---
    monitor = cv2.resize(frame, (960, 540))
    # center marker position
    mx, my = 480, 270
    
    # color and status text
    if is_waiting:
        cross_color = (0, 255, 255) # สีเหลือง/ฟ้า (Waiting)
        status_text = f"READY IN... {max(0, WAIT_BEFORE_SCAN - (time.time()-ready_start_time)):.1f}s"
    elif is_scanning:
        cross_color = (0, 255, 0)   # สีเขียว (Scanning)
        status_text = f"SCANNING... {int(((time.time()-start_time)/SCAN_DURATION)*100)}%"
    elif scan_finished:
        cross_color = (0, 0, 255)   # สีแดง (Finished)
        status_text = "FINISHED - PLEASE REMOVE"
    else:
        cross_color = (0, 0, 255)   # สีแดง (Ready)
        status_text = "PLACE CAN AT CENTER"

    # aiming marker
    cv2.drawMarker(monitor, (mx, my), cross_color, cv2.MARKER_CROSS, 40, 2)
    cv2.circle(monitor, (mx, my), 20, cross_color, 1)
    cv2.putText(monitor, status_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, cross_color, 2)

    cv2.imshow('Cylindrical Scan System', monitor)
    
    # live preview of unwrapped image
    if unwrapped_img is not None:
        live_preview = np.clip(unwrapped_img, 0, 255).astype(np.uint8)
    
        p_h, p_w = live_preview.shape[:2]
        cv2.imshow('Live Result', cv2.resize(live_preview, (min(p_w*2, 1200), 400))) # size

    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()