#!/Library/Frameworks/Python.framework/Versions/3.12/bin/python3
import cv2
import time
from cvzone.HandTrackingModule import HandDetector
import keyboard

def calculate_distance(pt1, pt2):
    return ((pt1[0] - pt2[0])*2 + (pt1[1] - pt2[1])*2)*0.5

movement_threshold = 0
stability_count = 0
stable_frames_required = 0
last_position = None
pinch_threshold = 40
double_click_timeout = 0.4
hold_timeout = 0.4
last_pinch_time = 0
pinch_count = 0
pinch_released = True
is_holding = False
single_click_pending = False
single_click_time = 0

keyboard.add_abbreviation('f', 'f')
keyboard.add_abbreviation('@@n@@', 'shift+n')

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(maxHands=1, detectionCon=0.8)

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)

    current_time = time.time()
    if hands:
        hand = hands[0]
        lmList = hand['lmList']
        wrist_point = lmList[0]
        hand_type = hand['type']

        if last_position:
            movement = calculate_distance(wrist_point, last_position)
            if movement < movement_threshold:
                stability_count += 1
            else:
                stability_count = 0
        last_position = wrist_point

        thumb_tip = lmList[4]
        index_tip = lmList[8]
        distance = calculate_distance(thumb_tip, index_tip)

        if distance < pinch_threshold and stability_count >= stable_frames_required:
            if pinch_released:
                if current_time - last_pinch_time < double_click_timeout:
                    if single_click_pending:
                        #double click right hand se
                        if hand_type == 'Right':
                            keyboard.press_and_release('a') 
                        else:
                        #double click left hand se
                            keyboard.press_and_release('b')
                        single_click_pending = False
                    pinch_count = 0
                else:
                    single_click_pending = True
                    single_click_time = current_time
                last_pinch_time = current_time
                pinch_released = False
            if current_time - last_pinch_time > hold_timeout and not is_holding:
                if hand_type == 'Right':
                    #right hold
                    keyboard.press_and_release('c')  
                else:
                    #left hold
                    keyboard.press_and_release('d') 
                is_holding = True
                single_click_pending = False  
        else:
            if not pinch_released:
                if is_holding:
                    if hand_type == 'Right':
                        print(f"{hand_type} hand is not pinching")
                    else:
                        print(f"{hand_type} hand is not pinching")
                    is_holding = False
                elif pinch_count == 1 and not is_holding:
                    if hand_type == 'Right':
                        #right single tap
                        keyboard.press_and_release('q')  
                    else:
                        #left single tap
                        keyboard.press_and_release('w') 
                    pinch_count = 0
                pinch_released = True
    else:
        last_position = None
        stability_count = 0

    if single_click_pending and current_time - single_click_time > double_click_timeout and not is_holding:
        if hand_type == 'Right':
            #right single tap
            keyboard.press_and_release('p') 
        else:
            #left single tap
            keyboard.press_and_release('r')  
        single_click_pending = False

    cv2.imshow("Image", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()