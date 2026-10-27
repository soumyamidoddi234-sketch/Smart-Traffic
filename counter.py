"""Classical CV vehicle counting: MOG2 background subtraction + contours. No ML."""
import cv2
import numpy as np
from config import FRAME_SKIP, MIN_AREA, WARMUP, ROI


def count_vehicles(video_path):
    """Return the queue estimate (75th percentile of per-frame vehicle counts)."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    bg = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=40, detectShadows=True)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    counts, i = [], 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        i += 1
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = int(ROI[0]*w), int(ROI[1]*h), int(ROI[2]*w), int(ROI[3]*h)
        roi = cv2.GaussianBlur(frame[y1:y2, x1:x2], (5, 5), 0)
        mask = bg.apply(roi)
        if i <= WARMUP or i % FRAME_SKIP:
            continue
        mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)[1]   # drop shadows (127)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        counts.append(sum(cv2.contourArea(c) >= MIN_AREA for c in cnts))
    cap.release()
    return float(np.percentile(counts, 75)) if counts else 0.0
