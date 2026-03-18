"""
data.py — Auto Scan & Save for AI Training Dataset
---------------------------------------------------
วางกระป๋อง → สแกนอัตโนมัติ → บันทึก PNG เปล่าๆ ทันที
ไม่ต้องกดอะไร  |  Q = ออก  |  F = toggle auto-flip
"""

import cv2
import numpy as np
import time
import os

# ==========================================
# CONFIG
# ==========================================
TARGET_H         = 1080
STRETCH_RATIO    = 2.5
LOCKED_FOCUS     = 300
WAIT_BEFORE_SCAN = 1.0
DISPLAY_DURATION = 1.5      # วินาทีที่โชว์ภาพก่อนรีเซ็ต
REQUIRED_PIXELS  = 586
LOWER_GREEN      = np.array([35, 40, 40])
UPPER_GREEN      = np.array([85, 255, 255])

SAVE_DIR   = 'dataset_raw'
AUTO_FLIP  = False           # toggle ด้วยปุ่ม F ขณะรัน
os.makedirs(SAVE_DIR, exist_ok=True)

# ==========================================
# CAMERA
# ==========================================
cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
cap.set(cv2.CAP_PROP_BUFFERSIZE,   1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  2560)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)
cap.set(cv2.CAP_PROP_AUTOFOCUS,    0)
cap.set(cv2.CAP_PROP_FOCUS,        LOCKED_FOCUS)

WIN = 'DATA COLLECT  [F=Flip toggle  Q=Quit]'
cv2.namedWindow(WIN, cv2.WINDOW_NORMAL)

# ==========================================
# STATE
# ==========================================
unwrapped_img    = None
is_scanning      = False
is_waiting       = False
scan_done        = False
ready_start_time = 0.0
finish_time      = 0.0
final_img        = None
saved_count      = 0

print("=" * 50)
print("  AUTO DATA COLLECTION  —  PNG no overlay")
print(f"  Save → {os.path.abspath(SAVE_DIR)}/")
print(f"  Auto-flip: {AUTO_FLIP}  (กด F เพื่อ toggle)")
print("=" * 50)

# ==========================================
# MAIN LOOP
# ==========================================
while True:
    if cap.grab():
        ret, frame = cap.retrieve()
    else:
        break
    if not ret:
        break

    h, w   = frame.shape[:2]
    cx, cy = w // 2, h // 2

    # Green background check
    roi     = frame[max(0,cy-10):min(h,cy+10), max(0,cx-10):min(w,cx+10)]
    avg_bgr = np.mean(roi, axis=(0,1)).astype(np.uint8)
    avg_hsv = cv2.cvtColor(np.uint8([[avg_bgr]]), cv2.COLOR_BGR2HSV)[0][0]
    is_green = LOWER_GREEN[0] <= avg_hsv[0] <= UPPER_GREEN[0]

    # Trigger scan
    if not is_green and not is_scanning and not scan_done:
        if not is_waiting:
            is_waiting       = True
            ready_start_time = time.time()
        if time.time() - ready_start_time >= WAIT_BEFORE_SCAN:
            unwrapped_img = None
            is_scanning   = True
            is_waiting    = False

    # Slit accumulation
    if is_scanning:
        slit = np.mean(frame[:, cx:cx+2], axis=1, keepdims=True).astype(np.uint8)
        unwrapped_img = slit if unwrapped_img is None else np.hstack((unwrapped_img, slit))

        if unwrapped_img.shape[1] >= REQUIRED_PIXELS:
            final_img = cv2.resize(
                unwrapped_img,
                (int(unwrapped_img.shape[1] * STRETCH_RATIO), TARGET_H),
                interpolation=cv2.INTER_LANCZOS4
            )

            # Auto-flip ถ้าเปิดใช้
            if AUTO_FLIP:
                final_img = cv2.flip(final_img, 1)

            # บันทึก PNG เปล่า ไม่มี overlay
            filename = f"can_{int(time.time()*1000)}.png"
            path     = os.path.join(SAVE_DIR, filename)
            cv2.imwrite(path, final_img)
            saved_count += 1
            print(f"  [#{saved_count:04d}] {filename}")

            is_scanning = False
            scan_done   = True
            finish_time = time.time()

    # Auto-reset หลัง display
    if scan_done and time.time() - finish_time >= DISPLAY_DURATION:
        scan_done     = False
        final_img     = None
        unwrapped_img = None

    # Display
    if scan_done and final_img is not None:
        preview = cv2.resize(final_img, (0,0), fx=min(1.0, 1400/final_img.shape[1]),
                             fy=min(1.0, 1400/final_img.shape[1]))
        # HUD เฉพาะ preview ไม่กระทบไฟล์ที่บันทึก
        cv2.putText(preview, f"SAVED #{saved_count}",
                    (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 100), 3)
        cv2.putText(preview, f"flip={'ON' if AUTO_FLIP else 'OFF'}",
                    (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 255), 2)
        cv2.imshow(WIN, preview)
    else:
        monitor = cv2.resize(frame, (960, 540))
        cur_px  = 0 if unwrapped_img is None else unwrapped_img.shape[1]
        m_color = (0,255,0) if is_scanning else (0,255,255) if is_waiting else (0,0,255)
        cv2.drawMarker(monitor, (480,270), m_color, cv2.MARKER_CROSS, 40, 2)
        cv2.putText(monitor, f"PX: {cur_px}/{REQUIRED_PIXELS}",
                    (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)
        cv2.putText(monitor, f"Saved: {saved_count}  |  flip={'ON' if AUTO_FLIP else 'OFF'}",
                    (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,220,255), 2)
        cv2.imshow(WIN, monitor)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('f'):
        AUTO_FLIP = not AUTO_FLIP
        print(f"  [FLIP] Auto-flip = {'ON' if AUTO_FLIP else 'OFF'}")

cap.release()
cv2.destroyAllWindows()
print(f"\n  บันทึกทั้งหมด {saved_count} รูป → {os.path.abspath(SAVE_DIR)}/")
