import cv2
import numpy as np 
import glob 
from argparse import ArgumentParser 

#=============================================
# https://www.pyimagesearch.com/2018/08/06/tracking-multiple-objects-with-opencv/
#=============================================


good_init = [(829, 118, 70, 54), 
             (796, 497, 57, 92)]

parser = ArgumentParser()
parser.add_argument('--manual', action = 'store_true')
args = parser.parse_args()


def drawBox(img, bbox):
    bbox = np.array(bbox).astype(int)
    x,y,w,h = bbox
    cv2.rectangle(img, (x,y), ((x+w), (y + h)), (255,255,255), 2, 1)


def drawSpeed(img, prev_box, box):
    box = np.array(box).astype(int)
    x,y,w,h = box
    xcentre = int(x + w/2)
    ycentre = int(y + h/2)
    prev_box = np.array(prev_box).astype(int)
    x,y,w,h = prev_box
    xcentreprev = int(x + w/2)
    ycentreprev = int(y + h/2)
    dx = xcentre - xcentreprev
    dy = ycentre - ycentreprev
    cv2.arrowedLine(img, (xcentre, ycentre), (xcentre+5*dx, ycentre+5*dy), (0, 255, 0), 2, 1)


cam = cv2.VideoCapture("car-v3.mp4")
cam_fps = cam.get(cv2.CAP_PROP_FPS)
trackers = cv2.legacy.MultiTracker_create()

success, img = cam.read()
if args.manual: 
    nb_detect = int(input('How many object to detect ? '))
    for i in range(nb_detect):
        box = cv2.selectROI("Car Tracking", img, fromCenter = False)
        # tracker = cv2.legacy.TrackerKCF_create()
        tracker = cv2.legacy.TrackerCSRT_create()
        print('Box: {}'.format(box))
        trackers.add(tracker, img, box)
else: 
    for i in range(len(good_init)): 
        box = good_init[i]
        # tracker = cv2.legacy.TrackerKCF_create()
        tracker = cv2.legacy.TrackerCSRT_create()
        print('Box: {}'.format(box))
        trackers.add(tracker, img, box)

w,h = int(img.shape[1]*0.6), int(img.shape[0]*0.6)
video_writer = cv2.VideoWriter('output.mp4',cv2.VideoWriter_fourcc(*'mp4v'), cam_fps, (w,h))

prev_bbox = None

while True: 
    timer = cv2.getTickCount()
    success, img = cam.read()

    if img is None:
        break

    success, bbox = trackers.update(img)

    if success: 
        for box in bbox: 
            drawBox(img, box)
        cv2.putText(img, 'Tracking', (75,80), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255,0,0), 2)
    else: 
        print('Lost')
        cv2.putText(img, 'Lost', (75,80), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255,0,0), 2)

    if prev_bbox is not None:
        for (prev_box, box) in zip(prev_bbox, bbox):
            drawSpeed(img, prev_box, box)

    prev_bbox = bbox

    fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
    cv2.putText(img, str(int(fps)), (75,50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (128,12,60), 2)

    w,h = int(img.shape[1]*0.6), int(img.shape[0]*0.6)
    img = cv2.resize(img, (w,h))
    cv2.imshow("Tracking", img)

    video_writer.write(img)

    # if cv2.waitKey(1) & 0xff == ord('s'): 
    #     box = cv2.selectROI("Car Tracking", img, fromCenter = False)
    #     tracker = cv2.legacy_TrackerKCF()
    #     print('ok')
    #     trackers.add(tracker, img, box) 

    if cv2.waitKey(1) & 0xff == ord('q'): 
        break

cam.release()
video_writer.release()