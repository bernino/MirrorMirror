""" Analyze photo and write description to its exif user-comment tag as json.

Usage:
    mirrormirror.py

    Change the "img" variable to a photo of your choice.
    This script will evolve into a "find similar faces" service.

Output:
    - A image.show() with rectangle around face and meta data.
    - Meta data in json on stdout.


TODO:
    - stdin folder argument, loop through all photos there
    - implement find similar faces
    - make it a web app
    - probably change to matplotlib for jpg output of show()
    - define all functionality as functions and call these
    - preserve all originial exif data and write to out.jpg

"""

import json
import requests
import pyexiv2
from PIL import Image, ImageDraw
# from io import BytesIO
# from matplotlib import patches
# import matplotlib.pyplot as plt
from PIL import ImageFont
# import http.client
import urllib.request
import urllib.parse
import urllib.error
# import base64

img = 'emotions.jpg'

# leaving url based img in for future web app
# img_url = 'https://pbs.twimg.com/profile_images/833617827999469569/ymGepKGv.jpg'
# img_data = open(img_url, 'rb')

# Convert width height to a point in a rectangle
def getRectangle(faceDictionary):
    rect = faceDictionary['faceRectangle']
    left = rect['left']
    top = rect['top']
    bottom = left + rect['height']
    right = top + rect['width']
    return ((left, top), (bottom, right))


face_api_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect'
face_headers = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': '420abad09f3e43ccbb9e6032055c557b'
}
face_params = urllib.parse.urlencode({
    # Request parameters
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'true',
    'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
    'recognitionModel': 'recognition_02',
    'returnRecognitionModel': 'false',
    'detectionModel': 'detection_01',
})

facelist_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/facelists/facelist/persistedFaces'
facelist_headers = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': '420abad09f3e43ccbb9e6032055c557b'
}
facelist_params = urllib.parse.urlencode({
    # Request parameters
    'detectionModel': 'detection_01',
})

vision_api_url = 'https://westcentralus.api.cognitive.microsoft.com/vision/v2.0/analyze'
vision_params = {'visualFeatures': 'Categories,Description,Color'}
vision_headers = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': '2ccbc989619642c893fcc7db3985a521'
}

with open(img, 'rb') as f:
    img_data = f.read()

# here we detect faces and get their meta data
face_request = requests.post(face_api_url, params=face_params, headers=face_headers, data=img_data)
faces = face_request.json()
print(json.dumps(faces, indent=4, sort_keys=True))

# here we get a meta description of the picture
vision_response = requests.post(vision_api_url, params=vision_params, headers=vision_headers, data=img_data)
vision = vision_response.json()
print(json.dumps(vision, indent=4, sort_keys=True))

# Download the image from the url
# response = requests.get(img_url)
# img = Image.open(BytesIO(response.content))
image = Image.open(img)

# For each face returned: count, use the face rectangle and draw a red box.
# Plus get to know the return data
draw = ImageDraw.Draw(image)
font = ImageFont.truetype("/Applications/Microsoft Excel.app/Contents/Resources/Fonts/arial.ttf", 8, encoding="unic")

face_count = 0

for face in faces:
    # add face to faceList
    # facelist_response = requests.post(facelist_url, params=facelist_params, headers=headers, data=img_data)
    # print(facelist_response.url)
    # facelist = facelist_response.json()
    # print(json.dumps(facelist, indent=4, sort_keys=True))

    # looping through all items and into "all" isn't being used but can be
    # by un-commenting draw-text below the loop

    all = ""
    for k, v in face.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                if isinstance(v2, dict):
                    for k3, v3 in v2.items():
                        k = str(k2) + " : " + str(k3)
                        v = str(v3)
                        all = all + k + " " + v + "\n"
                else:
                    k = str(k) + " : " + str(k2)
                    v = str(v2)
                    all = all + k + " " + v + "\n"
        else:
            k = str(k)
            v = str(v)
            all = all + k + " " + v + "\n"

    fa = face["faceAttributes"]
    faceId = face["faceId"]
    # print(faceId)
    fr = face["faceRectangle"]
    age = fa["age"]
    gender = fa["gender"]
    emotion = fa["emotion"]
    emotions = ""

    for k, v in emotion.items():
        k = str(k)
        v = str(v)
        emotions = emotions + k + " " + v + "\n"

    face_count += 1

    info = str(gender) + "\n" + str(emotions) + '\n Guessed age:' + str(age) + '\n ID:' + str(faceId)
    draw.rectangle(getRectangle(face), outline='red')
    origin = (fr["left"], fr["top"])
    draw.text((origin[0], origin[1]), info, (255, 255, 255), font)
#    draw.text((origin[0], origin[1]), all, (255, 255, 255), font)

face_count = str(face_count) + " faces"
draw.text((10, 1), face_count, (255, 255, 255), font)

image.save('out.jpg')
image.show()

# writing the json data into the exif fields of the output jpg

metadata = pyexiv2.ImageMetadata('out.jpg')
metadata.read()

# info = metadata.exif_keys
# for key in info:
    # print("key: " + str(key))

metadata['Exif.Photo.UserComment'] = json.dumps(vision)
metadata['Exif.Image.Make'] = 'python'
try:
    metadata.write()
except IOError:
    print('An error occured trying to read the file.')
except:
    print('error writing exif data')

# printing the exif data to check it was all written
import pprint
metadata = pyexiv2.ImageMetadata('out.jpg')
metadata.read()
userdata = json.loads(metadata['Exif.Photo.UserComment'].value)
pprint.pprint(userdata)
