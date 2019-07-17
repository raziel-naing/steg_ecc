import random
import math

def init_curve():
    curve = []
    P = []

    cnt = 0
    while (True):
        # create curve
        while (True):
            a = random.randint(0, 8)
            b = random.randint(0, 8)

            discriminant = (4 * pow(a, 3)) + (27 * pow(b, 2))

            if (discriminant != 0):
                curve.append(a)
                curve.append(b)
                break


        # find multiple root
        while (True):
            a = random.randint(0, 8)

            for i in range(20):
                b = random.randint(1, 8)
                y = pow(a, 3) + (curve[0] * a) + curve[1] - pow(b, 2)
                cnt += 1

                if (y == 0):
                    P.append(a)
                    P.append(b)
                    break

            if (P != []):
                break
            if (cnt == 100000):
                break

        if (cnt == 100000):
            cnt = 0
            curve = []
            continue
        else:
            break

    print("Curve :", curve)
    print("P :", P)

    return curve, P

def calc_eliptic(curve, P, Q):
    R = []

    # calc m
    if (P == Q):
        m = (3*(pow(P[0], 2)) + curve[0]) / (2 * P[1])
    else :
        m = (P[1] - Q[1]) / (P[0] - Q[0])

    # calc R
    R.append(pow(m, 2) - P[0] - Q[0])
    R.append((P[1] + m*(R[0] - P[0]))*-1)

    # return R
    return R

def calc_writeOff(curve, P, Q, text_len, data_len):
    writeOff_arr = []
    cnt = 0
    firstP = P

    while(True):
        res = calc_eliptic(curve, P, Q)
        P = Q
        Q = res

        # if [1, 2], data is written at line 1, col 2
        # so 16 + 2, offset : start point + 18
        writePt = [abs(math.floor(res[0])), math.floor((res[1] % 16))]
        writeOff = (writePt[0] * 16) + writePt[1]

        # data_len > len(writeOff_arr)
        if ((P[0] - Q[0]) == 0):
            print("\nrecalculation")
            curve, P = init_curve()
            writeOff_arr = calc_writeOff(curve, P, P, text_len, data_len)
            return writeOff_arr, curve, P

        if (writeOff >= (data_len - 0x36)):
            continue

        try:
            temp = writeOff_arr.index(writeOff)
        except:
            writeOff_arr.append(writeOff)

            cnt += 1
            if (cnt == text_len):
                break



    print("writeOff_arr :", writeOff_arr)
    print("writeOff_arr's len :", len(writeOff_arr))

    return writeOff_arr, curve, firstP

def write_meta(curve, P, data):
    reserved1_off = 0x06
    reserved2_off = 0x08

    for i in range(2):
        data[reserved1_off + i] = curve[i]
        data[reserved2_off + i] = P[i]

    return data

def read_meta(data):
    reserved1_off = 0x06
    reserved2_off = 0x08

    curve = []
    P = []

    for i in range(2):
        curve.append(data[reserved1_off + i])
        P.append(data[reserved2_off + i])

    return curve, P

def calc_writeOff_unhide(curve, P, Q, data_len):
    writeOff_arr = []
    cnt = 0

    while(True):
        res = calc_eliptic(curve, P, Q)
        P = Q
        Q = res

        # if [1, 2], data is written at line 1, col 2
        # so 16 + 2, offset : start point + 18
        writePt = [abs(math.floor(res[0])), math.floor((res[1] % 16))]
        writeOff = (writePt[0] * 16) + writePt[1]

        # data_len > len(writeOff_arr)
        if ((P[0] - Q[0]) == 0):
            break

        if (writeOff >= (data_len - 0x36)):
            continue

        try:
            temp = writeOff_arr.index(writeOff)
        except:
            writeOff_arr.append(writeOff)

            cnt += 1
            if (cnt == data_len):
                break

    print("writeOff_arr :", writeOff_arr)
    print("writeOff_arr's len :", len(writeOff_arr))

    return writeOff_arr
