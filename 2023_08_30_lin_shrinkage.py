#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------
           COPYRIGHT INFORMATION
-------------------------------------------

© 2023 Emmanuel Bamidele. All rights reserved.

This software and its documentation are protected by copyright law and international treaties. Unauthorized reproduction or distribution of this software, or any portion of it for commercial purpose is not allowed.

Linear Shrinkage Measurement software, including all related files, data, and documentation, are the intellectual property of Emmanuel Bamidele.

For questions, inquiries, and permissions related to the use and distribution of this software, please contact:

Emmanuel Bamidele
Email: correspondence.bamidele@gmail.com

-------------------------------------------
               LICENSE INFORMATION
-------------------------------------------

The Linear Shrinkage Measurement software is released under the MIT License. A copy of the license can be found in the LICENSE file on the GitHub repository.

-------------------------------------------
              VERSION INFORMATION
-------------------------------------------

Linear Shrinkage Measurement software
Version: 1.0
Date: August 2023

-------------------------------------------
                 DISCLAIMER
-------------------------------------------

The Linear Shrinkage Measurement software is provided "as is" without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

The software is intended for research and educational purposes only. It is the responsibility of the user to ensure proper operation and adherence to all applicable laws and regulations while using this software.

-------------------------------------------
            CITATION INFORMATION
-------------------------------------------

To cite the Linear Shrinkage Measurement software, please use the following citation:

Bamidele, Emmanuel. (2023). Linear Shrinkage Measurement Software [Software]. Retrieved from www.emmanuelbamidele.com

For the GitHub repository, visit:
https://github.com/Emmanuel-Bamidele/Shrinkage-Measurement

Documentation is available on GitHub repository.
"""

import re
import tkinter as tk
import math
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import cv2
import os
import pandas as pd


class ShrinkageMeasurementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Linear Shrinkage Measurement: © 2023 Emmanuel Bamidele")

        self.folder_path = ""
        self.frames = []
        self.index = 0
        self.ref_point1 = None
        self.ref_point2 = None
        self.original_length = 0.0
        self.current_length = 0.0
        self.prev_gray = None
        self.valid_image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
        self.length_data = []

        pad_x = 10
        pad_y = 10

        self.canvas = tk.Canvas(root, bg="white", height=480, width=640)
        self.canvas.grid(row=0, column=0, columnspan=4, padx=pad_x, pady=pad_y)

        self.label_original_length = tk.Label(root, text="Original Length: 0.0", bg='black', fg='white')
        self.label_original_length.grid(row=1, column=0, padx=pad_x, pady=pad_y)

        self.label_current_length = tk.Label(root, text="Current Length: 0.0", bg='green', fg='white')
        self.label_current_length.grid(row=1, column=1, padx=pad_x, pady=pad_y)

        self.label_shrinkage = tk.Label(root, text="Linear Shrinkage: 0.0%", bg='red', fg='white')
        self.label_shrinkage.grid(row=1, column=2, padx=pad_x, pady=pad_y)

        self.label_status = tk.Label(root, text="Status: Idle", bg='blue', fg='white')
        self.label_status.grid(row=2, column=0, padx=pad_x, pady=pad_y)

        self.label_detected_shrinkage = tk.Label(root, text="Detected Shrinkage: None")
        self.label_detected_shrinkage.grid(row=2, column=1, padx=pad_x, pady=pad_y)

        self.label_known_distance = tk.Label(root, text="Known Distance: ")
        self.label_known_distance.grid(row=2, column=2, padx=pad_x, pady=pad_y)

        self.entry_known_distance = tk.Entry(root, width=8)
        self.entry_known_distance.grid(row=2, column=3, padx=pad_x, pady=pad_y)

        tk.Button(root, text="Load Frames", command=self.load_folder, bg='black', fg='white').grid(row=3, column=0,
                                                                                                   padx=pad_x,
                                                                                                   pady=pad_y)
        tk.Button(root, text="Start Measurement", command=self.start_measurement, bg='green', fg='white').grid(row=3,
                                                                                                               column=1,
                                                                                                               padx=pad_x,
                                                                                                               pady=pad_y)
        tk.Button(root, text="Export Data", command=self.export_data, bg='green', fg='white').grid(row=3, column=2,
                                                                                                   padx=pad_x,
                                                                                                   pady=pad_y)
        tk.Button(root, text="Calculate Shrinkage", command=self.calculate_shrinkage, bg='black', fg='white').grid(
            row=3, column=3, padx=pad_x, pady=pad_y)

        self.first_frame = True
        self.index = 0
        self.pixel_to_unit_ratio = 1.0

    def load_folder(self):
        self.folder_path = filedialog.askdirectory()
        if not self.folder_path:
            messagebox.showwarning("Warning", "No folder selected. Please select a folder.")
            return

        frames = [f for f in os.listdir(self.folder_path) if f.lower().endswith(self.valid_image_extensions)]

        if not frames:
            messagebox.showwarning("Warning", "No valid image frames found in the selected folder.")
            return

        # Sort the frames using a custom sorting function
        frames.sort(key=self.alphanumeric_sort)

        self.frames = [os.path.join(self.folder_path, f) for f in frames]

        step_messages = [
            "1) Frames uploaded successfully!",
            "2) Frames Sorted Successfully!",
            "3) Enter known distance of gage length or width of frame one",
            "4) Click Start Measurement",
            "5) Click the point 1 and point 2  with your known distance in mind",
            "6) Click Ok in the popped up message after clicking all points 1 and 2",
            "7) Click Calculate Shrinkage",
            "8) Data is automatically exported but you can do it manually again"
        ]

        full_message = "\n".join(step_messages)

        messagebox.showinfo("Steps to Follow", full_message)

        # Show the first frame after loading it
        self.index = 0
        self.show_frame(self.frames[self.index])

    def alphanumeric_sort(self, s):
        """Custom sorting function for alphanumeric sorting of filenames."""
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

    def start_measurement(self):
        # Reset all previous states and data
        self.ref_point1 = None
        self.ref_point2 = None
        self.index = 0
        self.length_data = []

        self.label_status.config(text="Status: Measurement started")

        self.first_frame = True  # Reset first_frame flag when starting a new measurement

        # Add this line to initiate optical flow-based updates
        self.root.after(100, self.update_frame)

        self.go_to_next_frame()

    def go_to_next_frame(self):
        if self.index < len(self.frames):
            frame_path = self.frames[self.index]
            self.show_frame(frame_path)
            self.canvas.bind("<Button-1>", self.set_reference)
            print(f"Ready for manual marking on frame {self.index + 1}")
        else:
            # This block of code runs when all frames have been measured
            self.canvas.unbind("<Button-1>")  # Unbind the canvas click event
            messagebox.showinfo("Completed",
                                "All frames are measured. Please click Calculate to complete the calculation.")
            self.label_status.config(text="Status: Measurement complete. Click Calculate to finish.")

    def set_reference(self, event):
        print(f"Received a click event at ({event.x}, {event.y}).")

        if self.ref_point1 is None:
            self.ref_point1 = np.array([event.x, event.y])
            self.canvas.create_text(event.x, event.y, text="Point 1", fill="red")
            print("Set Point 1.")
        else:
            # Initial raw point
            raw_point2 = np.array([event.x, event.y])

            # Compute differences to determine orientation
            delta_x = abs(raw_point2[0] - self.ref_point1[0])
            delta_y = abs(raw_point2[1] - self.ref_point1[1])

            # Snap to the closest axis (horizontal or vertical)
            if delta_x > delta_y:
                # Make it horizontal
                self.ref_point2 = np.array([raw_point2[0], self.ref_point1[1]])
            else:
                # Make it vertical
                self.ref_point2 = np.array([self.ref_point1[0], raw_point2[1]])

            self.canvas.create_text(self.ref_point2[0], self.ref_point2[1], text="Point 2", fill="red")
            print("Set Point 2.")

        if self.ref_point1 is not None and self.ref_point2 is not None:
            pixel_distance = np.linalg.norm(self.ref_point2 - self.ref_point1)

            if self.first_frame:  # Check if it's the first frame
                self.original_length = pixel_distance
                try:
                    known_distance = float(self.entry_known_distance.get())
                except ValueError:
                    messagebox.showwarning("Warning", "Please enter a valid known distance.")
                    return

                self.pixel_to_unit_ratio = known_distance / self.original_length
                self.original_length *= self.pixel_to_unit_ratio  # Scale the original_length
                self.label_original_length.config(text=f"Original Length: {self.original_length:.2f}")

                self.first_frame = False  # Set first_frame to False after updating original_length

            real_distance = pixel_distance * self.pixel_to_unit_ratio  # Scale the real_distance

            shrinkage = ((self.original_length - real_distance) / self.original_length) * 100

            self.label_current_length.config(text=f"Current Length: {real_distance:.2f}")
            self.label_shrinkage.config(text=f"Linear Shrinkage: {shrinkage:.2f}%")

            self.length_data.append({
                "Frame": self.index,
                "Current Length": real_distance,
                "Original Length": self.original_length,
                "Shrinkage": shrinkage
            })

            self.ref_point1 = None
            self.ref_point2 = None

            self.index += 1
            self.go_to_next_frame()

    def show_frame(self, frame_path):
        # Clear the canvas before displaying a new frame
        self.canvas.delete("all")

        # Load and show image
        image = cv2.imread(frame_path)
        image = cv2.resize(image, (640, 480))  # Resize the image to fit the canvas
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image=image)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
        self.canvas.image = image

        # Reset reference points for the new frame
        self.ref_point1 = None
        self.ref_point2 = None

        # Bind canvas to set_reference function
        self.canvas.bind("<Button-1>", self.set_reference)

    def calculate_shrinkage(self):
        if not self.length_data:
            messagebox.showwarning("Warning", "No data to calculate shrinkage.")
            return

        for frame_data in self.length_data:
            current_length = frame_data["Current Length"]
            # Updated the formula to use the natural logarithm
            frame_data["Shrinkage"] = math.log(current_length / self.original_length)
            
            # Update Detected Shrinkage if shrinkage is greater than zero
            if frame_data["Shrinkage"] > 0:
                self.label_detected_shrinkage.config(text="Detected Shrinkage: Yes")
            
        self.export_data()

        # Update Status to Completed
        self.label_status.config(text="Status: Completed")

        messagebox.showinfo("Info", "Shrinkage calculated.")

    def update_frame(self):
        if self.index < len(self.frames):
            frame_path = self.frames[self.index]
            image = cv2.imread(frame_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            if self.prev_gray is not None:
                # Optical Flow calculation
                p0 = np.float32([self.ref_point1, self.ref_point2]).reshape(-1, 1, 2)
                p1, st, err = cv2.calcOpticalFlowPyrLK(self.prev_gray, gray, p0, None)

                if p1 is not None and np.any(st == 1):
                    new_points = p1.reshape(-1, 2).astype(int)
                    if len(new_points) == 2:
                        self.ref_point1, self.ref_point2 = new_points

                    pixel_distance = np.linalg.norm(self.ref_point2 - self.ref_point1)
                    real_distance = pixel_distance * self.pixel_to_unit_ratio
                    shrinkage = ((self.original_length - real_distance) / self.original_length) * 100

                    self.label_current_length.config(text=f"Current Length: {real_distance:.2f}")
                    self.label_shrinkage.config(text=f"Linear Shrinkage: {shrinkage:.2f}%")

                    self.length_data.append({
                        "Frame": self.index,
                        "Current Length": real_distance,
                        "Original Length": self.original_length,
                        "Shrinkage": shrinkage
                    })

                    self.prev_gray = gray.copy()

                    # Display the image on the tkinter canvas
                    self.show_frame(frame_path)

                    # Draw a line between reference points
                    self.canvas.create_line(self.ref_point1[0], self.ref_point1[1], self.ref_point2[0],
                                            self.ref_point2[1], fill="white")

                    self.index += 1

                    # Schedule the next frame update
                    self.root.after(100, self.update_frame)
                else:
                    print("Optical flow calculation failed. Possibly points went out of the frame.")
            else:
                self.prev_gray = gray.copy()
                self.root.after(100, self.update_frame)

    def export_data(self):
        if self.length_data:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            if file_path:
                df = pd.DataFrame(self.length_data)
                df = df[['Frame', 'Original Length', 'Current Length', 'Shrinkage']]
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", "Data exported successfully.")
        else:
            messagebox.showwarning("Warning", "No data to export.")


if __name__ == '__main__':
    root = tk.Tk()
    app = ShrinkageMeasurementApp(root)
    root.mainloop()
