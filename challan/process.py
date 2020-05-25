import cv2 as cv
import numpy as np
import imutils
import matplotlib.pyplot as plt
from tempfile import TemporaryDirectory
import requests
import os

import logging
logger = logging.getLogger(__name__)

# def get_last_box(binary, right):
#     x = np.sum(binary, axis=1)
#     x = x.argsort()[-20:][::-1]
#     x = np.sort(x)[::-1]
#     t = 1
#     while abs(x[t]-x[0]) < 10:
#         t += 1
#     bottom = x[t]
#     while abs(x[t]-bottom) < 10:
#         t += 1
#     top = x[t]
#     left = binary.shape[1]//2
#     return left, top, right, bottom

def main(input_image_url, data=None):
    """Inputs the aws url of the original gatepass that is to be processed
    and the data dict in the format given below:
    Outputs a tuple containing the tmp_dir and path of the processed gatepass"""
    if data is None:
        # populate a random data if it is not given
        data = {
            'max_qty': 9,
            'tuff_qty': 15,
            'max_size': 1125,
            'tuff_size': 2231,
            'date': '04/11/2020'
        }
    # image = cv.imread('test2.jpg')
    image = requests.get(input_image_url)
    logger.info('Downloaded the gatepass image from: {}'.format(input_image_url))
    tmp_dir = TemporaryDirectory(prefix='images')
    input_image_path = os.path.join(tmp_dir.name, 'original_gatepass.jpg')
    with open(input_image_path, 'wb') as f:
        f.write(image.content)
    logger.info('Saved the downloaded gatepass to location: {}'.format(input_image_path))
    original = cv.imread(input_image_path)
    logger.info('Shape of the Original image = {}'.format(original.shape))
    ratio = original.shape[0]/500
    image = imutils.resize(original, height=500)
    gray = ~cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    gray_blur = cv.GaussianBlur(gray, (5,5), 0)
    binary = cv.Canny(gray_blur, 50, 200)
    row = np.sum(binary, axis=1)
    col = np.sum(binary, axis=0)
    top = np.nonzero(row)[0][0]
    bottom = np.nonzero(row)[0][-1]
    left = np.nonzero(col)[0][0]
    right = np.nonzero(col)[0][-1]
    left = (right-left)*3//5
    # These number and size are calculated manually to optimize
    # for several images of gatepass (currently tested over 7 variations)
    y_scrap = (bottom-60, bottom-35) # size = 25
    y_return = (bottom-85, bottom-60) # size = 25
    y_qty = (bottom-95, bottom-85) # size = 10
    y_size = (bottom-125, bottom-95) # size = 30
    y_ignore = (bottom-145, bottom-125)
    y_date = (bottom-170, bottom-145) # size = 25
    logger.info('y_scrap = {}\ny_return = {}\ny_qty = {}\ny_size = {}\ny_ignore = {}\ny_date = {}'.format(
        y_scrap, y_return, y_qty, y_size, y_ignore, y_date
    ))
    x = int(left * ratio)
    logger.info('Left = {}'.format(x))
    # date_dispatched = '27/04/2020'
    # max_size = '1280.56'
    # tuff_size = '335.12'
    # binary = ~binary
    # x = np.sum(binary, axis=0)
    # x = x.argsort()[-5:][::-1]
    # right = max(x)
    # left = min(x)
    # x = np.sum(binary, axis=1)
    # x = x.argsort()[-20:][::-1]
    # top = min(x)
    # bottom = max(x)
    test = original.copy()
    # l, t, r, b = get_last_box(binary, right)
    # # test = cv.rectangle(test, (l, t), (r, b), (255, 0, 0), 5)
    # l,t,r,b = get_last_box(binary[:b+10], right)
    # # test = cv.rectangle(test, (l, t), (r, b), (0, 255, 0), 5)
    # x = l+(r-l)//5
    # y = b-(b-t)//3
    # test = cv.putText(test, 'Returned: 0', (x,y), cv.FONT_HERSHEY_SIMPLEX, 3, (0,0,0), 4, cv.LINE_AA)
    y = int((y_return[0]+20) * ratio)
    test = cv.putText(test, 'Returned: 0', (x,y), cv.FONT_HERSHEY_SIMPLEX, 3, (0,0,0), 4, cv.LINE_AA)

    # l,t,r,b = get_last_box(binary[:b+10], right)
    # # test = cv.rectangle(test, (l, t), (r, b), (0, 0, 255), 5)
    # x = l+20
    # y = b-5
    # test = cv.putText(test, 'max: {}, tuff: {}'.format(data['max_qty'],data['tuff_qty']), (x,y), cv.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 4, cv.LINE_AA)
    y = int(y_qty[1] * ratio)
    test = cv.putText(test, 'max: {}, tuff: {}'.format(data['max_qty'],data['tuff_qty']), (x,y), cv.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 4, cv.LINE_AA)
    # l,t,r,b = get_last_box(binary[:b+10], right)
    # # test = cv.rectangle(test, (l, t), (r, b), (0, 0, 255), 5)
    # x = l+(r-l)//7
    # y1 = t+(b-t)//3
    # y2 = b-(b-t)//5
    y1 = int((y_size[0]+15) * ratio)
    y2 = int((y_size[0]+25) * ratio)
    test = cv.putText(test, 'Max-380 : {} Sq.Ft.'.format(data['max_size']), (x,y1), cv.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 4, cv.LINE_AA)
    test = cv.putText(test, 'Tuff-480 : {} Sq.Ft.'.format(data['tuff_size']), (x,y2), cv.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 4, cv.LINE_AA)

    # l,t,r,b = get_last_box(binary[:b+10], right)
    # # test = cv.rectangle(test, (l, t), (r, b), (255, 0, 255), 5)

    # l,t,r,b = get_last_box(binary[:b+10], right)
    # # test = cv.rectangle(test, (l, t), (r, b), (125, 32, 12), 5)
    # x = l+(r-l)//5
    # y = b-(b-t)//3
    y = int((y_date[0]+20) * ratio)
    test = cv.putText(test, data['date'], (x,y), cv.FONT_HERSHEY_SIMPLEX, 3, (0,0,0), 4, cv.LINE_AA)
    # tmp_dir = TemporaryDirectory(prefix='images')
    out_image_path = os.path.join(tmp_dir.name, 'gatepass_processed.jpg')
    cv.imwrite(out_image_path, test)
    return (tmp_dir, out_image_path)
    # plt.imshow(test)
    # plt.show()