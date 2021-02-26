import cv2
import numpy as np
from argparse import ArgumentParser 
import matplotlib.pyplot as plt 
import pandas as pd 
import os
# =============================================
# https://www.pyimagesearch.com/2018/08/06/tracking-multiple-objects-with-opencv/
# =============================================


def get_box_center(box: np.ndarray) -> np.ndarray:
    return (box[:2] + box[2:]/2).astype(int)


def draw_box(img: np.ndarray, bbox: np.ndarray):
    bbox = bbox.astype(int)
    x, y, w, h = bbox
    cv2.rectangle(img, (x, y), ((x+w), (y + h)), (255, 255, 255), 2, 1)


def draw_speed(img: np.ndarray, prev_box: np.ndarray, box: np.ndarray, size_multiplier: int = 5):
    centre = get_box_center(box).astype(int)
    prev_centre = get_box_center(prev_box).astype(int)
    diff = centre - prev_centre
    cv2.arrowedLine(img, tuple(centre), tuple(centre + size_multiplier*diff), (0, 255, 0), 2, 1)


def add_to_record_file(data, name_p): 
    name = '{}_{}'.format(name_p['tracker'], name_p['nb'])
    if not os.path.isfile('fps_data.csv'): 
        df = pd.DataFrame(data, columns=[name])
    else: 
        df = pd.read_csv('fps_data.csv')
        df[name] = data

    df.to_csv('fps_data.csv', index=False)


def main():
    good_init = [(829, 118, 70, 54),
                 (796, 497, 57, 92)]

    parser = ArgumentParser()
    parser.add_argument('--manual', action='store_true')
    parser.add_argument('--kcf', action='store_true')
    args = parser.parse_args()

    plt.style.use('ggplot')

    cam = cv2.VideoCapture("car-v3.mp4")
    cam_fps = cam.get(cv2.CAP_PROP_FPS)

    trackers = cv2.legacy.MultiTracker_create()
    tracker_strategy = cv2.legacy.TrackerKCF_create if args.kcf else cv2.legacy.TrackerCSRT_create

    fps_record = []

    success, img = cam.read()

    if args.manual:
        nb_detect = int(input('How many object to detect ? '))
        for i in range(nb_detect):
            box = cv2.selectROI("Car Tracking", img, fromCenter=False)
            tracker = tracker_strategy()

            print(f'Box: {box}')
            trackers.add(tracker, img, box)
    else:
        nb_detect = len(good_init)
        for box in good_init:
            tracker = tracker_strategy()

            print(f'Box: {box}')
            trackers.add(tracker, img, box)

    w, h = int(img.shape[1]*0.6), int(img.shape[0]*0.6)
    video_writer = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), cam_fps, (w, h))

    prev_bbox = None

    while True:
        timer = cv2.getTickCount()
        success, img = cam.read()

        if img is None:
            break

        success, bbox = trackers.update(img)

        if success:
            for box in bbox:
                draw_box(img, box)
            cv2.putText(img, 'Tracking', (75, 80), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 0), 2)
        else:
            print('Lost')
            cv2.putText(img, 'Lost', (75, 80), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 0), 2)

        if prev_bbox is not None:
            for (prev_box, box) in zip(prev_bbox, bbox):
                draw_speed(img, prev_box, box)

        prev_bbox = bbox

        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

        if success:
            fps_record.append(fps)
        else:
            fps_record.append(0)

        cv2.putText(img, str(int(fps)), (75, 50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (128, 12, 60), 2)

        w, h = int(img.shape[1]*0.6), int(img.shape[0]*0.6)
        img = cv2.resize(img, (w, h))
        cv2.imshow("Tracking", img)

        video_writer.write(img)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break

    add_to_record_file(fps_record, {'tracker': 'KCF' if args.kcf else 'CSRT',
                                    'nb': nb_detect})

    cam.release()
    video_writer.release()


if __name__ == '__main__':
    main()
