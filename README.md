# 📷 Automated AI Attendance System

An enterprise-grade, full-stack Automated Attendance System using Computer Vision, Django REST Framework, and SQLite/PostgreSQL. 

Instead of traditional roll calls or RFID cards, this system uses a Kiosk-style webcam to detect faces, calculate 128-dimension facial embeddings, and communicate with a backend REST API to log check-ins and check-outs smartly.

## ✨ Key Features
* **Real-Time Face Recognition:** Utilizes OpenCV and `dlib`'s state-of-the-art facial recognition model (99.38% accuracy on LFW dataset).
* **Decoupled Architecture:** Separates the Kiosk camera script from the Django Backend, communicating via RESTful APIs.
* **Smart Attendance Logic:** Implements time-buffer logic (debouncing) to prevent API spam and automatically handles Check-In vs. Check-Out states based on time deltas.
* **Privacy-First Data Storage:** Does not store raw images in the database. Instead, it converts faces to 128-d mathematical vectors and stores them securely in JSON fields.
* **Automated Registration:** Includes custom Django Management Commands to bulk-register employees from a directory of images.

## 🛠️ Tech Stack
* **Backend:** Python, Django, Django REST Framework
* **Computer Vision:** OpenCV, `face_recognition` (dlib), NumPy
* **Database:** SQLite (Development) / PostgreSQL (Production ready via JSONFields)

## 🏗️ System Architecture
1. **The Kiosk (`kiosk.py`):** Runs continuously at an entryway. It downscales video frames for performance, detects face locations, and sends cropped frame bytes to the API on a 5-second cooldown.
2. **The Server (`api/views.py`):** Receives the HTTP POST request, calculates the 128-d face encodings, compares them against the database using Euclidean distance, and logs the timestamp.

## 🚀 How to Run Locally

### 1. Setup the Environment
```bash
git clone https://github.com/sarojsap/Face-Recognition-Attendance-System.git
cd YOUR_REPO_NAME
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

### ⚠️ Special Note: Installing `dlib` on Windows
The `face_recognition` library relies on `dlib`, which is written in C++. Because Windows does not come with a C++ compiler by default, running `pip install dlib` usually results in a build error. You have two options to fix this:

**Option 1: The Official Method (Recommended for Developers)**
1. Download and install the [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
2. During installation, check the box for **"Desktop development with C++"**.
3. Restart your computer and run `pip install dlib`.

**Option 2: The Quick Method (Pre-compiled Wheel)**
If you are using Python 3.10 or 3.11, you can install a pre-compiled `.whl` file without needing C++ tools.
1. Download the appropriate `.whl` file for your Python version from a community repo (e.g., [z-mahmud22/Dlib_Windows_Python3.x](https://github.com/z-mahmud22/Dlib_Windows_Python3.x)).
2. Place the file in the project folder.
3. Run: `pip install dlib-19.22.99-cp310-cp310-win_amd64.whl` *(adjust filename as needed)*.
4. Then run: `pip install face_recognition`.