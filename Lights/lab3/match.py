import numpy as np
import cv2
import matplotlib.pyplot as plt

def matched(img2, img1):
    # Initiate SIFT detector
    sift = cv2.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)

    # Initialize matcher
    matcher = cv2.BFMatcher()

    # Match descriptors
    matches = matcher.knnMatch(des1, des2, k=2)
    good_matches = [m for m, n in matches if m.distance<0.7*n.distance]

    # Get corresponding keypoints
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    # Find transformation matrix using RANSAC
    M, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC)

    # Apply transformation to image1 to align it with image2
    aligned_image = cv2.warpPerspective(img1, M, (img2.shape[1], img2.shape[0]))

    # Show the aligned image
    cv2.imwrite('aligned_image.jpg', aligned_image)

    return aligned_image

matched(cv2.imread("a.png"), cv2.imread("b.png"))

