# Digital-Slit-Scan-Camera
It uses a green-screen mask to isolate a rotating object, then extracts a 1-pixel vertical "slit" from the center of every frame. Over 21 seconds, it stitches these slices horizontally to "unwrap" the cylindrical surface into a flat image, finally stretching the result for the correct aspect ratio.

🌀 Cylindrical Slit-Scan System
A Python-based computer vision tool that "unwraps" rotating cylindrical objects (like soda cans or bottles) into a flat, 2D panoramic image using OpenCV.

🚀 Overview
The system detects an object against a green background, performs a perspective transformation to square the object, and captures a 1-pixel wide "slit" from the center of every frame. Over a set duration, these slices are stitched together to create a seamless flat projection of the object's entire surface.

🛠️ Key FeaturesAutomatic Detection: Uses HSV color masking to detect when an object is placed in the frame.Perspective Correction: Automatically warps the object's bounding box to a standard vertical rectangle ($1080 \times 540$) before scanning.Intelligent State Machine: * READY: Waiting for object placement.WAITING: A 1-second "debounce" to ensure the object is still.SCANNING: Real-time stitching with a live progress percentage.FINISHED: Saves the final high-resolution .png.Live Preview: Shows the unwrapping process in real-time.

📋 Requirements
Python 3.x
OpenCV (cv2)
NumPy

⚙️ Configuration
You can adjust the following variables at the top of the script:
| Variable | Description |
| :--- | :--- |
| SCAN_DURATION | How many seconds the scan runs (set to match one full rotation). |
| STRETCH_RATIO | Horizontal scaling factor to correct the aspect ratio. |
| LOWER/UPPER_GREEN | HSV threshold values for your green screen background. |
| WAIT_BEFORE_SCAN | Delay before the scan starts once an object is detected. |

🕹️ How to Use
Setup: Place a green background behind a rotating platform (turntable).
Lighting: Ensure even lighting to avoid shadows on the green screen.
Run: Execute the script. The camera will lock focus at the predefined value.
Place Object: Put your can/bottle in the center marker.
Scan: Once the timer finishes, the image is saved to the project folder as scan_final_[timestamp].png.

⚠️ Important Notes
Focus: Auto-focus is disabled by default to prevent "hunting" during the scan. Adjust LOCKED_FOCUS_VALUE to suit your camera distance.
Sync: For a perfect unwrap, the SCAN_DURATION must match the exact time it takes for your turntable to complete one 360° rotation.
