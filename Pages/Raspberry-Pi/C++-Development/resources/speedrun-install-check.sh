# Check that Python 3.8 and OpenCV were installed correctly
ssh -t RPi3 "python3.8 -c 'import cv2; print(cv2.__version__)'"