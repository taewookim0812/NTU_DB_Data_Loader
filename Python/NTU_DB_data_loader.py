# -*- coding: utf-8 -*-
"""
NTU_DB Data Loader

@author: Tae-woo Kim
e-mail: twkim0812@gmail.com
"""

class joint_struct:
    def __init__(self, joint_vec):
        if len(joint_vec) is not 12:
            raise ValueError('joint vector length is not valid..')

        # 3D location of the joint j
        self.x = joint_vec[0]
        self.y = joint_vec[1]
        self.z = joint_vec[2]

        # 2D location of the joint in corresponding depth/IR frame
        self.depthX = joint_vec[3]
        self.depthY = joint_vec[4]

        # 2D location of the joint in corresponding RGB frame
        self.colorX = joint_vec[5]
        self.colorY = joint_vec[6]

        # The orientation of the joint j
        self.orientationW = joint_vec[7]
        self.orientationX = joint_vec[8]
        self.orientationY = joint_vec[9]
        self.orientationZ = joint_vec[10]

        # The tracking state of the joint j
        self.trackingState = joint_vec[11]

    def display_joint_info(self):
        pass

class body_struct:
    def __init__(self):
        self.bodyID = None
        self.clippedEdges = None
        self.handLeftConfidence = None
        self.handLeftState = None
        self.handRightConfidence = None
        self.handRightState = None
        self.isRestricted = None
        self.leanX = None
        self.leanY = None
        self.trackingState = None
        self.jointCount = None

        self.joints = []

    def set_body_info(self, info_vec, jointCount):
        if len(info_vec) is not 10:
            raise ValueError('body infomation vector length is not valid..')

        self.bodyID = info_vec[0]
        self.clippedEdges = int(info_vec[1])
        self.handLeftConfidence = int(info_vec[2])
        self.handLeftState = int(info_vec[3])
        self.handRightConfidence = int(info_vec[4])
        self.handRightState = int(info_vec[5])
        self.isRestricted = int(info_vec[6])
        self.leanX = info_vec[7]
        self.leanY = info_vec[8]
        self.trackingState = int(info_vec[9])

        self.jointCount = jointCount


    def display_body_info(self):
        print('---------- Body information ------------')
        print('body ID: ', self.bodyID)
        print('clipped edges: ', self.clippedEdges)
        print('hand left confidence: ', self.handLeftConfidence)
        print('hand left state: ', self.handLeftState)
        print('hand right confidence: ', self.handRightConfidence)
        print('hand right state: ', self.handRightState)
        print('isRestricted: ', self.isRestricted)
        print('lean X: ', self.leanX)
        print('lean Y: ', self.leanY)
        print('tracking state: ', self.trackingState)
        print('joint count: ', self.jointCount)


class skeleton_struct:
    def __init__(self):
        self.iBody = []
        self.frameIdx = 0

    def append_body(self, fIdx, bIdx, body):
        if isinstance(body, body_struct)==False:
            raise ValueError('instance type error')

        if len(self.iBody) <= fIdx:
            self.iBody.append([])

        if len(self.iBody[fIdx]) <= bIdx:
            self.iBody[fIdx].append([])

        self.iBody[fIdx][bIdx].append(body)

    def get_body(self, fIdx, bIdx):
        return self.iBody[fIdx][bIdx]

    def print_skeleton_info(self):
        print('-------- Skeleton information ----------')
        for f in range(len(self.iBody)):
            print('Frame Index', f, ' nBody: ', len(self.iBody[f]))
            for b in range(len(self.iBody[f])):
                self.iBody[f][b][0].display_body_info()

        print('\n')
        print('---------- Joint information ------------')
        print('')


class Category:
    def __init__(self):
        self.daily_action = 'Daily_Actions'
        self.medical_conditions = 'Medical_Conditions'
        self.mutual_conditions = 'Mutual_Conditions'

# ------------------------------------------------------------------------------------
# ----------------------------------- Main Code --------------------------------------
# ------------------------------------------------------------------------------------

"""
***Notice
Before you use this code, Your NTU database files should be ordered as following.
Example)
/*your own path */NTU_DB/Daily_Actions/A022
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
import os, glob
print('OpenCV version: ', cv2.__version__)

# NTU DB were captured by Kinect-v2 with 30Hz
# What classes we hold
# [A022: cheer up, A023: hand waving, A031: pointing to something with finger]
# [A034: rub two hands together, A035: nod head/bow, A036: shake head, A038: salute]

S = 'S' + '{0:03}'.format(1)  # Setup Number
C = 'C' + '{0:03}'.format(1)  # Camera ID
P = 'P' + '{0:03}'.format(1)  # Performer ID
R = 'R' + '{0:03}'.format(1)  # Replication Number

# set file path
A = 'A' + '{0:03}'.format(50)  # Action class label
my_path = '/dd/'                                # TODO, change the '/dd/' to your own path
category = Category()
file_path = os.path.join(my_path, 'NTU_DB', category.mutual_conditions, A)

video_file_list = sorted(glob.glob(file_path + "/*.avi"))
skeleton_file_list = sorted(glob.glob(file_path + "/*.skeleton"))
print('video: ', video_file_list)
print('skeleton: ', skeleton_file_list)


# MATLAB based index, thus, -1 should be added in python-like index.
connecting_joint = [2, 1, 21, 3, 21, 5, 6, 7, 21, 9, 10, 11, 1, 13, 14, 15, 1, 17, 18, 19, 2, 8, 8, 12, 12]

index = 0
backward = False
stop = False
frame_rate = 30     # Hz
period = int((1.0/frame_rate) * 1000)
exception_avi_list = []
exception_skel_list = []
while index < len(video_file_list):
    # -----[ Data Load ]-----
    print('list number: ', index)
    print('video: ', video_file_list[index])
    print('skeleton: ', skeleton_file_list[index])

    cap = cv2.VideoCapture(video_file_list[index])
    file = open(skeleton_file_list[index])

    frameCount = np.fromstring(file.readline(), sep=' ', dtype='int32')[0]
    skel = skeleton_struct()
    for f in range(frameCount):  # frameCount
        bodyCount = np.fromstring(file.readline(), sep=' ', dtype='int32')[0]

        for b in range(bodyCount):
            body = body_struct()
            bodyInfo = np.fromstring(file.readline(), sep=' ', dtype='float64')
            jointCount = np.fromstring(file.readline(), sep=' ', dtype='int32')[0]
            body.set_body_info(bodyInfo, jointCount)

            for j in range(jointCount):
                jointInfo = np.fromstring(file.readline(), sep=' ', dtype='float64')
                joint = joint_struct(jointInfo)
                body.joints.append(joint)
            skel.append_body(f, b, body)
    file.close()
    # print(skel.print_skeleton_info())

    # -----[ Display Image and Skeleton ]-----
    fCount = 0
    while(cap.isOpened()):
        ret, frame = cap.read()

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
                cy1 = int(fBody.joints[p].colorY + 0.5)
                cv2.line(frame, (cx0, cy0), (cx1, cy1), (0, 0, 255), 2)
                # print('cj: ', connecting_joint[j]-1)

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
        elif key == 27:         # ESC
            stop = True
            break

        fCount += 1
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

# Display the result
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

# # Save the exception file list
# with open(A+'_exeception_avi_list.txt', 'w') as f:
#     for i in range(len(exception_avi_list)):
#         f.write(exception_avi_list[i]+'\n')
#
# with open(A+'_exeception_skeleton_list.txt', 'w') as f:
#     for i in range(len(exception_skel_list)):
#         f.write(exception_skel_list[i]+'\n')
