import json
import numpy as np
import cv2
import requests
from utils import *
from darknet import Darknet
from skimage.metrics import structural_similarity as ssim

cfg_file = './cfg/yolov3.cfg'
weight_file = './weights/yolov3.weights'
namesfile = './data/coco.names'

m = Darknet(cfg_file)
m.load_weights(weight_file)
class_names = load_class_names(namesfile)

nms_thresh = 0.6
iou_thresh = 0.4

campione = cv2.imread('./public/campione.jpg')

istogrammi = {'red': [], 'green': [], 'blue': [], 'gray': []}

img1 = cv2.cvtColor(campione, cv2.COLOR_BGR2GRAY)
istogrammi['gray'] = cv2.calcHist([img1], [0], None, [256], [0, 256])

img1 = cv2.cvtColor(campione, cv2.COLOR_BGR2RGB)

istogrammi['red'] = cv2.calcHist([img1], [0], None, [256], [0, 256])
istogrammi['green'] = cv2.calcHist([img1], [1], None, [256], [0, 256])
istogrammi['blue'] = cv2.calcHist([img1], [2], None, [256], [0, 256])

resized_image = cv2.resize(img1, (m.width, m.height))

boxes = detect_objects(m, resized_image, iou_thresh, nms_thresh)

oggetti = {}

for i in range(len(boxes)):
    box = boxes[i]
    if len(box) >= 7 and class_names:
        cls_conf = box[5]
        cls_id = box[6]
        oggetti[cls_id] = cls_conf

nuovaImmagine = {'istogrammi': {}, 'oggetti': {}}
nuovaImmagine['istogrammi'] = istogrammi
nuovaImmagine['oggetti'] = oggetti


while True:

    newCampione = cv2.imread('./public/campione.jpg')

    with open('./algWeights.json') as algWeightsFile:
        algWeights = json.load(algWeightsFile)
        histVal = float(algWeights['hist'])
        objectVal = float(algWeights['yolo'])
        ssimVal = float(algWeights['ssim'])
        print("Pesi degli algoritmi aggiornati")

    if(not(newCampione.shape == campione.shape and not(np.bitwise_xor(newCampione, campione).any()))):
        print("Immagine campione modificata, ricontrollo il campione")
        campione = newCampione

        istogrammi = {'red': [], 'green': [], 'blue': [], 'gray': []}

        img1 = cv2.cvtColor(campione, cv2.COLOR_BGR2GRAY)
        istogrammi['gray'] = cv2.calcHist([img1], [0], None, [256], [0, 256])

        img1 = cv2.cvtColor(campione, cv2.COLOR_BGR2RGB)

        istogrammi['red'] = cv2.calcHist([img1], [0], None, [256], [0, 256])
        istogrammi['green'] = cv2.calcHist([img1], [1], None, [256], [0, 256])
        istogrammi['blue'] = cv2.calcHist([img1], [2], None, [256], [0, 256])

        resized_image = cv2.resize(img1, (m.width, m.height))

        boxes = detect_objects(m, resized_image, iou_thresh, nms_thresh)

        oggetti = {}

        for i in range(len(boxes)):
            box = boxes[i]
            if len(box) >= 7 and class_names:
                cls_conf = box[5]
                cls_id = box[6]
                oggetti[cls_id] = cls_conf

        nuovaImmagine = {'istogrammi': {}, 'oggetti': {}}
        nuovaImmagine['istogrammi'] = istogrammi
        nuovaImmagine['oggetti'] = oggetti

    with open('./images.json') as json_data:
        images = json.load(json_data)

        for item in images:

            if 'perc' not in item:

                path = './public/' + item['path']
                print(path)
                img = cv2.imread(path)

                ID = item['ID']

                print('Analyzing image ID ' + str(ID) + '...')

                istogrammi = {'red': [], 'green': [], 'blue': [], 'gray': []}

                img1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                istogrammi['gray'] = cv2.calcHist(
                    [img1], [0], None, [256], [0, 256])

                img1 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                istogrammi['red'] = cv2.calcHist(
                    [img1], [0], None, [256], [0, 256])
                istogrammi['green'] = cv2.calcHist(
                    [img1], [1], None, [256], [0, 256])
                istogrammi['blue'] = cv2.calcHist(
                    [img1], [2], None, [256], [0, 256])

                resized_image = cv2.resize(img1, (m.width, m.height))

                boxes = detect_objects(
                    m, resized_image, iou_thresh, nms_thresh)

                oggetti = {}

                for i in range(len(boxes)):
                    box = boxes[i]
                    if len(box) >= 7 and class_names:
                        cls_conf = box[5]
                        cls_id = box[6]
                        oggetti[cls_id] = cls_conf

                item['istogrammi'] = istogrammi
                item['oggetti'] = oggetti

                istogrammi = item['istogrammi']

                percHistGray = (
                    1+cv2.compareHist(istogrammi['gray'], nuovaImmagine["istogrammi"]['gray'], cv2.HISTCMP_CORREL))*50
                percHistRed = (
                    1+cv2.compareHist(istogrammi['red'], nuovaImmagine["istogrammi"]['red'], cv2.HISTCMP_CORREL))*50
                percHistGreen = (
                    1+cv2.compareHist(istogrammi['green'], nuovaImmagine["istogrammi"]['green'], cv2.HISTCMP_CORREL))*50
                percHistBlue = (
                    1+cv2.compareHist(istogrammi['blue'], nuovaImmagine["istogrammi"]['blue'], cv2.HISTCMP_CORREL))*50

                percHist = (percHistGray+percHistRed +
                            percHistGreen+percHistBlue)/4

                oggetti = item['oggetti']

                tmp = 0
                percOggetti = 0.0
                for (oggKey, oggValue) in nuovaImmagine["oggetti"].items():
                    tmp += 1
                    for (key, value) in oggetti.items():
                        if oggKey == key:
                            percOggetti += (value.item() * oggValue.item())

                percOggetti = (percOggetti/tmp)*100
                if percOggetti > 100:
                    percOggetti = 100

                img1ssim = cv2.resize(img, (1000, 1000))
                img2ssim = cv2.resize(campione, (1000, 1000))
                percSSIM = (ssim(img1ssim, img2ssim, multichannel=True))*100

                comparison = (
                    histVal*percHist+objectVal*percOggetti+ssimVal*percSSIM)/100

                comparison = round(comparison, 2)

                print('Sending request to update image ID ' +
                      str(ID) + ' with percentage ' + str(comparison))

                request = requests.get(
                    'http://localhost:3000/util/pyupdate/' + str(ID) + '/' + str(comparison))

                break
