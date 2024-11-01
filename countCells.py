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


    # Circle Identification parameters
    min_radius = 10
    max_radius = 50
    circle_quality = 0.3

    # Hough circle identification
    hough_radii = np.arange(min_radius,max_radius,1)
    hough_res = hough_circle(edges, hough_radii)
    accums, cx, cy, radii = hough_circle_peaks(hough_res, hough_radii, min_xdistance=max_radius, min_ydistance=max_radius, threshold=circle_quality)


    # remove overlapping circles
    no_overlapping = False
    while no_overlapping == False:
        no_overlapping = True
        overlap_ind = []
        for i in range(len(radii)-1):
            for j in range(i+1,len(radii)):
                if pow(cx[i]-cx[j],2) + pow(cy[i]-cy[j],2) < pow(radii[i]+radii[j],2):
                    # track indices to remove
                    overlap_ind = np.append(overlap_ind,j)
                    no_overlapping = False
                    
            if no_overlapping == False:
                #remove circle j
                ind = overlap_ind.astype(int)
                accums = np.delete(accums,ind)
                cx = np.delete(cx,ind)
                cy = np.delete(cy,ind)
                radii = np.delete(radii,ind)
                print(len(radii))
                break



    # Draw them
    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 4))
    image = color.gray2rgb(img_as_ubyte(im))
    for center_y, center_x, radius in zip(cy, cx, radii):
        circy, circx = circle_perimeter(center_y, center_x, radius, shape=image.shape)
        image[circy, circx] = (220, 20, 20)

    ax.imshow(image, cmap=plt.cm.gray)
    plt.show()


    # Count Dead cells

    # subtract GB channels from R
    im = im_original
    for i in range(im.size[0]):
        for j in range(im.size[1]):
            pixDiff = im.getpixel((i,j))[0] - np.max(im.getpixel((i,j))[1:2])
            if pixDiff < 0:
                im.putpixel((i,j),(0,0,0))
            else:
                im.putpixel((i,j),(pixDiff,0,0))


    im = im.filter(ImageFilter.MaxFilter(3))
    im = im.filter(ImageFilter.GaussianBlur(3))


    # save modified image for testing
    im.save("editted_image.tif")

    #pix = im_original.load()
    avgRed = np.mean(list(im.getdata(0)))
    red_cell_count = 0
    for i in range(len(cx)):
        if im.getpixel([cx[i],cy[i]])[0] > avgRed:
            red_cell_count+= 1



    # return number of cells
    cellInfo = (len(radii), red_cell_count)

    return cellInfo