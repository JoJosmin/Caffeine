from iris_status import get_iris_status
from cv2 import CAP_PROP_FRAME_HEIGHT, CAP_PROP_FRAME_WIDTH
import torch
import cv2
import numpy as np
from random import choice
import tkinter as tk

SPEED = 1 #스피드 조절 변수

# Make a board
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
iris_x_threshold, iris_y_threshold = 0.15, 0.26
cap = cv2.VideoCapture(0)
iris_status = 'Center'
board = np.uint8(np.zeros([20, 10, 3]))

# Initialize some variables

quit = False
place = False
switch = False
held_piece = ""
flag = 0
score = 0
gameover = ""

# All the tetris pieces
next_piece = choice(["O", "I", "S", "Z", "L", "J", "T"])

def get_info(piece):
    if piece == "I":
        coords = np.array([[0, 3], [0, 4], [0, 5], [0, 6]])
        color = [255, 155, 15]
    elif piece == "T":
        coords = np.array([[1, 3], [1, 4], [1, 5], [0, 4]])
        color = [138, 41, 175]
    elif piece == "L":
        coords = np.array([[1, 3], [1, 4], [1, 5], [0, 5]])
        color = [2, 91, 227]
    elif piece == "J":
        coords = np.array([[1, 3], [1, 4], [1, 5], [0, 3]])
        color = [198, 65, 33]
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


def display(board, coords, color, next_info, held_info, score, SPEED, gameover):
    # Generates the display

    border = np.uint8(127 - np.zeros([20, 1, 3]))
    border_ = np.uint8(127 - np.zeros([1, 34, 3]))

    dummy = board.copy()
    dummy[coords[:,0], coords[:,1]] = color

    right = np.uint8(np.zeros([20, 10, 3]))
    right[next_info[0][:,0] + 2, next_info[0][:,1]] = next_info[1]
    left = np.uint8(np.zeros([20, 10, 3]))
    left[held_info[0][:,0] + 2, held_info[0][:,1]] = held_info[1]

    dummy = np.concatenate((border, left, border, dummy, border, right, border), 1)
    dummy = np.concatenate((border_, dummy, border_), 0)
    dummy = dummy.repeat(20, 0).repeat(20, 1)
    dummy = cv2.putText(dummy, "Score", (515, 200), cv2.FONT_HERSHEY_DUPLEX, 1, [0, 0, 255], 2)
    dummy = cv2.putText(dummy, str(score), (520, 240), cv2.FONT_HERSHEY_DUPLEX, 1, [0, 0, 255], 2)
    dummy = cv2.putText(dummy, str(gameover), (200, 250), cv2.FONT_HERSHEY_DUPLEX, 1.5, [0, 0, 255], 2)

    # Instructions for the player

    dummy = cv2.putText(dummy, "A - move left", (45, 200), cv2.FONT_HERSHEY_DUPLEX, 0.6, [0, 0, 255])
    dummy = cv2.putText(dummy, "D - move right", (45, 225), cv2.FONT_HERSHEY_DUPLEX, 0.6, [0, 0, 255])
    dummy = cv2.putText(dummy, "L - rotate right", (45, 250), cv2.FONT_HERSHEY_DUPLEX, 0.6, [0, 0, 255])
    dummy = cv2.putText(dummy, "BackSpace - quit", (45, 275), cv2.FONT_HERSHEY_DUPLEX, 0.6, [0, 0, 255])

    cv2.namedWindow("Tetris", cv2.WINDOW_NORMAL)

    # 창을 전체 화면으로 설정
    cv2.setWindowProperty("Tetris", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    cv2.imshow("Tetris", dummy)
    key = cv2.waitKey(int(1000/SPEED))

    return key

if __name__ == "__main__":
    while not quit:
        
        # Check if user wants to swap held and current pieces
        if switch:
           # swap held_piece and current_piece
            held_piece, current_piece = current_piece, held_piece
            switch = False
        else:
            # Generates the next piece and updates the current piece
            current_piece = next_piece
            next_piece = choice(["I", "T", "L", "J", "Z", "S", "O"])
        
        if flag > 0:
            flag -= 1
        
        # Determines the color and position of the current, next, and held pieces
        if held_piece == "":
            held_info = np.array([[0, 0]]), [0, 0, 0]
        else:
           held_info = get_info(held_piece)
        
        next_info = get_info(next_piece)

        coords, color = get_info(current_piece)
        if current_piece == "I":
            top_left = [-2, 3]

        if not np.all(board[coords[:,0], coords[:,1]] == 0):
            gameover = "Game over"
            break
            
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
            # Shows the board and gets the key press
            key = display(board, coords, color, next_info, held_info, score, SPEED, gameover)
            # Create a copy of the position
            dummy = coords.copy()
            
        
            if iris_status =="Left":
                # Moves the piece left if it isn't against the left wall
                if np.min(coords[:,1]) > 0:
                    coords[:,1] -= 1
                if current_piece == "I":
                    top_left[1] -= 1
                    
            elif iris_status =="Right":
                # Moves the piece right if it isn't against the right wall
                if np.max(coords[:,1]) < 9:
                    coords[:,1] += 1
                    if current_piece == "I":
                        top_left[1] += 1
                        
            elif key == ord("l"):
                # Rotation mechanism
                # arr is the array of nearby points which get rotated and pov is the indexes of the blocks within arr
                
                if current_piece != "I" and current_piece != "O":
                    if coords[1,1] > 0 and coords[1,1] < 9:
                        arr = coords[1] - 1 + np.array([[[x, y] for y in range(3)] for x in range(3)])
                        pov = coords - coords[1] + 1
                    
                elif current_piece == "I":
                    # The straight piece has a 4x4 array, so it needs seperate code
                    
                    arr = top_left + np.array([[[x, y] for y in range(4)] for x in range(4)])
                    pov = np.array([np.where(np.logical_and(arr[:,:,0] == pos[0], arr[:,:,1] == pos[1])) for pos in coords])
                    pov = np.array([k[0] for k in np.swapaxes(pov, 1, 2)])
            
                # Rotates the array and repositions the piece to where it is now
                
                if current_piece != "O":
                    if key == ord("l"):
                        arr = np.rot90(arr)
                    else:
                        arr = np.rot90(arr ,-1)
                    coords = arr[pov[:,0], pov[:,1]]

            elif key == 8 or key == 27:
                quit = True
                break
                
            # Checks if the piece is overlapping with other pieces or if it's outside the board, and if so, changes the position to the position before anything happened
                        
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
                # Places the piece where it is on the board
                for pos in coords:
                    board[tuple(pos)] = color
                    
                # Resets place to False
                place = False
                break

            # Moves down by 1

            coords[:,0] += 1
            if current_piece == "I":
                top_left[0] += 1
        
        # Clears lines and also counts how many lines have been cleared and updates the score
    
        lines = 0
                
        for line in range(20):
            if np.all([np.any(pos != 0) for pos in board[line]]):
                lines += 1
                board[1:line+1] = board[:line]
                        
        if lines >= 1:
            score += lines*10

        if 10<= score < 50:
            SPEED = 2
        elif 30 <= score < 100:
            SPEED = 3
        elif 150 <= score < 200:
            SPEED = 4
        elif score >= 200:
            SPEED = 5 
    dummy = display(board, coords, color, next_info, held_info, score, SPEED, gameover)
    cv2.waitKey()