# Digital Slit-Scan Camera  
**Digital Slit-Scan Camera** is a specialized high-speed imaging tool designed for Cylindrical Surface Inspection and Dimensional Measurement.  

By extracting raw pixel slits and stitching them in real-time, this system transforms rotating objects into high-resolution "unwrapped" 2D maps, making it perfect for detecting surface defects, dents, or verifying product dimensions.

# 🌟 Features
* **Ultra-Sharp RAW Sampling:** Bypasses perspective warping during capture to maintain maximum image clarity and text legibility.  
* **Intelligent Auto-Trigger:** Uses HSV-based green screen detection to automatically start and stop scans when an object is placed.  
* **High-Precision Measurement:** Integrated diameter calculation (cm) using calibrated pixel-to-mm ratios.  
* **Bayer Pattern Filter:** Advanced 2-pixel neighborhood averaging to eliminate color artifacts (Red/Green lines) without blurring the image.  
* **Real-time Monitoring:** Dual-window interface showing the live camera feed and the "unwrapping" progress.  
* **Industrial Ready:** Locked focus and exposure support for consistent results in manufacturing environments.  

# 🛠 Installation  
**Clone the Repository:**

```bash
git clone https://github.com/PetchTueksuban/Digital-Slit-Scan-Camera.git
```

```bash
cd Digital-Slit-Scan-Camera
``` 

**Install Dependencies:**  
This project requires Python and a few essential libraries.  

```bash
pip install -r requirements.txt
```

# 💡 What is Slit-Scan?
This technique mimics the functionality of panoramic or photo-finish cameras. Instead of capturing the entire frame at once, the tool extracts only a specific pixel row/column (e.g., the center) from every frame and joins them together. This "unfolds" moving objects into a single, stretched, and often surreal image.

<img width="1570" height="1080" alt="549884444-2de19870-ca09-4711-88cc-c7dc44e67ece" src="https://github.com/user-attachments/assets/94696c98-7260-49cc-b1d6-c9d5bb00bc35" />
