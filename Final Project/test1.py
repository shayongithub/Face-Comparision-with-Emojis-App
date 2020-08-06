from scipy.spatial import distance as dist
from imutils.video import VideoStream
import time
from imutils import face_utils
import cv2
import numpy as np
import dlib
import os
import random

def eye_aspect_ratio(eye):
	# compute the euclidean distances between the two sets of
	# vertical eye landmarks (x, y)-coordinates
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])

	# compute the euclidean distance between the horizontal
	# eye landmark (x, y)-coordinates
	C = dist.euclidean(eye[0], eye[3])

	# compute the eye aspect ratio
	ear = (A + B) / (2.0 * C)

	# return the eye aspect ratio
	return ear
def mouth_aspect_ratio(mouth):
    A = dist.euclidean(mouth[1], mouth[7])
    B = dist.euclidean(mouth[2], mouth[6])
    C = dist.euclidean(mouth[3], mouth[5])

    D = dist.euclidean(mouth[0], mouth[4])

    mar = (A + B + C) / (3.0 * D)

    return mar
def play_video(folder):
    # load video capture from file
    video = cv2.VideoCapture(os.path.join(folder, "video.avi"))
    # window name and size
    cv2.namedWindow("video", cv2.WINDOW_AUTOSIZE)
    while video.isOpened():
        # Read video capture
        ret, frame = video.read()

        #when video finishes, break
        if ret != True:
            break
        # Display each frame
        cv2.imshow("video", frame)
        # show one frame at a time
        #cv2.waitKey(00) == ord('k')
        # Quit when 'q' is pressed

        if cv2.waitKey(100) == 27:
            break
    # Release capture object
    video.release()
    # Exit and distroy all windows
    cv2.destroyAllWindows()
def random_emoji():

    return emoji

#Record Video

filename = 'video.avi'
frames_per_second = 24.0
res = '720p'

def change_res(cap, width, height):
    cap.set(3, width)
    cap.set(4, height)

# Standard Video Dimensions Sizes
STD_DIMENSIONS =  {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}

# grab resolution dimensions and set video capture to it.
def get_dims(cap, res='1080p'):
    width, height = STD_DIMENSIONS["480p"]
    if res in STD_DIMENSIONS:
        width,height = STD_DIMENSIONS[res]
    ## change the current caputre device
    ## to the resulting resolution
    change_res(cap, width, height)
    return width, height

VIDEO_TYPE = {
    'avi': cv2.VideoWriter_fourcc(*'XVID'),
    #'mp4': cv2.VideoWriter_fourcc(*'H264'),
    'mp4': cv2.VideoWriter_fourcc(*'XVID'),
}

def get_video_type(filename):
    filename, ext = os.path.splitext(filename)
    if ext in VIDEO_TYPE:
      return VIDEO_TYPE[ext]
    return VIDEO_TYPE['avi']

#Smile cascade

smile_cascade= cv2.CascadeClassifier("Resources/haarcascade_smile.xml")

#EMOJI DETECTOR
EYE_AR_THRESH = 0.20
EYE_AR_THRESH_RIGHT = 0.19
EYE_NORMAL_AR_THRESH_LOW = 0.22
EYE_NORMAL_AR_THRESH_HIGH = 0.35

EYE_AR_CONSEC_FRAMES = 25
EYE_AR_CONSEC_FRAMES_RIGHT = 20

MOUTH_AR_THRESH = 0.6
MOUTH_AR_CONSEC_FRAMES = 20
MOUTH_SHUT_AR_THRESH = 0.1
MOUTH_SHUT_AR_CONSEC_FRAMES = 25

COUNTER = 0
COUNTER_RIGHT_EYE = 0
COUNTER_NEUTRAL = 0
COUNTER_MOUTH = 0
COUNTER_MOUTH_SHUT = 0

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mStart, mEnd) = (60,68)
(mOutStart, mOutEnd) = (48,60)

#TURN ON WEBCAM
print("[INFO] camera sensor warming up...")
cap = cv2.VideoCapture(0)
time.sleep(2.0)
#Resize the frame

cap.set(3, 640)
cap.set(4,480)

#Random emoji
emoji_list = ["smile.jpg", "blink.jpg", "neutral.jpg", "wow.jpg", "sad.jpg"]
emoji = random.choice(emoji_list)
emoji_list.remove(emoji)
image_emoji = cv2.imread(emoji)
image_emoji = cv2.resize(image_emoji, (200, 200))
alpha = 0.1

#Record the video
record = False

elapse = 0
#Start the game
print('The game is starting...')
ans = input('Do you want to record (Y/N): ')
if ans.lower() == 'y':
    out = cv2.VideoWriter(filename, get_video_type(filename), 25, get_dims(cap, res='720'))
    record = True
else:
    pass
start = time.time()
while True:

    verbose_smile = False

    _, frame = cap.read()
    frame = cv2.flip(frame,1)

    added_image = cv2.addWeighted(frame[0:200, 0:200, :], alpha, image_emoji[0:200, 0:200, :], 1 - alpha, 0)
    frame[0:200, 0:200] = added_image

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray, 0)

    for face in faces:
        shape = predictor(gray, face)
        shape = face_utils.shape_to_np(shape)

        # Eye detection
        # extract the left and right eye coordinates, then use the
        # coordinates to compute the eye aspect ratio for both eyes

        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)

        # average the eye aspect ratio together for both eyes
        ear = (leftEAR + rightEAR) / 2.0

        # compute the convex hull for the left and right eye, then
        # visualize each of the eyes
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        # Mouth-opened detection
        mouth_inside = shape[mStart:mEnd]
        mouth_outside = shape[mOutStart:mOutEnd]
        mouthMAR = mouth_aspect_ratio(mouth_inside)

        # draw contours around the mouth
        mouthHull = cv2.convexHull(mouth_outside)
        cv2.drawContours(frame, [mouthHull], -1, (0, 255, 255), 1)

        if emoji.split('.jpg')[0] == 'blink':
            for face in faces:

                # smile detection
                x1 = face.left()
                y1 = face.top()
                x2 = face.right()
                y2 = face.bottom()
                roi_gray = gray[y1:y2, x1:x2]

                smile = smile_cascade.detectMultiScale(roi_gray, 1.6, 22)

                for (sx, sy, sw, sh) in smile:
                    verbose_smile = True

                if rightEAR < EYE_AR_THRESH_RIGHT:
                    COUNTER_RIGHT_EYE += 1
                    if COUNTER_RIGHT_EYE >= EYE_AR_CONSEC_FRAMES_RIGHT and verbose_smile:
                        # draw an alarm on the frame
                        cv2.putText(frame, "BLINK RIGHT", (220, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

                        # otherwise, the eye aspect ratio is not below the blink
                        # threshold, so reset the counter and alarm

                else:
                    COUNTER_RIGHT_EYE = 0
        elif emoji.split('.jpg')[0] == 'smile':
            for face in faces:
                # smile detection
                x1 = face.left()
                y1 = face.top()
                x2 = face.right()
                y2 = face.bottom()
                roi_gray = gray[y1:y2, x1:x2]

                smile = smile_cascade.detectMultiScale(roi_gray, 1.6, 22)

                for (sx, sy, sw, sh) in smile:
                    cv2.putText(frame, "SMILE RIGHT", (220, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 255), 3)
        elif emoji.split('.jpg')[0] == 'neutral':
            # detect neutral face
            if mouthMAR < MOUTH_SHUT_AR_THRESH\
                    and EYE_NORMAL_AR_THRESH_LOW < ear < EYE_NORMAL_AR_THRESH_HIGH:

                COUNTER_MOUTH_SHUT += 1
                COUNTER_NEUTRAL += 1

                if COUNTER_MOUTH_SHUT >= MOUTH_SHUT_AR_CONSEC_FRAMES \
                        and COUNTER_NEUTRAL >= EYE_AR_CONSEC_FRAMES:
                    # draw an alarm on the frame
                    cv2.putText(frame, "NEUTRAL RIGHT", (220, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                    verbose_mouth = True
            else:
                COUNTER_MOUTH_SHUT = 0
                COUNTER_NEUTRAL = 0
        elif emoji.split('.jpg')[0] == 'wow':
            # detect mouth open
            if mouthMAR > MOUTH_AR_THRESH:
                COUNTER_MOUTH += 1
                if COUNTER_MOUTH >= MOUTH_AR_CONSEC_FRAMES:
                    # draw an alarm on the frame
                    cv2.putText(frame, "WOW RIGHT !!!", (220, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

            else:
                COUNTER_MOUTH = 0
        elif emoji.split('.jpg')[0] == 'sad':
            if ear < EYE_AR_THRESH and mouthMAR < MOUTH_SHUT_AR_THRESH:
                COUNTER += 1
                COUNTER_MOUTH_SHUT += 1
                if COUNTER >= EYE_AR_CONSEC_FRAMES \
                        and COUNTER_MOUTH_SHUT >= MOUTH_SHUT_AR_CONSEC_FRAMES:
                    # draw an alarm on the frame
                    cv2.putText(frame, "SAD RIGHT", (220, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            else:
                COUNTER = 0
                COUNTER_MOUTH_SHUT = 0

        #PUT EAR AND MAR
        cv2.putText(frame, "EAR: {:.2f}".format(ear), (450, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "MAR: {:.2f}".format(mouthMAR), (450, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


    # record the video
    if record:
        out.write(frame)

    # show the webcam
    cv2.imshow("Frame", frame)

    elapse = time.time() - start
    #print(elapse)

    # if elapse > 10 and len(emoji_list) != 0:
    #     emoji = random.choice(emoji_list)
    #     emoji_list.remove(emoji)
    #     image_emoji = cv2.imread(emoji)
    #     image_emoji = cv2.resize(image_emoji, (200, 200))
    #     start = time.time()
    # if elapse > 15:
    #     break

    k = cv2.waitKey(1)
    if k == 27:
        break
    if k == ord('d'):
        emoji = random.choice(emoji_list)
        emoji_list.remove(emoji)
        image_emoji = cv2.imread(emoji)
        image_emoji = cv2.resize(image_emoji, (200, 200))
cap.release()
out.release()
cv2.destroyAllWindows()

ans = input('Do you wanna show your video: ')
if ans.lower() == 'yes':
    play_video("E:\\Python\\project")
else:
    print('Thanks for playing')
    print('Game is closing...')
# while True:
#     _, frame = cap.read()
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#
#     faces = detector(gray, 0)
#
#     for face in faces:
#
#         #smile detection
#         x1 = face.left()
#         y1 = face.top()
#         x2 = face.right()
#         y2 = face.bottom()
#         roi_gray = gray[y1:y2, x1:x2]
#
#         smile = smile_cascade.detectMultiScale(roi_gray, 1.6, 22)
#
#         for (sx,sy,sw,sh) in smile:
#             cv2.putText(frame, "SMILE!", (400, 300),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
#
#
#
#         # determine the facial landmarks for the face region, then
#         # convert the facial landmark (x, y)-coordinates to a NumPy
#         # array
#         shape = predictor(gray, face)
#         shape = face_utils.shape_to_np(shape)
#
#
#         #Eye detection
#         # extract the left and right eye coordinates, then use the
#         # coordinates to compute the eye aspect ratio for both eyes
#
#         leftEye = shape[lStart:lEnd]
#         rightEye = shape[rStart:rEnd]
#         leftEAR = eye_aspect_ratio(leftEye)
#         rightEAR = eye_aspect_ratio(rightEye)
#
#         # average the eye aspect ratio together for both eyes
#         ear = (leftEAR + rightEAR) / 2.0
#
#         # compute the convex hull for the left and right eye, then
#         # visualize each of the eyes
#         leftEyeHull = cv2.convexHull(leftEye)
#         rightEyeHull = cv2.convexHull(rightEye)
#         cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
#         cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
#
#         #Mouth-opened detection
#         mouth_inside = shape[mStart:mEnd]
#         mouth_outside = shape[mOutStart:mOutEnd]
#         mouthMAR = mouth_aspect_ratio(mouth_inside)
#
#         #draw contours around the mouth
#         mouthHull = cv2.convexHull(mouth_outside)
#         cv2.drawContours(frame, [mouthHull], -1, (0, 255, 255), 1)
#
#         # check to see if the eye aspect ratio is below the blink
#         # threshold, and if so, increment the blink frame counter
#         if ear < EYE_AR_THRESH:
#             COUNTER += 1
#             if COUNTER >= EYE_AR_CONSEC_FRAMES:
#                 # draw an alarm on the frame
#                 cv2.putText(frame, "EYE CLOSED", (400, 60),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
#                 verbose_eye_closed = True
#                 # otherwise, the eye aspect ratio is not below the blink
#                 # threshold, so reset the counter and alarm
#
#         else:
#             COUNTER = 0
#
#         #detect right eye closed
#         if rightEAR < EYE_AR_THRESH_RIGHT:
#             COUNTER_RIGHT_EYE += 1
#             if COUNTER_RIGHT_EYE >= EYE_AR_CONSEC_FRAMES_RIGHT:
#                 # draw an alarm on the frame
#                 cv2.putText(frame, "EYE Right CLOSED", (400, 150),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
#
#                 # otherwise, the eye aspect ratio is not below the blink
#                 # threshold, so reset the counter and alarm
#
#         else:
#             COUNTER_RIGHT_EYE = 0
#         #detect mouth open
#         if mouthMAR > MOUTH_AR_THRESH:
#             COUNTER_MOUTH += 1
#             if COUNTER_MOUTH >= MOUTH_AR_CONSEC_FRAMES:
#                 # draw an alarm on the frame
#                 cv2.putText(frame, "MOUTH OPEN", (50, 60),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
#                 verbose_mouth = True
#         else:
#             COUNTER_MOUTH = 0
#
#         #put the aspect ratio of eyes and mouth on the frame
#         cv2.putText(frame, "EAR: {:.2f}".format(ear), (400, 30),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
#         cv2.putText(frame, "MAR: {:.2f}".format(mouthMAR), (50, 30),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
#
#     #record the video
#     out.write(frame)
#     #show the webcam
#     cv2.imshow("Frame", frame)
#
#     if cv2.waitKey(1) & 0xFF == 13:
#         break
#
#
# cap.release()
# out.release()

