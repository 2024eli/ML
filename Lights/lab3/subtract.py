import cv2
from imutils import contours
import imutils
from match import matched

#image processing
def preprocess(gray):
    blurred = cv2.GaussianBlur(gray, (1, 1), 1)
    thresh = cv2.erode(blurred, None, iterations=0)
    thresh = cv2.dilate(thresh, None, iterations=1)
    thresh = cv2.erode(thresh, None, iterations=0)
    thresh = cv2.convertScaleAbs(thresh, alpha=1, beta=0)
    return thresh

#find contour and return in a form readable for the rest of my code
def findCnt(thresh): 
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts, _ = contours.sort_contours(cnts)

#take in the image
onimg = cv2.imread("a.png")
offimg = cv2.imread("b.png")
offimg = matched(onimg, offimg) # gets rid of jitter by using SIFT and aligning through transformations

onimg = preprocess(onimg)
offimg = preprocess(offimg)

#gray-ify the image
ongray = cv2.cvtColor(onimg, cv2.COLOR_BGR2GRAY)
offgray = cv2.cvtColor(offimg, cv2.COLOR_BGR2GRAY)

#establish thresholds for the image
_, onthresh = cv2.threshold(ongray, 80, 255, cv2.THRESH_BINARY)
_, offthresh = cv2.threshold(offgray, 80, 255, cv2.THRESH_BINARY)

cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
cv2.resizeWindow("Image", 1800, 1200)

i = 0

# Displaying the image
cv2.imshow("Image", onimg)

cv2.namedWindow('onthresh', cv2.WINDOW_NORMAL)
cv2.resizeWindow("onthresh", 1800, 1200)
cv2.imshow('onthresh', onthresh)

cv2.namedWindow('offthresh', cv2.WINDOW_NORMAL)
cv2.resizeWindow("offthresh", 1800, 1200)
cv2.imshow('offthresh', offthresh)

onpoints = findCnt(onthresh)
offpoints = findCnt(offthresh)
print(f"onpoints count: {len(onpoints)}, offpoints count: {len(offpoints)} \nlights count: {len(onpoints)-len(offpoints)}")

#subtracting the two images
subtracted = cv2.subtract(onthresh, offthresh) 
subpoints = findCnt(subtracted)
cv2.imshow("s", subtracted)
s = onimg.copy() 

#labeling the image where lights aren't on (captures the extraneous)
for (i, c) in enumerate(onpoints):
    (x, y, w, h) = cv2.boundingRect(c)
    ((cX, cY), radius) = cv2.minEnclosingCircle(c)
    cv2.circle(onimg, (int(cX), int(cY)), int(radius),
                (200, 0, 200), 3)
cv2.imshow("lights from onimg", onimg)

#labeling lights from image where they're on
for (i, c) in enumerate(offpoints):
    (x, y, w, h) = cv2.boundingRect(c)
    ((cX, cY), radius) = cv2.minEnclosingCircle(c)
    cv2.circle(offimg, (int(cX), int(cY)), int(radius),
                (200, 0, 200), 3)
cv2.imshow("lights from offimg", offimg)

#labels lights with the extraneous lights subtracted out
for (i, c) in enumerate(subpoints):
    (x, y, w, h) = cv2.boundingRect(c)
    ((cX, cY), radius) = cv2.minEnclosingCircle(c)
    cv2.circle(s, (int(cX), int(cY)), int(radius),
                (200, 0, 200), 3)
cv2.imshow("subtracted", s)
print("subpoints ", len(subpoints))
cv2.waitKey(0)

cv2.destroyAllWindows()
