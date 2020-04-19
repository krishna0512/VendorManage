import cv2 as cv
import numpy as np
# import matplotlib.pyplot as plt
from tempfile import TemporaryDirectory
import os

def get_last_box(binary, right):
    x = np.sum(binary, axis=1)
    x = x.argsort()[-20:][::-1]
    x = np.sort(x)[::-1]
    t = 1
    while abs(x[t]-x[0]) < 10:
        t += 1
    bottom = x[t]
    while abs(x[t]-bottom) < 10:
        t += 1
    top = x[t]
    left = binary.shape[1]//2
    return left, top, right, bottom

def main(input_image_path, data=None):
    # image = cv.imread('test2.jpg')
    image = cv.imread(input_image_path)
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    _, binary = cv.threshold(gray, 100, 255, cv.THRESH_BINARY)
    date_dispatched = '27/04/2020'
    max_size = '1280.56'
    tuff_size = '335.12'
    binary = ~binary
    x = np.sum(binary, axis=0)
    x = x.argsort()[-5:][::-1]
    right = max(x)
    left = min(x)
    x = np.sum(binary, axis=1)
    x = x.argsort()[-20:][::-1]
    top = min(x)
    bottom = max(x)
    test = image.copy()
    l, t, r, b = get_last_box(binary, right)
    # test = cv.rectangle(test, (l, t), (r, b), (255, 0, 0), 5)
    l,t,r,b = get_last_box(binary[:b+10], right)
    # test = cv.rectangle(test, (l, t), (r, b), (0, 255, 0), 5)
    x = l+(r-l)//5
    y = b-(b-t)//3
    test = cv.putText(test, 'Returned: 0', (x,y), cv.FONT_HERSHEY_SIMPLEX, 3, (0,0,0), 4, cv.LINE_AA)

    l,t,r,b = get_last_box(binary[:b+10], right)
    # test = cv.rectangle(test, (l, t), (r, b), (0, 0, 255), 5)
    x = l+20
    y = b-5
    test = cv.putText(test, 'max: {}, tuff: {}'.format(data['max_qty'],data['tuff_qty']), (x,y), cv.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 4, cv.LINE_AA)
    l,t,r,b = get_last_box(binary[:b+10], right)
    # test = cv.rectangle(test, (l, t), (r, b), (0, 0, 255), 5)
    x = l+(r-l)//7
    y1 = t+(b-t)//3
    y2 = b-(b-t)//5
    test = cv.putText(test, 'Max-380 : {} Sq.Ft.'.format(data['max_size']), (x,y1), cv.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 4, cv.LINE_AA)
    test = cv.putText(test, 'Tuff-480 : {} Sq.Ft.'.format(data['tuff_size']), (x,y2), cv.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 4, cv.LINE_AA)

    l,t,r,b = get_last_box(binary[:b+10], right)
    # test = cv.rectangle(test, (l, t), (r, b), (255, 0, 255), 5)

    l,t,r,b = get_last_box(binary[:b+10], right)
    # test = cv.rectangle(test, (l, t), (r, b), (125, 32, 12), 5)
    x = l+(r-l)//5
    y = b-(b-t)//3
    # print(x,y)
    test = cv.putText(test, data['date'], (x,y), cv.FONT_HERSHEY_SIMPLEX, 3, (0,0,0), 4, cv.LINE_AA)
    tmp_dir = TemporaryDirectory(prefix='images')
    out_image_path = os.path.join(tmp_dir.name, 'test.jpg')
    cv.imwrite(out_image_path, test)
    return (tmp_dir, out_image_path)
    # return test
    # plt.imshow(test)
    # plt.show()

# if __name__ == '__main__':
#     main()