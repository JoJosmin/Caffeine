from iris_status import get_iris_status
from cv2 import CAP_PROP_FRAME_HEIGHT, CAP_PROP_FRAME_WIDTH
import torch
import cv2

def yolo_process(img):
    yolo_results = model(img)
    df = yolo_results.pandas().xyxy[0]
    obj_list = []
    for i in range(len(df)) :
        obj_confi = round(df['confidence'][i], 2)
        obj_name = df['name'][i]
        x_min = int(df['xmin'][i])
        y_min = int(df['ymin'][i])
        x_max = int(df['xmax'][i])
        y_max = int(df['ymax'][i])
        obj_dict = {
            'class' : obj_name, 
            'confidence' : obj_confi,
            'xmin' : x_min,
            'ymin' : y_min,
            'xmax' : x_max, 
            'ymax' : y_max
        }
        obj_list.append(obj_dict)
    return obj_list

model = torch.hub.load('ultralytics/yolov5', 'custom', path='./best_epoch150.pt')
model.conf = 0.3
model.iou = 0
resize_rate = 1
iris_x_threshold, iris_y_threshold = 0.10, 0.20
cap = cv2.VideoCapture(0)
iris_status = 'Center'

while True:
    ret, img = cap.read()
    if not ret == True:
        break
    imgS = cv2.resize(img, (0, 0), None, resize_rate, resize_rate)
    results = yolo_process(imgS)

    eye_list = []
    iris_list = []

    for result in results:
        xmin_resize = int(result['xmin'] / resize_rate)
        ymin_resize = int(result['ymin'] / resize_rate)
        xmax_resize = int(result['xmax'] / resize_rate)
        ymax_resize = int(result['ymax'] / resize_rate)
        if result['class'] == 'eye':
            pass
        if result['class'] == 'iris':
            x_length = xmax_resize - xmin_resize
            y_length = ymax_resize - ymin_resize
            circle_r = int((x_length + y_length) / 4)
            x_center = int((xmin_resize + xmax_resize) / 2)
            y_center = int((ymin_resize + ymax_resize) / 2)
            cv2.circle(img, (x_center, y_center), circle_r, (255, 255, 255), 1)
        if result['class'] == 'eye':
            eye_list.append(result)
        elif result['class'] == 'iris':
            iris_list.append(result)

    iris_status = get_iris_status(eye_list, iris_list, iris_x_threshold, iris_y_threshold)

    cv2.putText(img, 'Iris Direction: {}'.format(iris_status),(10, 40), cv2.FONT_HERSHEY_COMPLEX, 1, (30, 30, 30), 2)
    cv2.imshow('img', img)
    cv2.waitKey(1)

cv2.destroyAllWindows()
