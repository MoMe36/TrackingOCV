import cv2
import numpy as np
from argparse import ArgumentParser 
import matplotlib.pyplot as plt 
import pandas as pd 
import os
import socket
# =============================================
# https://www.pyimagesearch.com/2018/08/06/tracking-multiple-objects-with-opencv/
# =============================================


class OcvTracker:
    def __init__(self, strategy):
        self.tracker = strategy()
        self.box = None

        self.kalman = cv2.KalmanFilter(4, 4)  # state = (x, y, vx, vy)
        self.kalman.transitionMatrix = np.array([[1., 0., 1., 0.],
                                                 [0., 1., 0., 1.],
                                                 [0., 0., 1., 0.],
                                                 [0., 0., 0., 1.]])
        self.kalman.processNoiseCov = 0.1 * np.array([[1., 0., 1., 0.],
                                                      [0., 1., 0., 1.],
                                                      [0., 0., 1., 0.],
                                                      [0., 0., 0., 1.]])
        self.kalman.measurementMatrix = 1. * np.eye(4)
        self.kalman.measurementNoiseCov = np.array([[1., 0., 2., 0.],
                                                    [0., 1., 0., 2.],
                                                    [0., 0., 2., 0.],
                                                    [0., 0., 0., 2.]]) * 10
        self.kalman.errorCovPost = 1. * np.ones((4, 4))
        self.kalman.errorCovPre = 1. * np.ones((4, 4))
        self.kalman.gain = self.kalman.gain.astype(float)
        self.kalman.statePre = 0.1 * np.random.randn(4)
        self.kalman.statePost = 0.1 * np.random.randn(4)

    def init(self, img, box):
        self.box = np.array(box)
        self.kalman.statePost[:2] = box[:2]
        self.tracker.init(img, tuple(box))

    def predict(self):
        self.kalman.predict()

    def update(self, img):
        success, box = self.tracker.update(img)
        box = np.array(box)
        if success:
            measure = np.zeros(4)
            measure[2:] = box[:2] - self.box[:2]
            measure[:2] = box[:2]
            self.kalman.correct(measure)
            self.box[:2] = self.kalman.statePost[:2].astype(int)
        else:
            self.box[:2] = self.kalman.statePre[:2].astype(int)
            self.init(img, self.box)

        return success, self.box


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


def draw_speed(img: np.ndarray, tracker: OcvTracker, scale: float, size_multiplier: int = 5):
    centre = (scale*get_box_center(tracker.box)).astype(int)
    diff = tracker.kalman.statePost[2:].astype(int)
    cv2.arrowedLine(img, tuple(centre), tuple(centre + size_multiplier*diff), (0, 255, 0), 2, 1)


def add_to_record_file(data, name_p): 
    name = '{}_{}'.format(name_p['tracker'], name_p['nb'])
    if not os.path.isfile('fps_data.csv'): 
        df = pd.DataFrame(data, columns=[name])
    else: 
        df = pd.read_csv('fps_data.csv')
        df[name] = data

    df.to_csv('fps_data.csv', index=False)

def communication(dataa):
	clientSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	try:
		clientSocket.connect(('localhost',5566))
		print("connected client!")
		data=dataa
		data=data.encode("utf8")
		clientSocket.sendall(data)

	except:
		print("communication to the server failed")

	finally:
		clientSocket.close()


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
    cam_w, cam_h = cam.get(cv2.CAP_PROP_FRAME_WIDTH), cam.get(cv2.CAP_PROP_FRAME_HEIGHT)

    tracker_scale = 0.6
    tracker_w, tracker_h = int(cam_w * tracker_scale), int(cam_h * tracker_scale)

    display_scale = 0.6
    display_w, display_h = int(cam_w * display_scale), int(cam_h * display_scale)

    good_init = [tuple(map(lambda x: int(x*tracker_scale), box)) for box in good_init]

    trackers = []
    # tracker_strategy = cv2.legacy.TrackerKCF_create if args.kcf else cv2.legacy.TrackerCSRT_create

    def tracker_strategy():
        return OcvTracker(cv2.legacy.TrackerKCF_create if args.kcf else cv2.legacy.TrackerCSRT_create)

    fps_record = []

    success, img = cam.read()
    tracker_img = cv2.resize(img, (tracker_w, tracker_h))

    if args.manual:
        nb_detect = int(input('How many object to detect ? '))
        for i in range(nb_detect):
            box = cv2.selectROI("Car Tracking", img, fromCenter=False)
            box = tuple(map(lambda x: int(x*tracker_scale), box))
            tracker = tracker_strategy()
            tracker.init(tracker_img, box)

            print(f'Box: {box}')
            trackers.append(tracker)
    else:
        nb_detect = len(good_init)
        for box in good_init:
            tracker = tracker_strategy()
            tracker.init(tracker_img, box)

            print(f'Box: {box}')
            trackers.append(tracker)

    video_writer = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), cam_fps, (display_w, display_h))

    while True:
        timer = cv2.getTickCount()
        success, img = cam.read()

        if img is None:
            print("End of input stream")
            break

        tracker_img = cv2.resize(img, (tracker_w, tracker_h))
        if not args.kcf:
            tracker_img = cv2.cvtColor(tracker_img, cv2.COLOR_BGR2GRAY)
        display_img = cv2.resize(img, (display_w, display_h))

        lost = False
        pos_value=[]
        for tracker in trackers:
            tracker.predict()
            success, bbox = tracker.update(tracker_img)

            box = tracker.box * display_scale / tracker_scale
            pos_value.append(box)
            draw_box(display_img, box)
            draw_speed(display_img, tracker, display_scale / tracker_scale)
            communication(pos_value)
            

            if not success:
                lost = True


        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
        if lost:
            print('Lost')
            fps_record.append(0)
            cv2.putText(display_img, 'Lost', (75, 80), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 0), 2)
        else:
            fps_record.append(fps)
            cv2.putText(display_img, 'Tracking', (75, 80), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 0), 2)

        cv2.putText(display_img, str(int(fps)), (75, 50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (128, 12, 60), 2)

        cv2.imshow("Tracking", display_img)

        video_writer.write(display_img)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break

    add_to_record_file(fps_record, {'tracker': 'KCF' if args.kcf else 'CSRT',
                                    'nb': nb_detect})

    cam.release()
    video_writer.release()


if __name__ == '__main__':
    main()
