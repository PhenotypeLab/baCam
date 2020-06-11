import cv2
from os import path
import numpy as np
from four_points_edited import four_point_transform
dir_path = path.dirname(path.realpath(__file__))

def colorBalance(img, marker_coords):
    """
    Color correction based on a coloured template as objective. Uses the marker coordinates to find the reference

    :param img: numpy array image. Input image where the color correction is applied
    :return: numpy array image. Corrected input image
    """

    color_reference = path.join(dir_path, "reference.png")
    colors = ['b', 'g', 'r']
    #search for the template
    img_pattern, _=four_point_transform(img, marker_coords)
    #colour cuantization into 2 colours with k-means clustering
    Z = img_pattern.reshape((-1, 3))
    Z = np.float32(Z)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = 2
    ret, label, center = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    center = np.uint8(center)
    res = center[label.flatten()]
    img_pattern = res.reshape((img_pattern.shape))
    img_pattern = cv2.resize(img_pattern, (7,7), interpolation=cv2.INTER_LINEAR)
    #obtain the BGR values from the white area of the matched template
    h_p = img_pattern[3, 3]
    # obtain the BGR values from the black area of the matched template
    l_p = img_pattern[0,0]
    img_pattern=[h_p,l_p]
    img_reference = cv2.imread(color_reference, 1)
    h_r=img_reference[3, 3]
    l_r=img_reference[0,0]
    img_reference=[h_r, l_r]
    return [img_pattern,img_reference]