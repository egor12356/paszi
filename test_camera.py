import time

import cv2
import os

RTSP_URL = 'rtsp://admin:123Qwerty@192.168.1.108:554/h264Preview_01_main'
RTSP_URL = 'rtsp://admin:123Qwerty@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0'

os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp'

cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

if not cap.isOpened():
    print('Cannot open RTSP stream')
    exit(-1)

while True:
    _, frame = cap.read()
    cv2.imshow('RTSP stream', frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()

# vs = cv2.VideoCapture(RTSP_URL)
# while True:
#     ret,frame = vs.read()
#     if not(ret):
#         st = time.time()
#         vs = cv2.VideoCapture(RTSP_URL)
#         print("tot time lost due to reinitialization : ", time.time()-st)
#         continue
#
#     cv2.imshow("Current frame", frame)
#     cv2.waitKey(0)


