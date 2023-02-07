from flask import Flask, request, jsonify
import cv2
import math
import numpy as np
import base64
import io
import imageio.v2 as imageio

# Tunable Parameters:
WHITE_EXTRACTION_THRESHOLD = 150
WHITE_EXTRACTION_PERCENT = 0.4
MIN_LENGTH_THRESHOLD = 3                                                 # In cm
MAX_LENGTH_THRESHOLD = 40                                                # In cm
ARUCO_LENGTH =  3.8                                                      # In cm
MIN_AREA_THRESHOLD = MIN_LENGTH_THRESHOLD*MIN_LENGTH_THRESHOLD           # In cm2

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def isDimInRange(len):
    return len >= MIN_LENGTH_THRESHOLD and len <= MAX_LENGTH_THRESHOLD

def getDistance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))

def getAvgDist(corners):
    return (getDistance(corners[0], corners[1]) + getDistance(corners[1], corners[2]) + getDistance(corners[2], corners[3]) + getDistance(corners[3], corners[0]))/4

def getPixelWidthAruco(image):
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_250)
    parameters =  cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)
    markerCorners, _ , _ = detector.detectMarkers(image)
    if(len(markerCorners)==0):
        return -1
    return getAvgDist(markerCorners[0][0])

def detectAndExtractWhiteBoundaries(image):
    lr = 0
    hr = image.shape[0] - 1
    lc = 0
    hc = image.shape[1] - 1

    percent = 0
    while(lr < hr and percent < WHITE_EXTRACTION_PERCENT):
        white = 0
        total = hc+1
        white = np.count_nonzero(image[lr,:hc+1]>=WHITE_EXTRACTION_THRESHOLD)
        # for i in range(hc+1):
        #     if(image[lr][i] >= WHITE_EXTRACTION_THRESHOLD):
        #         white += 1
        percent = white / total
        lr += 1
    
    percent = 0
    while(hr > lr and percent < WHITE_EXTRACTION_PERCENT):
        white = 0
        total = hc+1
        white = np.count_nonzero(image[hr,:hc+1]>=WHITE_EXTRACTION_THRESHOLD)
        # for i in range(hc+1):
        #     if(image[hr][i] >= WHITE_EXTRACTION_THRESHOLD):
        #         white += 1
        percent = white / total
        hr -= 1

    percent = 0
    while(lc < hc and percent < WHITE_EXTRACTION_PERCENT):
        white = 0
        total = hr+1
        white = np.count_nonzero(image[:hr+1,lc]>=WHITE_EXTRACTION_THRESHOLD)
        # for i in range(hr+1):
        #     if(image[i][lc] >= WHITE_EXTRACTION_THRESHOLD):
        #         white += 1
        percent = white / total
        lc += 1

    percent = 0
    while(hc > lc and percent < WHITE_EXTRACTION_PERCENT):
        white = 0
        total = hr+1
        white = np.count_nonzero(image[:hr+1,hc]>=WHITE_EXTRACTION_THRESHOLD)
        # for i in range(hr+1):
        #     if(image[i][hc] >= WHITE_EXTRACTION_THRESHOLD):
        #         white += 1
        percent = white / total
        hc -= 1

    if(lr==hr or lc==hc):
        return np.array([])
    
    return image[lr:hr+1, lc:hc+1]

def getVolumeAndOtherDetails(img, format):
    image = None
    if format == 'buffer':
        file_bytes = np.frombuffer(img.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
    elif format == 'base64':
        decoded_img_data = base64.b64decode(img)
        image = imageio.imread(io.BytesIO(decoded_img_data))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = detectAndExtractWhiteBoundaries(gray)

    if gray.ndim == 1:
        resp = jsonify({
            'message': 'Poor Lightning Conditions, Fix and Try Again'
        })
        print("Poor Lightning Conditions, Fix and Try Again")
        resp.status_code = 400
        return resp
    

    _, edge = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    edge = cv2.bitwise_not(edge)


    # detect the contours on the binary image using cv2.CHAIN_APPROX_NONE
    contours, _ = cv2.findContours(image=edge, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)

    # draw contours on the original image
    arucoPixelWidth = getPixelWidthAruco(image)
    if(arucoPixelWidth==-1):
        resp = jsonify({
            'message': 'Could not detect aruco, Try Again'
        })
        print("Could not detect aruco, Try Again")
        resp.status_code = 400
        return resp

    LENGTH_RATIO = arucoPixelWidth/ARUCO_LENGTH
    AREA_RATIO = LENGTH_RATIO*LENGTH_RATIO

    expectedArea = MIN_AREA_THRESHOLD
    expectedLength = MIN_LENGTH_THRESHOLD
    expectedBreadth = MIN_LENGTH_THRESHOLD

    for contour in contours:
        rect = cv2.minAreaRect(contour)
        (_, _), (width, height), _ = rect
        width, height = width/LENGTH_RATIO, height/LENGTH_RATIO
        area = cv2.contourArea(cv2.convexHull(contour)) / AREA_RATIO
        if(expectedArea < area):
            expectedArea = area
            expectedLength = width
            expectedBreadth = height

    if(not isDimInRange(expectedLength) or not isDimInRange(expectedBreadth)):
        resp = jsonify({
            'message': 'Dimension not in threshold range, Try Again'
        })
        print("Dimensions are not in threshold range...")
        resp.status_code = 400
        return resp


    if(expectedLength < expectedBreadth):
        expectedLength, expectedBreadth = expectedBreadth, expectedLength

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

@app.route('/volume/fromFile', methods=['POST'])
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
        return getVolumeAndOtherDetails(file, 'buffer')
    else:
        resp = jsonify({'message' : 'Allowed file types are png, jpg, jpeg'})
        resp.status_code = 400
        return resp

@app.route('/volume/fromBase64', methods=['POST'])
def upload_data_string():
    if not request.is_json:
        resp = jsonify({'message' : "JSON payload not found"})
        resp.status_code = 400
        return resp
    else:
        reqBody = request.get_json();
        img = reqBody['file']
        return getVolumeAndOtherDetails(img, 'base64')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)