import cv2
from skimage import measure
import numpy as np

points = [] # list of points

# marking regions for a mask
def mouse_callback(event, x, y, flags, param):
  if event == cv2.EVENT_LBUTTONDOWN: # left mouse pad presses down
    points.append((x, y)) #adding to list of points
    if len(points) > 1: # connect lines if there's more than one point
      cv2.line(img, points[-2], points[-1], (0, 255, 0), 2)
    cv2.circle(img, (x, y), 5, (200, 0, 170), -1) # point designated by circle

img = cv2.imread('lights_on.png') # reading in the image

# setting window parameters
cv2.namedWindow('Image', cv2.WINDOW_NORMAL) 
cv2.resizeWindow("Image", 1200, 1800)

cv2.setMouseCallback('Image', mouse_callback) # enabling masking on image

# modifying image to make light detection easier
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # convert to gray
blurred = cv2.GaussianBlur(gray, (3, 3), 0) # blurring picture
thresh = cv2.erode(blurred, None, iterations=1)
thresh = cv2.dilate(thresh, None, iterations=1)
_, thresh = cv2.threshold(thresh, 10, 255, cv2.THRESH_BINARY) #setting a threshold of colors that can be white

labels = measure.label(thresh, background=0)
mask = np.zeros(thresh.shape, dtype="uint8")

while True:
  
  # Displaying the image
  cv2.imshow("Image", img)
  key = cv2.waitKey(1) & 0xFF

  # Press 'c' to clear polygons
  if key == ord('c'):
    points = [] # reset points
    img = cv2.imread('lights_on.png') # reset the image to unmarked

  # Press 'p' to create a polygon
  elif key == ord('p'):
    if len(points) >= 3: # so it qualifies for a polygon
      pts = np.array(points, np.int32)
      pts = pts.reshape((-1, 1, 2)) # change dimensions of array
      cv2.fillPoly(mask, [pts], (255, 255, 255)) # makes the masked part white (not a light)
      cv2.imwrite("thresh.jpg", thresh)
    points = [] # reset points for new polygon

  # Press 'm' to show the polygon masks
  elif key == ord('m'):
    for label in np.unique(labels):
      if label == 0:
        continue
      labelMask = np.zeros(thresh.shape, dtype="uint8") # creating the polygons
      labelMask[labels == label] = 255
      mask = cv2.add(mask, labelMask) # adding polygon to the mask image

    cv2.imwrite("mask.jpg", mask)
    cv2.imshow('Mask', mask)

    # Finding and counting contours
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    lights = []
    for contour in cnts:
      x, y, w, h = cv2.boundingRect(contour)
      (_, radius) = cv2.minEnclosingCircle(contour)
      if radius>40: # any areas with a radius greater than 40 is not a light
        continue
      lights.append((x, y, w, h)) # list of lights
    
    # label the image with detected lights
    out = img.copy()
    for x, y, w, h in lights:
      cv2.circle(out, (x + w // 2, y + h // 2), 2, (200, 0, 255), 2)
    
    cv2.imshow("Image", out)
    cv2.waitKey(0)

    cv2.imwrite("modified_christmas_lights.jpg", out)

    print("Number of lights: ", len(lights))

  # Press 'q' to quit
  elif key == ord('q'):
    break

cv2.destroyAllWindows()