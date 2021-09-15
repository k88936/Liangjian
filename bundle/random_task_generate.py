import numpy as np
from math import floor
print(int(floor(max(12, 7) / 5) * 5))

lenx = 5
leny = 5
occupied_node_list = [(0, 0)]
number_of_agv = 1
while number_of_agv <= 50:
    out_put_str = ''
    start_point_x = 0
    start_point_y = 0
    dire1 = 0
    while (start_point_x, start_point_y) in occupied_node_list:
        x = np.random.randint(1, lenx + 1, 1)
        y = np.random.randint(1, leny + 1, 1)
        dire1 = np.random.randint(0, 4, 1)
        if dire1 == 0:
            start_point_x = (x-1)*5 + 4
            start_point_y = (y-1)*5 + np.random.randint(2, 4, 1)
        if dire1 == 1:
            start_point_x = (x-1)*5 + np.random.randint(2, 4, 1)
            start_point_y = (y-1)*5 + 1
        if dire1 == 2:
            start_point_x = (x-1)*5 + 1
            start_point_y = (y-1)*5 + np.random.randint(2, 4, 1)
        if dire1 == 3:
            start_point_x = (x-1)*5 + np.random.randint(2, 4, 1)
            start_point_y = (y-1)*5 + 4
    occupied_node_list.append((start_point_x, start_point_y))

    end_point_x = 0
    end_point_y = 0
    dire2 = 0
    while (end_point_x, end_point_y) in occupied_node_list:
        x = np.random.randint(1, lenx + 1, 1)
        y = np.random.randint(1, leny + 1, 1)
        dire2 = np.random.randint(0, 4, 1)
        if dire2 == 0:
            end_point_x = (x - 1) * 5 + 4
            end_point_y = (y - 1) * 5 + np.random.randint(2, 4, 1)
        if dire2 == 1:
            end_point_x = (x - 1) * 5 + np.random.randint(2, 4, 1)
            end_point_y = (y - 1) * 5 + 1
        if dire2 == 2:
            end_point_x = (x - 1) * 5 + 1
            end_point_y = (y - 1) * 5 + np.random.randint(2, 4, 1)
        if dire2 == 3:
            end_point_x = (x - 1) * 5 + np.random.randint(2, 4, 1)
            end_point_y = (y - 1) * 5 + 4
    occupied_node_list.append((end_point_x, end_point_y))
    out_put_str += str(number_of_agv) + ': {"robot_id": ' + str(number_of_agv) + ', "x": ' + str(start_point_x[0]) + ', "y": ' + str(
        start_point_y[0]) + ', "destX": ' + str(end_point_x[0]) + ', "destY": ' + str(end_point_y[0]) + ', "endDirection": ' + str(dire2[0]) + ', "direction": ' + str(dire1[0]) + '},'
    print(out_put_str)
    number_of_agv += 1

