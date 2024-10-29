# Matthew Beltran
# 10/22/2024

import numpy as np
import matplotlib.pyplot as plt

from PIL import Image, ImageFilter

from skimage import color
from skimage.transform import hough_circle, hough_circle_peaks
from skimage.feature import canny
from skimage.draw import circle_perimeter
from skimage.util import img_as_ubyte

print("Welcome to count cells")

def countCells(imageLoc):
    # open image
    im_original = Image.open(imageLoc, mode='r')
    #pix_original = im.load()

    # find cells

    # convert to greyscale
    im = im_original.convert("L")

    # blur to reduce background noise
    im = im.filter(ImageFilter.BoxBlur(1))

    # edge detection
    #im = im.filter(ImageFilter.FIND_EDGES)

    # turn into binary "white/black" image
    #pix = im.load()
    #print(pix[200,5])

    #for i in range(im.size[0]):
    #    #print(i)
    #    for j in range(im.size[1]):
    #        #pix[i,j] = (0,0,255)
    #        if pix[i,j] > 30:
    #            im.putpixel((i,j),(255))
    #        else:
    #            im.putpixel((i,j),(0))
    
    #im_u = img_as_ubyte(im)

    # canny "binary" edge-detection
    edges = canny(img_as_ubyte(im))

    # Hough circle identification
    hough_radii = np.arange(10,30,2)
    hough_res = hough_circle(edges, hough_radii)

    # display prominent circles
    # Select the most prominent 3 circles
    accums, cx, cy, radii = hough_circle_peaks(hough_res, hough_radii, min_xdistance=10, min_ydistance=10, threshold=0.3)


    # remove overlapping circles
    no_overlapping = False
    while no_overlapping == False:
        no_overlapping = True
        overlap_ind = 0
        for i in range(len(radii)-1):
            for j in range(i+1,len(radii)):
                if pow(cx[i]-cx[j],2) + pow(cy[i]-cy[j],2) < pow(radii[i]+radii[j],2):
                    # exit loops
                    overlap_ind = j
                    no_overlapping = False
                    break
            if no_overlapping == False:
                break


        #remove circle j
        accums = np.delete(accums,overlap_ind)
        cx = np.delete(cx,overlap_ind)
        cy = np.delete(cy,overlap_ind)
        radii = np.delete(radii,overlap_ind)
        print(len(radii))

    # Draw them
    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 4))
    image = color.gray2rgb(img_as_ubyte(im))
    for center_y, center_x, radius in zip(cy, cx, radii):
        circy, circx = circle_perimeter(center_y, center_x, radius, shape=image.shape)
        image[circy, circx] = (220, 20, 20)

    ax.imshow(image, cmap=plt.cm.gray)
    plt.show()

    # save modified image for testing
    im.save("editted_image.tif")

    cellInfo = "empty"

    return cellInfo