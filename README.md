## Linear Shrinkage Measurement App

### Description

This application is designed to measure the linear shrinkage of objects over time by analyzing a series of image frames. It is built with Python, utilizing libraries like Tkinter for the GUI, OpenCV for image processing, and Pandas for data management.


### Features

Load multiple frames from a folder

Manual point selection for distance measurement

Real-time linear shrinkage calculation

Optical Flow for tracking points in consecutive frames

Export shrinkage data to CSV


### Algorithms Used

Point Tracking: The Lucas-Kanade method in Optical Flow

Shrinkage Calculation: Natural Logarithm and percentage-based formulas

Data Export: Pandas DataFrame to CSV


### Installation

Clone the Repository

bash


```git clone https://github.com/your_username/linear-shrinkage-measurement.git```

Navigate to the Directory

bash


```cd linear-shrinkage-measurement```

Install Required Libraries

Make sure you have Python installed, then run:

```pip install -r requirements.txt```


### User Guide

### Step-by-Step Guide

Load Frames: Click the "Load Frames" button to load image frames from a folder.

Enter Known Distance: Input the known distance for calibration.

Start Measurement: Click the "Start Measurement" button.

Set Points: Click two points on the image to measure the distance.

Calculate Shrinkage: Once all frames have points set, click "Calculate Shrinkage" to calculate and export the data.


### Exceptions and Warnings

If no folder is selected, a warning popup appears.

If no valid images are found, a warning popup appears.

If the known distance is invalid, a warning popup appears.

If no data is available for export or calculation, a warning popup appears.


### Contribution

Feel free to fork the project and submit a pull request.
