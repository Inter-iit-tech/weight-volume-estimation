from flask import Flask, request, jsonify
import cv2
import math
import numpy

# Tunable Parameters:
MIN_AREA = 10
MAX_AREA = 1000
AREA_RATIO = 228.565
LENGTH_RATIO = 50

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)

def getVolumeAndOtherDetails(img):
    file_bytes = numpy.frombuffer(img.read(), numpy.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Canny Filter Parameter:
    t_lower = 0  # Lower Threshold
    t_upper = 200  # Upper threshold
    
    # Applying the Canny Edge filter
    edge = cv2.Canny(gray, t_lower, t_upper)

    # detect the contours on the binary image using cv2.CHAIN_APPROX_NONE
    contours, hierarchy = cv2.findContours(image=edge, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)

    expectedArea = MIN_AREA
    expectedLength = math.sqrt(MIN_AREA)
    expectedBreadth = math.sqrt(MIN_AREA)

    for contour in contours:
        area = cv2.moments(contour)['m00']
        area = area / AREA_RATIO
        if(area >= MIN_AREA and area <= MAX_AREA):
            if(expectedArea < area):
                expectedArea = area
                x,y,w,h = cv2.boundingRect(contour)
                expectedLength = w / LENGTH_RATIO
                expectedBreadth = h / LENGTH_RATIO

    print("File: ", img.filename)
    print("Area: ", expectedArea)
    print("Length: ", expectedLength)
    print("Breadth: ", expectedBreadth)

    resp = jsonify({
        'area': expectedArea,
        'length': expectedLength,
        'breadth': expectedBreadth
    })
    resp.status_code = 201
    return resp

@app.route('/volume', methods=['POST'])
def upload_file():
	# check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message' : 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        return getVolumeAndOtherDetails(file)
    else:
        resp = jsonify({'message' : 'Allowed file types are png, jpg, jpeg'})
        resp.status_code = 400
        return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)