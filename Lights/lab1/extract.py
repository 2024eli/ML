import cv2

img = cv2.imread('lights_on.png') # reading in the image

# setting window parameters
cv2.namedWindow('Image', cv2.WINDOW_NORMAL) 
cv2.resizeWindow("Image", 1200, 1800)

# modifying image to make light detection easier
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # convert to gray
blurred = cv2.GaussianBlur(gray, (3, 3), 0) # blurring picture
thresh = cv2.erode(blurred, None, iterations=1)
thresh = cv2.dilate(thresh, None, iterations=1)
_, thresh = cv2.threshold(thresh, 20, 255, cv2.THRESH_BINARY) #setting a threshold of colors that can be white

cv2.imwrite("thresh.jpg", thresh)

# displaying the image
cv2.imshow("Image", img)
cv2.waitKey(0)

# Finding and counting contours
cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
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

#saving output email and showing
cv2.imwrite("output.jpg", out)
cv2.imshow("Image", out)
cv2.waitKey(0)

print("Number of lights:", len(lights))

cv2.destroyAllWindows()