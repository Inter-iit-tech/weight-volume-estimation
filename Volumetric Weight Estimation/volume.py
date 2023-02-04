from flask import Flask, request, jsonify
import cv2
import math
import numpy as np

# Tunable Parameters:
WHITE_EXTRACTION_THRESHOLD = 180
WHITE_EXTRACTION_PERCENT = 0.4
MIN_LENGTH_THRESHOLD = 3                                                 # In cm
MAX_LENGTH_THRESHOLD = 40                                                # In cm
LENGTH_RATIO = 14
MIN_AREA_THRESHOLD = MIN_LENGTH_THRESHOLD*MIN_LENGTH_THRESHOLD           # In cm2
MAX_AREA_THRESHOLD = MAX_LENGTH_THRESHOLD*MAX_LENGTH_THRESHOLD           # In cm2
AREA_RATIO = LENGTH_RATIO*LENGTH_RATIO

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)

def detectAndExtractWhiteBoundaries(image):
    lr = 0
    hr = image.shape[0] - 1
    lc = 0
    hc = image.shape[1] - 1

    percent = 0
    while(lr < hr and percent < WHITE_EXTRACTION_PERCENT):
        white = 0
        total = hc+1
        for i in range(hc+1):
            if(image[lr][i] >= WHITE_EXTRACTION_THRESHOLD):
                white += 1
        percent = white / total
        lr += 1
    
    percent = 0
    while(hr > lr and percent < WHITE_EXTRACTION_PERCENT):
        white = 0
        total = hc+1
        for i in range(hc+1):
            if(image[hr][i] >= WHITE_EXTRACTION_THRESHOLD):
                white += 1
        percent = white / total
        hr -= 1

    percent = 0
    while(lc < hc and percent < WHITE_EXTRACTION_PERCENT):
        white = 0
        total = hr+1
        for i in range(hr+1):
            if(image[i][lc] >= WHITE_EXTRACTION_THRESHOLD):
                white += 1
        percent = white / total
        lc += 1

    percent = 0
    while(hc > lc and percent < WHITE_EXTRACTION_PERCENT):
        white = 0
        total = hr+1
        for i in range(hr+1):
            if(image[i][hc] >= WHITE_EXTRACTION_THRESHOLD):
                white += 1
        percent = white / total
        hc -= 1

    if(lr==hr or lc==hc):
        return np.array([])
    
    return image[lr:hr+1, lc:hc+1]

def getVolumeAndOtherDetails(img):
    file_bytes = np.frombuffer(img.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = detectAndExtractWhiteBoundaries(gray)

    if gray.ndim == 1:
        resp = jsonify({
            'message': 'Poor Lightning Conditions, Fix and Try Again'
        })
        print("Poor Lightning Conditions, Fix and Try Again")
        resp.status_code = 406
        return resp

    # Canny Filter Parameter:
    t_lower = 30  # Lower Threshold
    t_upper = 200  # Upper threshold
    
    # Applying the Canny Edge filter
    edge = cv2.Canny(gray, t_lower, t_upper)

    # detect the contours on the binary image using cv2.CHAIN_APPROX_NONE
    contours, _ = cv2.findContours(image=edge, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)

    expectedArea = MIN_AREA_THRESHOLD
    expectedLength = MIN_LENGTH_THRESHOLD
    expectedBreadth = MIN_LENGTH_THRESHOLD

    for contour in contours:
        rect = cv2.minAreaRect(contour)
        (_, _), (width, height), _ = rect
        width, height = width/LENGTH_RATIO, height/LENGTH_RATIO
        area = cv2.contourArea(cv2.convexHull(contour)) / AREA_RATIO
        if(width >= MIN_LENGTH_THRESHOLD and height >=MIN_LENGTH_THRESHOLD and area >= MIN_AREA_THRESHOLD and area <= MAX_AREA_THRESHOLD):
            if(expectedArea < area):
                expectedArea = area
                expectedLength = width
                expectedBreadth = height

    if(expectedLength < expectedBreadth):
        expectedLength, expectedBreadth = expectedBreadth, expectedLength

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