import numpy as np 
import cv2 as cv 
from argparse import ArgumentParser
import matplotlib.pyplot as plt 
import pandas as pd

parser = ArgumentParser()
parser.add_argument('--manual', action = 'store_true')
args= parser.parse_args()


def run_optic_flow(): 
    feature_params = {"maxCorners": 100, 
                      'qualityLevel': 0.3,
                      'minDistance':7,
                      'blockSize':7}

    lk_params = dict( winSize  = (15,15),
                  maxLevel = 2,
                  criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

    color = np.random.randint(0,255,(100,3))


    cam = cv.VideoCapture("car-v3.mp4")
    success, im = cam.read()
    
    old_gray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
    p0 = cv.goodFeaturesToTrack(old_gray, mask = None, **feature_params)


    if args.manual: 
        p0 = []
        for i in range(3): 
            box = cv.selectROI("Car Tracking", im, fromCenter = False)
            p0.append([box[0] + box[2]*0.5, box[1] + box[-1]*0.5])


        p0 = np.array(p0, dtype = np.float32)
        df = pd.DataFrame(p0, columns = 'x,y'.split(','))
        df.to_csv('init_of.csv', index =False)

    else: 
        p0 = pd.read_csv('init_of.csv').values

    p0 = np.array(p0, dtype = np.float32).reshape(-1,1,2)

    color = color[:p0.shape[0], :]
    mask = np.zeros_like(im)

    while True: 
        success, im = cam.read()
        gray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
        p1, st, err = cv.calcOpticalFlowPyrLK(old_gray, gray, p0, None, **lk_params)

        if p1 is not None: 
            good_new = p1[st==1]
            good_old = p0[st==1]

        for i, (new, old) in enumerate(zip(good_new, good_old)): 
            a,b =new.ravel()
            c,d =old.ravel()
            mask = cv.line(mask, (int(a), int(b)), (int(c), int(d)), color[i].tolist(), 2)
            im = cv.circle(im, (int(a), int(b)),5,color[i].tolist(), -1)
        im = cv.add(im,mask)
        cv.imshow("OF", im)

        if cv.waitKey(1) & 0xff == ord('q'): 
            break 

        old_gray = gray.copy()
        p0 = good_new.reshape(-1,1,2)


if __name__ == "__main__": 

    run_optic_flow()