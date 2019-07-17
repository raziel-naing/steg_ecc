import eliptic

def open_bmp(file_name):
    with open(file_name, "rb") as file:
        data = file.read()

        return data


def save_bmp(file_name, steg_bmp):
    with open(file_name, "wb") as file:
        file.write(steg_bmp)


def read_header(data):
    bmp_headerchk = 0x424d

    header = data[0:14]
    header = (data[0] << 8) + (data[1])
    size = (data[5] << 24) + (data[4] << 16) + (data[3] << 8) + (data[2])
    offset = data[10]

    if (header != bmp_headerchk):
        print("Target file format is not bitmap.")
        return -1

    print("Header of target file is", header)
    print("Size of target file is", size)
    print("Start offset of target file's pixel area is", offset)

    return header, size, offset

def steg_hide(file_name, msg):
    # Open bitmap image
    bmp_data = open_bmp(file_name)

    # Get bitmap data
    bmp_header, bmp_size, bmp_offset = read_header(bmp_data)

    New_filedata = list(bmp_data)

    bytemsg = ""
    print("MSG ",msg)
    #pw = b'My private key'
    #ciphertext = encrypt_msg(msg,pw)
    #print(ciphertext)
    for x in msg:
        bytex = format(ord(x), 'b')
        clen = len(bytex)

        if clen%4 != 0:
            lacknum = 4 - clen%4
            new_msg = ""
            for i in range(lacknum):
                new_msg += "0"
            new_msg += bytex

        bytemsg += new_msg

    tlen = len(bytemsg)
    if (bmp_size - bmp_offset - 1 < tlen):
        print("The text is lager than image.")
        return -1

    print("Length of the text to hide is", tlen)

    curve, P = eliptic.init_curve()
    writeOff_arr, curve, P = eliptic.calc_writeOff(curve, P, P, tlen, bmp_size)
    New_filedata = eliptic.write_meta(curve, P, New_filedata)

    for i in range(tlen):
        if ((New_filedata[writeOff_arr[i] + bmp_offset] % 2) == 0):
            New_filedata[writeOff_arr[i] + bmp_offset] = New_filedata[writeOff_arr[i] + bmp_offset] | int(bytemsg[i])
        else:
            New_filedata[writeOff_arr[i] + bmp_offset] = New_filedata[writeOff_arr[i] + bmp_offset] & int(bytemsg[i])

    new_bmp = bytearray(New_filedata)
    save_bmp("steg_battery.bmp", new_bmp)


def steg_unhide(file_name):
    # Open bitmap image
    bmp_data = open_bmp(file_name)
    filedata = list(bmp_data)

    # Get bitmap data
    bmp_header, bmp_size, bmp_offset = read_header(bmp_data)
    print(bmp_header, bmp_size, bmp_offset)

    curve, P = eliptic.read_meta(filedata)
    print("curve :", curve)
    print("P :", P)

    # calc text writed point
    writeOff_arr = eliptic.calc_writeOff_unhide(curve, P, P, bmp_size)

    hiddenMsg = ""

    temp = 0
    for i in range(len(writeOff_arr)):
        temp = temp << 1
        tempchar = bmp_data[writeOff_arr[i]+bmp_offset] & 1
        temp = temp + tempchar

        if (i%8 == 7 and i != 0):
            if (temp < 128):
                hiddenMsg += chr(temp)
            temp = 0
    pw = b'My private key'
    #hiddenMsg=decrypt_msg(hiddenMsg,pw)
    # Write hidden text
    with open("hidden_msg.txt", "w") as file:
        file.write(hiddenMsg)


def main():
    # Hide text message to image
    print("steg_hide")
    steg_hide("battery.bmp", "abcdefg")

    # Unhide text message from image
    print("\nsteg_unhide")
    steg_unhide("steg_battery.bmp")

    return 0


main()