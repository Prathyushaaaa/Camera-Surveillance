import numpy as np
import cv2 as cv
import sys
import necessities as nc
from darkflow.net.build import TFNet
import copy

linep1=(114, 132)
linep2=(577, 178)
people_count=0

options = {"model": "cfg/yolo.cfg", "load": "yolov2.weights", "threshold": 0.25}
tfnet = TFNet(options)

cv.namedWindow("tracking")
camera = cv.VideoCapture("sample_img/pedestrians.mp4")

fourcc = cv.VideoWriter_fourcc(*'XVID')
out = cv.VideoWriter('output.avi',fourcc, 20.0, (1920/3,1080/3))

tracker = cv.MultiTracker()
trackerObjects=[]
newTrackerObjects=[]
boxesHistory=[]
boxesStopped=[]

ok, image=camera.read()
image=cv.resize(image,(1920/3,1080/3))
if not ok:
    print('Failed to read video')
    exit()
count=0

while camera.isOpened():
    count+=1
    print count
    newTrackerObjects=[]
    ok, image=camera.read()
    if count >700:
        break
    if count<200:
        continue
    image=cv.resize(image,(1920/3,1080/3))
    if not ok:
        print 'no image to read'
        break
        count+=1
        print count
    #___________________________________________________________________________
    image=cv.cvtColor(image, cv.COLOR_BGR2RGB)
    result= tfnet.return_predict(image)
    personsTFNet=[i for i in result if i['label']=='person']
    print len(personsTFNet)
    if trackerObjects==None:
        for item in personsTFNet:
            if nc.correlated(personsTFNet[0], personsTFNet[0], image.shape)!=1:
                trackerObjects=personsTFNet[0]
                break
            else:
                continue

    for item in personsTFNet:
        item_found=0
        for iter2 in range(len(trackerObjects)):
            item2=trackerObjects[iter2]
            if (nc.correlated(item, item2, image.shape)==1)&(boxesStopped[iter2]<4):
                item_found+=1
        if item_found==0:
            print "appended"
            newTrackerObjects.append(item)

    for item in newTrackerObjects:
        trackerObjects.append(item)
    #___________________________________________________________________________
    #This section is for putting a flag on the stationary trackers.
    for item in newTrackerObjects:
        boxesStopped.append(0)
    for iter in range(len(boxesHistory)):
        if nc.outOfRegion(trackerObjects[iter], image.shape)==1:
            boxesStopped[iter]=4
        elif nc.cease(boxesHistory[iter], trackerObjects[iter]):
            boxesStopped[iter]+=1
        elif boxesStopped[iter]<4:
            boxesStopped[iter]=0
    print len(boxesHistory)
    print len(trackerObjects)
    #___________________________________________________________________________
        #Counting objects
    for iter in range(len(boxesHistory)):
        if boxesStopped[iter]<4:
            c1=[(boxesHistory[iter]['topleft']['x']+boxesHistory[iter]['bottomright']['x'])/2.0, (boxesHistory[iter]['topleft']['y']+boxesHistory[iter]['bottomright']['y'])/2.0]
            c2=[(trackerObjects[iter]['topleft']['x']+trackerObjects[iter]['bottomright']['x'])/2.0, (trackerObjects[iter]['topleft']['y']+trackerObjects[iter]['bottomright']['y'])/2.0]
            print "c1 : ", str(c1)
            print "c2 : ", str(c2)
            people_count=people_count+nc.crossed(c1, c2, linep1, linep2)
    text= "people count: "+str(people_count)
    print text
    cv.putText(image, text, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), lineType=cv.LINE_AA)
    # #___________________________________________________________________________
    boxesHistory=copy.deepcopy(trackerObjects)
    #___________________________________________________________________________
    [tracker.add(cv.TrackerMIL_create(), image, tuple(nc.convert2ROI([item['topleft']['x'],item['topleft']['y']], [item['bottomright']['x'],item['bottomright']['y']]))) for item in newTrackerObjects]
    ok, boxes = tracker.update(image)
    for iter in range(len(boxes)):
        newlocation=nc.convert2Rect(boxes[iter])
        trackerObjects[iter]['topleft']['x']=int(newlocation['topleft']['x'])
        trackerObjects[iter]['topleft']['y']=int(newlocation['topleft']['y'])
        trackerObjects[iter]['bottomright']['x']=int(newlocation['bottomright']['x'])
        trackerObjects[iter]['bottomright']['y']=int(newlocation['bottomright']['y'])

    for iter in range(len(boxesHistory)):
        if nc.outOfRegion(trackerObjects[iter], image.shape)==1:
            boxesStopped[iter]=4
    #___________________________________________________________________________


    for iter in range(len(boxes)):
        newbox=boxes[iter]
        if boxesStopped[iter]< 4:
            p1 = (int(newbox[0]), int(newbox[1]))
            p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
            cv.rectangle(image, p1, p2, (200,0,0))

    cv.line(image,linep1, linep2, (255,0,0), 2)
    image=cv.cvtColor(image, cv.COLOR_RGB2BGR)
    out.write(image)
    cv.imshow('tracking', image)
    k = cv.waitKey(1)
    if k == 27 : break # esc pressed
camera.release()
out.release()
cv.destroyAllWindows()
