from iris_status import get_iris_status
from cv2 import CAP_PROP_FRAME_HEIGHT, CAP_PROP_FRAME_WIDTH
import torch
import cv2
import numpy as np
from random import choice
import tkinter as tk

SPEED = 2 #스피드 조절 변수

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

# 변수 선언

model = torch.hub.load('ultralytics/yolov5', 'custom', path='./best_epoch150.pt')
model.conf = 0.3
model.iou = 0
resize_rate = 1
iris_x_threshold, iris_y_threshold = 0.10, 0.20
cap = cv2.VideoCapture(0)
iris_status = 'Center'
board = np.uint8(np.zeros([20, 10, 3]))

quit = False
place = False
switch = False
held_piece = ""
flag = 0
score = 0
gameover = ""
navigate = ""

# 테트리스 블럭 구현
next_piece = choice(["O", "I", "S", "Z", "L", "J", "T"])

def get_info(piece):
    if piece == "I":
        coords = np.array([[0, 3], [0, 4], [0, 5], [0, 6]])
        color = [255, 155, 15]
    elif piece == "T":
        coords = np.array([[1, 3], [1, 4], [1, 5], [0, 4]])
        color = [100, 1, 40]
    elif piece == "L":
        coords = np.array([[1, 3], [1, 4], [1, 5], [0, 5]])
        color = [2, 91, 227]
    elif piece == "J":
        coords = np.array([[1, 3], [1, 4], [1, 5], [0, 3]])
        color = [200, 0, 200]
    elif piece == "S":
        coords = np.array([[1, 5], [1, 4], [0, 3], [0, 4]])
        color = [55, 15, 215]
    elif piece == "Z":
        coords = np.array([[1, 3], [1, 4], [0, 4], [0, 5]])
        color = [1, 177, 89]
    else:
        coords = np.array([[0, 4], [0, 5], [1, 4], [1, 5]])
        color = [2, 159, 227]

    return coords, color

#보드 생성 
def display(board, coords, color, next_info, held_info, score, SPEED, gameover, navigate):

    border = np.uint8(np.array([163, 49, 12]) * np.ones([20, 1, 3])) 
    border_ = np.uint8(np.array([163, 49, 12]) * np.ones([1, 34, 3]))  

    dummy = board.copy()
    dummy[coords[:,0], coords[:,1]] = color

    right = np.uint8(np.zeros([20, 10, 3]))
    right[next_info[0][:,0] + 9, next_info[0][:,1]] = next_info[1]
    left = np.uint8(np.zeros([20, 10, 3]))
    left[held_info[0][:,0] + 2, held_info[0][:,1]] = held_info[1]

    font = cv2.FONT_HERSHEY_SIMPLEX

    dummy = np.concatenate((border, left, border, dummy, border, right, border), 1)
    dummy = np.concatenate((border_, dummy, border_), 0)
    dummy = dummy.repeat(20, 0).repeat(20, 1)   
    dummy = cv2.putText(dummy, "Score", (515, 330), font, 1, [255, 204, 153], 2)
    dummy = cv2.putText(dummy, str(score), (520, 370), font, 1, [255, 204, 153], 2)
    dummy = cv2.putText(dummy, str(gameover), (200, 250), font, 1.5, [0, 0, 255], 3)
    dummy = cv2.putText(dummy, str(navigate), (50, 290), font, 1.5, [0, 0, 255], 3)

    dummy = cv2.putText(dummy, "<<", (40, 140), font, 1, [255, 102, 51], 5)
    dummy = cv2.putText(dummy, ">>", (590, 140), font, 1, [255, 102, 51], 5)

    # Instructions for the player

    dummy = cv2.putText(dummy, "look left - move left", (45, 200), font, 0.4, [255, 204, 153])
    dummy = cv2.putText(dummy, "look right - move right", (45, 225), font, 0.4, [255, 204, 153])
    dummy = cv2.putText(dummy, "blink - rotate right", (45, 250), font, 0.4, [255, 204, 153])
    dummy = cv2.putText(dummy, "BackSpace - quit", (45, 275), font, 0.4, [255, 204, 153])

    cv2.namedWindow("Tetris", cv2.WINDOW_NORMAL)

    # 창을 전체 화면으로 설정
    cv2.setWindowProperty("Tetris", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    cv2.imshow("Tetris", dummy)
    key = cv2.waitKey(int(1000/SPEED))

    return key

if __name__ == "__main__":
    while not quit:
        
        if switch:
            held_piece, current_piece = current_piece, held_piece
            switch = False
        else:
            current_piece = next_piece
            next_piece = choice(["I", "T", "L", "J", "Z", "S", "O"])
        
        if flag > 0:
            flag -= 1
        
        if held_piece == "":
            held_info = np.array([[0, 0]]), [0, 0, 0]
        else:
           held_info = get_info(held_piece)
        
        next_info = get_info(next_piece)

        coords, color = get_info(current_piece)
        if current_piece == "I":
            top_left = [-2, 3]

        #화면을 벗어날 정도로 블럭이 높게 쌓이면 Game over
        if not np.all(board[coords[:,0], coords[:,1]] == 0):
            gameover = "Game over"
            navigate="Press any key to restart"
            key = display(board, coords, color, next_info, held_info, score, SPEED, gameover, navigate)
            # game over가 된 후, 아무 키보드의 입력이 들어오면 게임이 재시작하게 구현
            while True:
                if key != -1 and key != 8:
                    break
                key = display(board, coords, color, next_info, held_info, score, SPEED, gameover, navigate)

            # 게임 재시작을 위해 변수 초기화
            board = np.zeros((20, 10, 3), dtype=np.uint8)
            coords = np.array([[0, 3], [1, 3], [2, 3], [3, 3]])
            color = [0, 255, 255]
            next_piece = choice(["I", "T", "L", "J", "Z", "S", "O"])
            held_piece = ""
            held_info = np.array([[0, 0]]), [0, 0, 0]
            score = 0
            SPEED = 1
            gameover = ""
            navigate = ""
            continue
            
        while True:

            #시선을 입력받기 위한 설정
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
            #보드를 생성 후 키보드 입력을 기다림
            key = display(board, coords, color, next_info, held_info, score, SPEED, gameover, navigate)
            dummy = coords.copy()
            
        
            if iris_status =="Left":
                # 왼쪽을 응시하면 블럭이 왼쪽으로 이동(왼쪽 벽을 만나면 더이상 왼쪽으로 가지 않음)
                if np.min(coords[:,1]) > 0:
                    coords[:,1] -= 1
                if current_piece == "I":
                    top_left[1] -= 1
                    
            elif iris_status =="Right":
                # 오른쪽을 응시하면 블럭이 오른쪽으로 이동(오른쪽 벽을 만나면 더이상 오른쪽으로 가지 않음)
                if np.max(coords[:,1]) < 9:
                    coords[:,1] += 1
                    if current_piece == "I":
                        top_left[1] += 1
                        
            elif iris_status =="Blink":
                ##눈을 깜빡이면 블럭이 시계방향으로 회전
                #저장되어 있는 회전 모습 array 사용
                if current_piece != "I" and current_piece != "O":
                    # 일자 블럭과, 정사각형 블럭의 경우 따로 처리 (회전 시 모양이 2개로 한정되어있기 때문)
                    if coords[1,1] > 0 and coords[1,1] < 9:
                        arr = coords[1] - 1 + np.array([[[x, y] for y in range(3)] for x in range(3)])
                        pov = coords - coords[1] + 1
                    
                elif current_piece == "I":
                    
                    arr = top_left + np.array([[[x, y] for y in range(4)] for x in range(4)])
                    pov = np.array([np.where(np.logical_and(arr[:,:,0] == pos[0], arr[:,:,1] == pos[1])) for pos in coords])
                    pov = np.array([k[0] for k in np.swapaxes(pov, 1, 2)])
            
                
                if current_piece != "O":
                    if key == ord("l"):
                        arr = np.rot90(arr)
                    else:
                        arr = np.rot90(arr ,-1)
                    coords = arr[pov[:,0], pov[:,1]]
            
            # cv2.putText(img, 'Iris Direction: {}'.format(iris_status),(10, 40), cv2.FONT_HERSHEY_COMPLEX, 1, (30, 30, 30), 2)
            # cv2.imshow('img', img)
            if key == 8 or key == 27:
                quit = True
                break
            
            if np.max(coords[:,0]) < 20 and np.min(coords[:,0]) >= 0:
                if not (current_piece == "I" and (np.max(coords[:,1]) >= 10 or np.min(coords[:,1]) < 0)):
                    if not np.all(board[coords[:,0], coords[:,1]] == 0):
                        coords = dummy.copy()
                else:
                    coords = dummy.copy()
            else:
                coords = dummy.copy()
                
            if np.max(coords[:,0]) != 19:
                for pos in coords:
                    if not np.array_equal(board[pos[0] + 1, pos[1]], [0, 0, 0]):
                        place = True
                        break
            else:
                place = True
                
            if place:
                #바닥을 만날경우 더이상 진행되지 않고 블럭이 고정되게 함
                for pos in coords:
                    board[tuple(pos)] = color
                    
                place = False
                break

            #바닥을 만나지 않을 경우 1라인씩 내려감
            coords[:,0] += 1
            if current_piece == "I":
                top_left[0] += 1
        
        #한 행이 꽉 차면 사라지면서 score 10추가
        lines = 0
                
        for line in range(20):
            if np.all([np.any(pos != 0) for pos in board[line]]):
                lines += 1
                board[1:line+1] = board[:line]
                        
        if lines >= 1:
            score += lines*10

        #점수에 따른 속도 차이구현
        if 10<= score < 20:
            SPEED = 2
        elif 20 <= score < 40:
            SPEED = 3
        elif 40 <= score < 60:
            SPEED = 4
        elif score >= 60:
            SPEED = 5 
    dummy = display(board, coords, color, next_info, held_info, score, SPEED, gameover, navigate)
    cv2.waitKey()
    
