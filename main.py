import cv2
import numpy as np
import mediapipe as mp
import serial
import time 
import pygame
from threading import Thread
mphands = mp.solutions.hands
hands = mphands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

keys = [f'{j}{i}' for i in [*'2345'] for j in [*'CDEFGAB']]
offsets = {'red': 48, 'guitar': 48, 'yellow': 0, 'piano':0}
activation = None
pygame.mixer.init()

noteaudios = [pygame.mixer.Sound(str(fileno)+'piano.wav') for fileno in range(48)] + [pygame.mixer.Sound(str(fileno)+'guitar.wav') for fileno in range(48)] #0guitar to 3guitar are empty wav files (classical guitar cannot play C2 to D#2)


def playnote(fileno): 
    global noteaudios
    noteaudios[fileno].play()


def stopnote(fileno):
    global noteaudios
    try:
        noteaudios[fileno].stop()
    except Exception: #if note is not playing, don't halt.
        pass

def avgColor(region):
    rowwise = np.mean(region, axis=0)
    total = np.mean(rowwise, axis=0)
    return total

def closestColor(avgcolor, colors):
    mindist = float('inf')
    closest = None

    for color, colorval in colors.items():
        distance = np.linalg.norm(avgcolor - np.array(colorval))
        if distance < mindist:
            mindist = distance
            closest = color

    return closest, mindist

def main():
    global activation, offsets
    colors = {
        'red': (230, 170, 230),
        'yellow': (50, 230, 230),
        'blue': (255, 100, 100)
    }

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera Unavailable")
        return
    
    playing = set()

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Cannot Capture Frame")
            break

        rgbframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgbframe)

        hands = {}
        if result.multi_hand_landmarks:
            for i, landmarks in enumerate(result.multi_hand_landmarks):
                mp_drawing.draw_landmarks(frame, landmarks, mphands.HAND_CONNECTIONS)

                height, width, _ = frame.shape
                x_min = width
                y_min = height
                x_max = 0
                y_max = 0

                for landmark in landmarks.landmark:
                    x = int(landmark.x * width)
                    y = int(landmark.y * height)
                    x_min = min(x, x_min)
                    y_min = min(y, y_min)
                    x_max = max(x, x_max)
                    y_max = max(y, y_max)

                xis = (x_min+x_max)//2
                yis = (y_min+y_max)//2

                if x_min < x_max and y_min < y_max:
                    handarea = frame[y_min:y_max, x_min:x_max]
                    avgcolor = avgColor(handarea)
                    color, distance = closestColor(avgcolor, colors)

                    if color:
                        print(f"Hand {i + 1}: Closest color: {color} (Distance: {distance:.2f})")
                        hands[i+1] = {'pos': xis/int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), 'color': color}
                        cv2.circle(frame, (xis, yis), radius=10, color=(0, 255, 0), thickness=2)
                        cv2.putText(frame, f"Hand {i + 1}: {color}", (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow('Hand Detection', frame)

        a2 = set(activation)

        topause = playing - a2
        tostart = a2 - playing

        for i in topause: 
            stopnote(i)
            stopnote(i+48)
        for i in tostart: 
            closesthandcolor = ''
            closesthanddist = 100000
            for hand in hands:
                if((m:= abs(hand['pos'] - i/48)) < closesthanddist):
                    closesthandcolor = hand['color']
                    closesthanddist = m

            Thread(target=playnote, args = (i + offsets[closesthandcolor],)).start()


        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()



def mainarduino():
    global activation
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)
    while (1):
        time.sleep(0.01)
        activation = {idx for idx, i in enumerate(ser.readline().decode('utf-8').strip()) if i=='1'} #activated




Thread(target=main).start()
Thread(target=mainarduino).start()
