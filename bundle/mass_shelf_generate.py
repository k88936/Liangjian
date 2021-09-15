startX = 6
startY = 1
pickTime = 20
districtLength = 5
dX = 3
dY = 3
shelf_count = 0


def shelfNumberToStr(n):
    re = ""
    if n < 10:
        re = "A000" + str(n)
    if 10 <= n < 100:
        re = "A00" + str(n)
    if 100 <= n < 1000:
        re = "A0" + str(n)
    if n >= 1000:
        re = "A" + str(n)
    return re


for x in range(dX):
    for y in range(dY):
        districtX = startX + x * districtLength
        districtY = startY + y * districtLength
        for m in range(districtLength - 1):
            shelf_count += 1
            shelfX = districtX + m
            shelfY = districtY
            shelfId = shelfNumberToStr(shelf_count)
            out_put_str = '"' + shelfId + '"' + ': {"shelfCode": ' + '"' + shelfId + '"' + ', "pickTime": ' + str(pickTime) + ', "x": ' + str(
                shelfX) + ', "y": ' + str(shelfY) + ', "targetArea": ' + str([]) + ', "shelfFaceCode": "F" ' + '},'
            print(out_put_str)
        for m in [0, districtLength-2]:
            for n in range(1, districtLength-2):
                shelf_count += 1
                shelfX = districtX + m
                shelfY = districtY + n
                shelfId = shelfNumberToStr(shelf_count)
                out_put_str = '"' + shelfId + '"' + ': {"shelfCode": ' + '"' + shelfId + '"' + ', "pickTime": ' + str(pickTime) + ', "x": ' + str(
                    shelfX) + ', "y": ' + str(shelfY) + ', "targetArea": ' + str([]) + ', "shelfFaceCode": "F" ' + '},'
                print(out_put_str)
        for m in range(districtLength - 1):
            shelf_count += 1
            shelfX = districtX + m
            shelfY = districtY + districtLength-2
            shelfId = shelfNumberToStr(shelf_count)
            out_put_str = '"' + shelfId + '"' + ': {"shelfCode": ' + '"' + shelfId + '"' + ', "pickTime": ' + str(pickTime) + ', "x": ' + str(
        shelfX) + ', "y": ' + str(shelfY) + ', "targetArea": ' + str([]) + ', "shelfFaceCode": "F" ' + '},'
            print(out_put_str)

