import cv2
import numpy as np 

def drawBox(img, bbox):
    bbox = np.array(bbox).astype(int)
    x,y,w,h = bbox
    cv2.rectangle(img, (x,y), ((x+w), (y + h)), (255,255,255), 2, 1)

cam = cv2.VideoCapture(0)
tracker = cv2.TrackerCSRT_create()
# tracker = cv2.TrackerTLD_create()
# tracker = cv2.Tracker('BOOSTING')
success, img = cam.read()
bbox = cv2.selectROI("Tracking", img, False)
tracker.init(img, bbox)

while True: 
    timer = cv2.getTickCount()
    success, img = cam.read()
    success, bbox = tracker.update(img)

    if success: 
        drawBox(img, bbox)
        cv2.putText(img, 'Tracking', (75,80), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255,0,0), 2)
    else: 
        print('Lost')
        cv2.putText(img, 'Lost', (75,80), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255,0,0), 2)

    fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
    cv2.putText(img, str(int(fps)), (75,50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (128,12,60), 2)
    
    cv2.imshow("Tracking", img)

    if cv2.waitKey(1) & 0xff == ord('q'): 
        break 