# QR-Based-AR-Campus-Navigator


## Overview
The **QR-Based AR Campus Navigator** is a web-based augmented reality system designed to help users navigate a college campus interactively. By scanning QR codes placed at key campus locations, users receive real-time AR-based information and navigation cues directly in their browser.

This project was developed as part of a **DBMS course project**, integrating web technologies with a backend database to manage locations, routes, and metadata.

---

## 🛠️ Tech Stack
- **Frontend:** HTML, CSS, JavaScript  
- **Backend:** Flask (Python)  
- **Database:** MySQL  
- **AR Framework:** AR.js + A-Frame  
- **Hosting:** Flask development server  

---

## Features
- QR code–based AR triggering for campus locations
- Real-time AR overlays displaying location name and details
- Centralized database for:
  - Building names
  - Room/Lab information
  - QR marker IDs
- Scalable design for adding new locations without code changes
- Lightweight — runs directly in the browser (no app install)

---

## 🗄️ Database Design
The MySQL database stores campus navigation data including:
- Location ID (linked to QR code)
- Building name
- Room/Lab name
- Description

### Example Tables
- `locations`
- `buildings`
- `qr_markers`

All tables are normalized to reduce redundancy and ensure efficient querying.

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
git clone https://github.com/Harsh3x/QR-Based-AR-Campus-Navigator
cd qr-ar-campus-navigator

### 2️⃣ Create virtual environment and install dependencies

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

### 3️⃣ Configure MySQL Database

DB_HOST = "localhost"

DB_USER = "root"

DB_PASSWORD = "your_password"

DB_NAME = "campus_navigator"

### 4️⃣ Run the Flask server

python app.py

Server will start at: http://localhost:5000


## 📸 How It Works

User scans a QR code placed in the campus

The browser opens the AR interface

AR.js detects the marker

Flask fetches corresponding data from MySQL

Location details are rendered as AR overlays

## 👨‍💻 Contributors
Harsh 

Hammas
