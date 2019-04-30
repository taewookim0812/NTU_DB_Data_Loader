# -*- coding: utf-8 -*-
"""
NTU_DB Data Loader

@author: Taewoo Kim
e-mail: twkim0812@gmail.com
"""

from Skeleton import Skeleton, Category, Body_struct, Joint_struct

# ------------------------------------------------------------------------------------
# ----------------------------------- Main Code --------------------------------------
# ------------------------------------------------------------------------------------
"""
***Notice
Before you use this code, Your NTU database files should be ordered as following.
Example)
/*your own path */NTU_DB/Daily_Actions/A022
/*your own path */NTU_DB/Medical_Conditions/A041
/*your own path */NTU_DB/Mutual_Conditions/A050
...

The pairs of video clip and skeleton file corresponding to each action class should be in each subfolder.
Example)
In /*your own path */NTU_DB/Daily_Actions/A022, it contains..
S001C001P001R001A022_rgb.avi, S001C001P001R001A022.skeleton, ...  
"""

# display RGB image with skeleton
import numpy as np
import cv2
import os, glob, random
print('OpenCV version: ', cv2.__version__)

# NTU DB were captured by Kinect-v2 with 30Hz
# What classes we hold
# [A022: cheer up, A023: hand waving, A031: pointing to something with finger]
# [A034: rub two hands together, A035: nod head/bow, A036: shake head, A038: salute]
S = 'S' + '{0:03}'.format(1)  # Setup Number
C = 'C' + '{0:03}'.format(1)  # Camera ID
P = 'P' + '{0:03}'.format(1)  # Performer ID
R = 'R' + '{0:03}'.format(1)  # Replication Number

"""
Key Configuration
E: forward
Q: backward
X: mark current video clip to be excluded
Z: mark current video clip to be included from the exception file list
"""

# ****************************************************
# ***** Main Control Parameter for NTU-DB Search *****
# ****************************************************
show_mode = 0   # 0: show all data, 1: show only good, 2:show only bad
save_exception_list = True    # save exception file list

iAction = 31                   # Action class number
# ****************************************************

# set file path
A = 'A' + '{0:03}'.format(iAction)  # Action class label
my_path = '/dd/'                                # TODO, change the '/dd/' to your own path
category = Category()
categ = ''  # category w.r.t actions
if iAction <= 40:
    categ = category.daily_action
elif iAction > 40 and iAction <= 49:
    categ = category.medical_conditions
else:
    categ = category.mutual_conditions

print('category: ', categ)
file_path = os.path.join(my_path, 'NTU_DB', categ, A)
video_file_list = sorted(glob.glob(file_path + "/*.avi"))
skeleton_file_list = sorted(glob.glob(file_path + "/*.skeleton"))
print('video len: ', len(video_file_list))
print('skeleton len: ', len(skeleton_file_list))

# MATLAB based index, thus, -1 should be added in python-like index.
connecting_joint = [2, 1, 21, 3, 21, 5, 6, 7, 21, 9, 10, 11, 1, 13, 14, 15, 1, 17, 18, 19, 2, 8, 8, 12, 12]
exception_avi_list = []
exception_skel_list = []

if show_mode > 0:
    with open(A+'_exeception_avi_list.txt', 'r') as f_avi:
        exception_avi_list = f_avi.read().splitlines()

    with open(A+'_exeception_skeleton_list.txt', 'r') as f_skel:
        exception_skel_list = f_skel.read().splitlines()

    if show_mode == 1:
        # exclude exception files
        for i in range(len(exception_avi_list)):
            exc_file = exception_avi_list[i].replace('\n', '')
            if exc_file in video_file_list: video_file_list.remove(exc_file)
        for i in range(len(exception_skel_list)):
            exc_file = exception_skel_list[i].replace('\n', '')
            if exc_file in skeleton_file_list: skeleton_file_list.remove(exc_file)

    elif show_mode == 2:
        # include only exception files
        exc_avi_file = []
        for i in range(len(exception_avi_list)):
            if exception_avi_list[i].replace('\n', '') != '':
                exc_avi_file.append(exception_avi_list[i].replace('\n', ''))
        exc_skel_file = []
        for i in range(len(exception_skel_list)):
            if exception_skel_list[i].replace('\n', '') != '':
                exc_skel_file.append(exception_skel_list[i].replace('\n', ''))
        video_file_list = exc_avi_file
        skeleton_file_list = exc_skel_file

print('Filtered video len: ', len(video_file_list))
print('Filtered skeleton len: ', len(skeleton_file_list))

# -----[ Video Play Control Parameters ]-----
index = 0
backward = False
stop = False
frame_rate = 30     # Hz
period = int((1.0/frame_rate) * 1000)

# -----[ Main Loop ]-----
while index < len(video_file_list):
    # -----------------------
    # -----[ Data Load ]-----
    # -----------------------
    print('list number: ', index, ' progress: {0:0.2f}'.format((index/len(video_file_list) * 100.0)),
          ' in ', len(video_file_list))
    print('video: ', video_file_list[index])
    print('skeleton: ', skeleton_file_list[index])

    cap = cv2.VideoCapture(video_file_list[index])
    file = open(skeleton_file_list[index])

    frameCount = np.fromstring(file.readline(), sep=' ', dtype='int32')[0]
    skel = Skeleton()
    for f in range(frameCount):  # frameCount
        bodyCount = np.fromstring(file.readline(), sep=' ', dtype='int32')[0]

        for b in range(bodyCount):
            body = Body_struct()
            bodyInfo = np.fromstring(file.readline(), sep=' ', dtype='float64')
            jointCount = np.fromstring(file.readline(), sep=' ', dtype='int32')[0]
            body.set_body_info(bodyInfo, jointCount, f*1.0/frameCount)

            for j in range(jointCount):
                jointInfo = np.fromstring(file.readline(), sep=' ', dtype='float64')
                joint = Joint_struct(jointInfo)
                body.joints.append(joint)
            skel.append_body(f, b, body)
    file.close()

    # print(skel.print_skeleton_info())

    # ----------------------------------------
    # -----[ Display Image and Skeleton ]-----
    # ----------------------------------------
    fCount = 0  # frame count
    while(cap.isOpened()):
        ret, frame = cap.read()

        try:
            # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            for i in range(len(skel.iBody[fCount])):
                fBody = skel.iBody[fCount][i][0]
                # print('fCount: ', fCount)
                for j in range(len(fBody.joints)):
                    # draw joints
                    cx0 = int(fBody.joints[j].colorX+0.5)
                    cy0 = int(fBody.joints[j].colorY+0.5)
                    cv2.circle(frame, (cx0, cy0), 4, (0, 255, 0), -1)

                    # draw lines
                    p = connecting_joint[j] - 1
                    cx1 = int(fBody.joints[p].colorX+0.5)
                    cy1 = int(fBody.joints[p].colorY+0.5)
                    cv2.line(frame, (cx0, cy0), (cx1, cy1), (0, 0, 255), 2)
                    # print('cj: ', connecting_joint[j]-1)
        except IndexError:
            exception_avi_list.append(video_file_list[index])
            exception_skel_list.append(skeleton_file_list[index])
            print('Marked exception file...')

        # vertical flip
        frame = cv2.flip(frame, 1)
        cv2.imshow('frame', frame)

        key = cv2.waitKey(period)
        if key == ord('q'):     # backward
            if index > 0: index -= 1
            backward = True
            break
        elif key == ord('e'):   # forward
            break
        elif key == ord('x'):   # mark the video clip name to exclude
            exception_avi_list.append(video_file_list[index])
            exception_skel_list.append(skeleton_file_list[index])
            print('Marked exception file...')
        elif key == ord('z'):
            if show_mode == 2:  # remove the marked file name from the exception list
                del exception_avi_list[index]
                del exception_skel_list[index]
                print('Remove the marked file from the exception list')
        elif key == 27:         # ESC
            stop = True
            break


        fCount += 1
        # phase = fCount * 1.0 / len(skel.iBody)
        # print('frame phase: ', phase, ' fc: ', len(skel.iBody))
        if fCount >= len(skel.iBody):
            break

    file.close()
    cap.release()
    if stop == True: break

    if backward == True:
        backward = False
    else:
        index += 1

cv2.destroyAllWindows()

# Deduplication
exception_avi_list = sorted(list(set(exception_avi_list)))
exception_skel_list = sorted(list(set(exception_skel_list)))


print('---------------------------------------------------------')
print('------------Exception file list information--------------')
print('---------------------------------------------------------')
print('Number of files[avi]: ', len(exception_avi_list))

print('File name of the avi list')
for i in range(len(exception_avi_list)):
    print(exception_avi_list[i])
print('\n')

print('Number of files[avi]: ', len(exception_skel_list))
print('File name of the skeleton list')
for i in range(len(exception_skel_list)):
    print(exception_skel_list[i])

# ----------------------------------------
# ----- [ Exception file list save ] -----
# ----------------------------------------
if save_exception_list:
    print('save exception list!')
    # exception list will be merged in mode 0 or 1
    if show_mode <= 1 \
        and os.path.isfile(A+'_exeception_avi_list.txt')\
        and os.path.isfile(A+'_exeception_skeleton_list.txt'):  # file existence check

        # Load the exception file list and append current list
        with open(A+'_exeception_avi_list.txt', 'r') as f_avi:
            load_exception_avi_list = f_avi.read().splitlines()
        with open(A+'_exeception_skeleton_list.txt', 'r') as f_skel:
            load_exception_skel_list = f_skel.read().splitlines()

        # list concat and deduplication
        exception_avi_list = sorted(set(load_exception_avi_list + exception_avi_list))
        exception_skel_list = sorted(set(load_exception_skel_list + exception_skel_list))

    # Save the exception file list
    with open(A+'_exeception_avi_list.txt', 'w') as f:
        for i in range(len(exception_avi_list)):
            f.write(exception_avi_list[i]+'\n')

    with open(A+'_exeception_skeleton_list.txt', 'w') as f:
        for i in range(len(exception_skel_list)):
            f.write(exception_skel_list[i]+'\n')
