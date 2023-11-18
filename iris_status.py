def get_iris_status(eye_list, iris_list, iris_x_threshold, iris_y_threshold):
    if len(eye_list) == 2 and len(iris_list) == 2:
        left_part = []
        right_part = []
        if eye_list[0]['xmin'] > eye_list[1]['xmin']:
            right_part.append(eye_list[0])
            left_part.append(eye_list[1])
        else:
            right_part.append(eye_list[1])
            left_part.append(eye_list[0])
        if iris_list[0]['xmin'] > iris_list[1]['xmin']:
            right_part.append(iris_list[0])
            left_part.append(iris_list[1])
        else:
            right_part.append(iris_list[1])
            left_part.append(iris_list[0])

        left_x_iris_center = (left_part[1]['xmin'] + left_part[1]['xmax']) / 2
        left_x_per = (left_x_iris_center - left_part[0]['xmin']) / (left_part[0]['xmax'] - left_part[0]['xmin'])
        left_y_iris_center = (left_part[1]['ymin'] + left_part[1]['ymax']) / 2
        left_y_per = (left_y_iris_center - left_part[0]['ymin']) / (left_part[0]['ymax'] - left_part[0]['ymin'])

        right_x_iris_center = (right_part[1]['xmin'] + right_part[1]['xmax']) / 2
        right_x_per = (right_x_iris_center - right_part[0]['xmin']) / (right_part[0]['xmax'] - right_part[0]['xmin'])
        right_y_iris_center = (right_part[1]['ymin'] + right_part[1]['ymax']) / 2
        right_y_per = (right_y_iris_center - right_part[0]['ymin']) / (right_part[0]['ymax'] - right_part[0]['ymin'])

        avr_x_iris_per = (left_x_per + right_x_per) / 2
        avr_y_iris_per = (left_y_per + right_y_per) / 2

        if avr_x_iris_per < (0.5 - iris_x_threshold):
            return 'Left'
        elif avr_x_iris_per > (0.5 + iris_x_threshold):
            return 'Right'
        # elif avr_y_iris_per < (0.5 - iris_y_threshold):
        #     return 'Up'
        # elif avr_y_iris_per > (0.5 + iris_y_threshold):
        #     return 'Down'
        else:
            return 'Center'
    else:
        return 'Blink'