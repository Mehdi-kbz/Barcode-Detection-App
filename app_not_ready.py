#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 11:17:03 2024

@author: starbook
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk

# Import your external functions
from segmentation import segmentation_main
from ray_launcher import lancer_aleatoire
from extract_main import extract
from barcode_decoder import decode_ean13_signature

class BarcodeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Barcode Extraction and Decoding")
        self.geometry("1000x700")
        self.configure(bg="#f0f0f0")

        self.image_path = None
        self.cv_image = None  # Will store the loaded grayscale image (OpenCV)
        self.cv_image_color = None  # Will store a color version for drawing lines
        self.photo_image = None
        self.ray_points = None
        self.region_points = None
        self.signature_95bits = None

        self.create_widgets()

    def create_widgets(self):
        # Top frame for buttons and actions
        action_frame = tk.Frame(self, bg="#f0f0f0", padx=10, pady=10)
        action_frame.pack(side=tk.TOP, fill=tk.X)

        # Buttons
        btn_load = tk.Button(action_frame, text="Choose Image", command=self.load_image_dialog, bg="#4CAF50", fg="white")
        btn_load.pack(side=tk.LEFT, padx=5)

        btn_segment = tk.Button(action_frame, text="Segment Region", command=self.segment_region, bg="#2196F3", fg="white")
        btn_segment.pack(side=tk.LEFT, padx=5)

        btn_ray = tk.Button(action_frame, text="Launch Ray", command=self.launch_ray, bg="#9C27B0", fg="white")
        btn_ray.pack(side=tk.LEFT, padx=5)

        btn_extract = tk.Button(action_frame, text="Extract Signature", command=self.extract_signature_action, bg="#FF9800", fg="white")
        btn_extract.pack(side=tk.LEFT, padx=5)

        btn_decode = tk.Button(action_frame, text="Decode Barcode", command=self.decode_barcode, bg="#E91E63", fg="white")
        btn_decode.pack(side=tk.LEFT, padx=5)

        # Status label
        self.status_label = tk.Label(action_frame, text="Please load an image.", bg="#f0f0f0")
        self.status_label.pack(side=tk.LEFT, padx=10)

        # Canvas to display image
        self.canvas = tk.Canvas(self, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def load_image_dialog(self):
        path = filedialog.askopenfilename(title="Select an image", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self.image_path = path
            self.load_image()
        else:
            self.status_label.config(text="No image selected.")

    def load_image(self):
        if not os.path.exists(self.image_path):
            messagebox.showerror("Error", f"Image {self.image_path} does not exist.")
            return
        self.cv_image = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
        if self.cv_image is None:
            messagebox.showerror("Error", "Failed to load image!")
            return
        # Create a color version for drawing lines
        self.cv_image_color = cv2.cvtColor(self.cv_image, cv2.COLOR_GRAY2BGR)
        self.display_image(self.cv_image_color)
        self.status_label.config(text="Image loaded. You can segment the region now.")

    def display_image(self, cv_image_bgr):
        # Convert cv_image_bgr (BGR) to RGB and then to PhotoImage
        cv_image_rgb = cv2.cvtColor(cv_image_bgr, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cv_image_rgb)
        self.photo_image = ImageTk.PhotoImage(image=pil_image)
        self.canvas.config(width=pil_image.width, height=pil_image.height)
        self.canvas.delete("all")
        self.canvas.create_image(0,0,anchor=tk.NW, image=self.photo_image)

    def segment_region(self):
        if self.cv_image_color is None:
            self.status_label.config(text="Please load an image first.")
            return

        # Call your external segmentation function
        p1, p2, p3, p4 = segmentation_main()
        self.region_points = (p1, p2, p3, p4)

        # Draw a polygon to show the segmented region
        pts = np.array([p1,p2,p3,p4], np.int32).reshape((-1,1,2))
        cv2.polylines(self.cv_image_color, [pts], isClosed=True, color=(0,255,0), thickness=2)
        self.display_image(self.cv_image_color)
        self.status_label.config(text="Region segmented. Now launch a ray.")

    def launch_ray(self):
        if self.region_points is None:
            self.status_label.config(text="Please segment the region first.")
            return

        p1, p2, p3, p4 = self.region_points
        point1, point2 = lancer_aleatoire(p1,p2,p3,p4)
        self.ray_points = (point1, point2)

        # Draw the ray on the image
        cv2.line(self.cv_image_color, point1, point2, (255,0,0), 2)
        self.display_image(self.cv_image_color)
        self.status_label.config(text="Ray launched. Now extract the signature.")

    def extract_signature_action(self):
        if self.ray_points is None:
            self.status_label.config(text="Please launch a ray first.")
            return

        point1, point2 = self.ray_points
        # Extract the 95-bit signature from the external function
        self.signature_95bits = extract(self.cv_image, point1, point2)
        if self.signature_95bits is not None:
            self.status_label.config(text="Signature extracted. Now decode the barcode.")
            messagebox.showinfo("Signature Extracted", f"95-bit signature:\n{self.signature_95bits}")
        else:
            self.status_label.config(text="No useful region found in the signature.")
            messagebox.showinfo("No Signature", "No useful region found in the signature.")

    def decode_barcode(self):
        if self.signature_95bits is None:
            self.status_label.config(text="No signature to decode.")
            return
        code_barres = decode_ean13_signature(self.signature_95bits)
        if code_barres:
            self.status_label.config(text=f"Decoded Barcode: {code_barres}")
            messagebox.showinfo("Barcode Decoded", f"EAN-13 Code: {code_barres}")
        else:
            self.status_label.config(text="Failed to decode barcode.")
            messagebox.showerror("Error", "Failed to decode barcode.")

if __name__ == "__main__":
    app = BarcodeApp()
    app.mainloop()
