# Check that Python 3.10 and OpenCV were installed correctly
ssh RPi3 "python3.10 -c 'import cv2; print(cv2.__version__)'"