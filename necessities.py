from darkflow.net.build import TFNet
import matplotlib.pyplot as plt
import cv2

def convert2ROI(corner1, corner2):
    return [corner1[0], corner1[1], corner2[0]-corner1[0], corner2[1]-corner1[1]]

def convert2Rect(item):
    return {
    'topleft': {
    'x': item[0],
    'y': item[1]
    },
    'bottomright':{
    'x':item[0]+item[2],
    'y':item[1]+item[3]
    }
    }

def correlated(item1, item2, image):
    imagey= image[0]
    imagex= image[1]
    imagez= image[2]
    tl11= item1['topleft']['x']
    tl12= item1['topleft']['y']
    tl21= item2['topleft']['x']
    tl22= item2['topleft']['y']

    br11=item1['bottomright']['x']
    br12=item1['bottomright']['y']
    br21=item2['bottomright']['x']
    br22=item2['bottomright']['y']

    c1=[(tl11+br11)/2, (tl12+br12)/2]
    c2=[(tl21+br21)/2, (tl22+br22)/2]
    k=10
    k2=2
    k3=2
    if ((c1[0]>k3*imagex/10)&(c1[0]<(10-k3)*imagex/10)&(c1[1]>k2*imagey/10)&(c1[1]<(10-k2)*imagey/10))!=1:
        return 1
    # if ((k*tl11+br11)<=(k+1)*c2[0])&((1*tl11+k*br11)>=(k+1)*c2[0])&((k*tl12+br12)<=(k+1)*c2[1])&((tl11+k*br11>=(k+1)*c2[1])):
    #     return 1
    # else:
    #     print "Uncorrelated in pos 2"
    if (c2[0]<br11)&((c2[0]>tl11))&((c2[1]<br12))&(c2[1]>tl12):
        return 1
    return 0

def cease(item1, item2):
    if (item1['topleft']==item2['topleft'])&(item1['bottomright']==item2['bottomright']):
        print item1
        print item2
        print "yes, returned"
        return 1
    return 0

def outOfRegion(item1, image):
    imagey= image[0]
    imagex= image[1]
    imagez= image[2]
    tl11= item1['topleft']['x']
    tl12= item1['topleft']['y']

    br11=item1['bottomright']['x']
    br12=item1['bottomright']['y']

    c1=[(tl11+br11)/2, (tl12+br12)/2]
    k3=1
    k2=2
    if ((c1[0]>k3*imagex/10)&(c1[0]<(10-k3)*imagex/10)&(c1[1]>k2*imagey/10)&(c1[1]<(10-k2)*imagey/10))!=1:
        return 1
    return 0
def crossed(item1, item2, p1, p2):
    print "item1 : ", item1
    print "item2 : ", item2
    slope=(p1[1]-p2[1]*1.0)/(p1[0]-p2[0]*1.0)
    print "slope ; ", slope
    value1=item1[1]-slope*item1[0]-p1[1]+p1[0]*slope
    print "value1 : ", value1

    value2=item2[1]*1.0-slope*item2[0]-p1[1]+p1[0]*slope
    print "value2 : ", value2

    if (value1<0)&(value2>=0):
        return 1
    if (value1>=0)&(value2<0):
        return -1
    return 0
