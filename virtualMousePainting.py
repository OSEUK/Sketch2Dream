import cv2
import mediapipe as mp
import time
import numpy as np

canvas = np.ones((480, 640, 3), np.uint8) * 255
col = [0, 0, 0]  # 기본 색상(검정색)
xp, yp = 0, 0
eraser_size = 20  # 지우개 크기 설정

def save_canvas():
    global canvas
    timestamp = int(time.time())
    filename = f'static/canvas_{timestamp}.png'
    cv2.imwrite(filename, canvas)
    return f"Canvas saved as {filename}"

# 손가락 위치를 저장할 전역 변수
finger_position = None  # 손가락 끝 위치를 저장할 전역 변수 (x, y 좌표)

def webcam_feed():
    global canvas, xp, yp, col, finger_position
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # 너비 설정
    cap.set(4, 480)  # 높이 설정
    cap.set(10, 150)  # 밝기 설정

    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpdraw = mp.solutions.drawing_utils

    frame_skip = 2  # 2 프레임 중 1프레임만 처리
    frame_count = 0

    while True:
        success, frame = cap.read()
        frame_count += 1

        # 일정 프레임만 처리 (프레임 스킵)
        if frame_count % frame_skip != 0:
            continue
        frame = cv2.flip(frame, 1)

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(img)
        lanmark = []

        if results.multi_hand_landmarks:
            for hn in results.multi_hand_landmarks:
                for id, lm in enumerate(hn.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lanmark.append([id, cx, cy])
                mpdraw.draw_landmarks(frame, hn, mpHands.HAND_CONNECTIONS)

        if len(lanmark) != 0:
            x1, y1 = lanmark[8][1], lanmark[8][2]  # 검지손가락 끝 좌표
            finger_position = (x1, y1)  # 손가락 끝 좌표를 전역 변수에 저장

            x2, y2 = lanmark[12][1], lanmark[12][2]  # 중지손가락 끝 좌표

            # 손을 펼치면 캔버스를 초기화
            if is_canvas_erase_mode(lanmark):
                canvas = np.ones((480, 640, 3), np.uint8) * 255
                xp, yp = 0, 0
                continue

            # 부분 지우기 모드
            elif is_erase_mode(lanmark):
                cv2.circle(frame, (x1, y1), eraser_size, (255, 255, 255), cv2.FILLED)
                cv2.circle(canvas, (x1, y1), eraser_size, (255, 255, 255), cv2.FILLED)
                xp, yp = 0, 0  # 지우기 모드에서는 선을 그리지 않기 위해 초기화

            # 그리기 모드
            elif is_draw_mode(lanmark):
                if xp == 0 and yp == 0:
                    xp, yp = x1, y1

                cv2.line(frame, (xp, yp), (x1, y1), col, 5, cv2.FILLED)
                cv2.line(canvas, (xp, yp), (x1, y1), col, 5, cv2.FILLED)
                xp, yp = x1, y1
            else:
                # 그리기 모드가 아닌 경우, xp, yp 초기화
                xp, yp = 0, 0

        # 프레임 인코딩
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def canvas_feed():
    global canvas, finger_position
    while True:
        canvas_copy = canvas.copy()  # 원본 canvas를 수정하지 않기 위해 복사본 사용

        # 손가락 위치가 있을 경우, 해당 위치에 원을 표시
        if finger_position is not None:
            x1, y1 = finger_position
            cv2.circle(canvas_copy, (x1, y1), 5, (0, 255, 0), cv2.FILLED)  # 손가락 위치에 초록색 원 표시

        # 캔버스 출력
        ret, buffer = cv2.imencode('.jpg', canvas_copy)
        canvas_frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + canvas_frame + b'\r\n')

def is_canvas_erase_mode(lanmark):
    # 모든 손가락을 펼쳤을 때 캔버스 지우기 모드
    if (lanmark[8][2] < lanmark[6][2] and
        lanmark[12][2] < lanmark[10][2] and
        lanmark[16][2] < lanmark[14][2] and
        lanmark[20][2] < lanmark[18][2]):
        return True
    return False

def is_draw_mode(lanmark):
    # 검지 손가락만 펼쳐졌는지 확인
    # 검지(8)의 끝이 관절(6)보다 위에 있고, 다른 손가락은 굽혀져 있는지 확인
    if (lanmark[8][2] < lanmark[6][2] and  # 검지 손가락은 펼쳐짐
        lanmark[12][2] > lanmark[10][2] and  # 중지 손가락은 굽혀짐
        lanmark[16][2] > lanmark[14][2] and  # 약지 손가락은 굽혀짐
        lanmark[20][2] > lanmark[18][2]):  # 소지 손가락은 굽혀짐
        return True
    return False

def is_erase_mode(lanmark):
    # 세 손가락을 펴고 나머지 손가락은 굽혀진 상태인 경우
    if (lanmark[8][2] < lanmark[6][2] and  # 검지 손가락은 펼쳐짐
        lanmark[12][2] < lanmark[10][2] and  # 중지 손가락은 펼쳐짐
        lanmark[16][2] < lanmark[14][2] and  # 약지 손가락은 펼쳐짐
        lanmark[20][2] > lanmark[18][2]):  # 소지 손가락은 굽혀짐
        return True
    return False
