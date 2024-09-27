from flask import Flask, render_template, Response, jsonify, request
import virtualMousePainting as virtualMouse

import numpy as np


canvas = np.zeros((480, 640, 3), np.uint8)

app = Flask(__name__)
COLAB_SERVER_URL = 'http://<ngrok-url>/process_image'

# welcome page
@app.route('/')
def home():
    return render_template("home.html")

# 두번째꺼 -> 완성 / canvas, video 분리 o
@app.route('/canvas')
def canvas():
    return render_template('canvas.html')

# /canvas에서 webcam을 받아옴
@app.route('/webcam_feed')
def webcam_feed_route():
    return Response(virtualMouse.webcam_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

# /canvas에서 그림이 그려지는 canvas를 받아옴
@app.route('/canvas_feed')
def canvas_feed_route():
    return Response(virtualMouse.canvas_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 변환 후 결과 페이지
@app.route('/result', methods=['POST'])
def result_page():
    # POST 요청으로 받은 이미지 URL과 텍스트를 처리
    image_url = request.form.get('image_url')  # JavaScript에서 전송한 이미지 URL 받기
    user_text = request.form.get('text')  # 사용자가 입력한 텍스트 받기

    # 템플릿으로 이미지 URL과 텍스트 전달
    return render_template('result.html', image_url=image_url, text=user_text)

if __name__ == '__main__':
    app.run(debug=True)
