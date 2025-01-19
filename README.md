# Barcode Reading Project
<img width="814" alt="lancers_rayons1" src="https://github.com/user-attachments/assets/365384c4-c769-4b0e-80c7-7553270db1d3" />
<img width="725" alt="segmentation_detecte" src="https://github.com/user-attachments/assets/6df9e9a9-5bbe-41c4-a392-3cb5d4a225b4" />
![segmentation_detecte1](https://github.com/user-attachments/assets/08616c41-86d2-4428-aca9-8d1a9ba25616)
<img width="627" alt="segmentation_detecte2" src="https://github.com/user-attachments/assets/da8ce4db-a56e-4889-9eb2-0e8b79a78238" />

![screenshot3](https://github.com/user-attachments/assets/3cac4e86-d151-4a08-8044-5d16108f5e33)



## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Setup](#project-setup)
- [How It Works](#how-it-works)
- [Interface and Usage](#interface-and-usage)
- [Challenges and Solutions](#challenges-and-solutions)
- [Future Enhancements](#future-enhancements)
- [Contributors](#contributors)
- [Acknowledgments](#acknowledgments)
- [License](#license)

---

## Overview

The Barcode Reading Project focuses on decoding EAN-13 barcodes from digital images using innovative methods like random ray casting. This project was undertaken as part of TS225, aiming to provide a robust solution for reading barcodes under varied conditions using image processing techniques and Python.

---

## Features

- **Random Ray Casting**: Simulates laser scanner behavior for detecting barcodes.
- **Automatic Region Detection**: Identifies regions of interest in the image.
- **Binary Signature Extraction**: Converts barcode data into a binary signature.
- **EAN-13 Decoding**: Decodes the extracted binary signature into a readable barcode.
- **Graphical User Interface (GUI)**: Allows users to interact seamlessly with the system.
- **Robust Database Handling**: Validates decoded barcodes against a predefined database.

---

## Technologies Used

- **Programming Language**: Python
- **Libraries**:
  - Scikit-image for image processing
  - Tkinter for GUI development
  - NumPy and SciPy for numerical computations
  - Matplotlib for visualizations
- **Algorithms**:
  - Random ray casting
  - Segmentation using structural tensor analysis
  - Decoding based on EAN-13 standards

---

## Project Setup

1. Navigate to the project directory:
   ```bash
   cd Barcode-Detection-App
   ```
2. Install the required dependencies.
  
3. Run the main program:
   ```bash
   python main.py
   ```
The graphical interface will open, allowing you to interact with the system.


## How It Works

1. **Image Preprocessing**: 
   - Converts the input image to grayscale.
   - Reduces noise to improve barcode region detection.

2. **Segmentation**: 
   - Identifies and isolates the region containing the barcode using gradient and structural tensor analysis.

3. **Random Ray Casting**:
   - Simulates laser scanner behavior by casting random rays within the detected barcode region.
   - Captures intensity variations along the path of each ray.

4. **Binary Signature Extraction**: 
   - Converts intensity variations into a binary signature that represents the barcode's structure.

5. **EAN-13 Decoding**:
   - Decodes the binary signature using the EAN-13 standard.
   - Validates the decoded barcode with a checksum to ensure accuracy.

6. **Database Validation**:
   - Matches the decoded barcode against a predefined database for further validation and identification.

---

## Interface and Usage

### Main Features:
1. **Image Loading**:
   - Select an image containing a barcode.
2. **Segmentation**:
   - Highlights the region of interest where the barcode is located.
3. **Ray Casting**:
   - **Manual Mode**: Allows the user to manually select points to define the ray.
   - **Automatic Mode**: Randomly casts rays in the identified barcode region.
4. **Visualization**:
   - Displays the binary signature and the decoded result in real time.
5. **Database Validation**:
   - Compares the decoded barcode with a database of known values.

### How to Use:
- Open the GUI by running the main program.
- Load an image using the interface.
- Follow the steps for segmentation, ray casting, and decoding.
- View the results, including the decoded barcode and visualization, in the GUI.

---

## Challenges and Solutions

### Challenges:
- **Handling Low-Quality Images**:
  - Barcode detection in noisy or low-resolution images was difficult.
- **Accurate Segmentation**:
  - Identifying the barcode region in complex or cluttered backgrounds required advanced techniques.
- **Reliable Decoding**:
  - Decoding the binary signature accurately under varying lighting conditions.

### Solutions:
- **Advanced Image Processing**:
  - Applied gradient-based structural tensor analysis for robust segmentation.
- **Ray Casting Optimization**:
  - Used random ray casting to improve the reliability of barcode data extraction.
- **EAN-13 Decoding Standards**:
  - Ensured decoding followed EAN-13 conventions, including checksum validation.

---

## Future Enhancements

- **Machine Learning Integration**:
  - Train models to automatically detect barcodes in complex images.
- **Support for Additional Barcode Formats**:
  - Extend decoding capabilities to handle QR codes and other formats.
- **Real-Time Processing**:
  - Enable live camera integration for real-time barcode scanning.
- **Cloud Integration**:
  - Store and validate barcodes using cloud databases.

---

## Contributors

- **Mehdi Khabouze**: Image processing, decoding algorithm development, GUI implementation, algorithm validation, system testing, and optimization.
- **Mohammed Arif**: Random ray casting.
- **Salma Alouah**: Database design and management, GUI optimization.

---

## Acknowledgments

We extend our gratitude to our project supervisor, **M. Donias**, for providing invaluable guidance and insights throughout the project.

