# Matthew Beltran
# 10/22/2024

from tkinter import *
from tkinter import ttk

import numpy as np
import matplotlib.pyplot as plt

from PIL import Image, ImageFilter

from skimage import color
from skimage.transform import hough_circle, hough_circle_peaks
from skimage.feature import canny
from skimage.draw import circle_perimeter
from skimage.util import img_as_ubyte


class CellCounter:

    def __init__(self, root):

        root.title("Cell Counter")
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
       
        self.fileLocation = StringVar()
        file_entry = ttk.Entry(mainframe, width=15, textvariable=self.fileLocation)
        file_entry.grid(column=2, row=1, sticky=(W, E))
        self.numCells = StringVar()
        self.deadCells = StringVar()
        self.liveCells = StringVar()

        ttk.Label(mainframe, textvariable=self.liveCells).grid(column=1, row=3, sticky=W)
        ttk.Label(mainframe, textvariable=self.deadCells).grid(column=2, row=3, sticky=W)
        ttk.Label(mainframe, textvariable=self.numCells).grid(column=3, row=3, sticky=W)
        ttk.Button(mainframe, text="Count Cells", command=self.countCells).grid(column=3, row=1, sticky=W)

        ttk.Label(mainframe, text="File Location:").grid(column=1, row=1, sticky=W)
        ttk.Label(mainframe, text="Live Cells").grid(column=1, row=2, sticky=W)
        ttk.Label(mainframe, text="Dead Cells").grid(column=2, row=2, sticky=W)
        ttk.Label(mainframe, text="Total Cells").grid(column=3, row=2, sticky=W)

        self.progBar = ttk.Progressbar(mainframe, orient='horizontal')
        self.progBar.grid(column=1, row=4, sticky=W)
        self.progBar['value'] = 0

        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        file_entry.focus()
        root.bind("<Return>", self.countCells)

    def countCells(self, *args):

        #try:
            # open image
            self.im_original = Image.open(self.fileLocation.get(), mode='r')

            # track progress
            print("counting cells")
            self.progBar['value'] = 20
            root.update()

            global interrupt; interrupt = False
            root.after(1, self.findCells)

            
            
        #except AttributeError:
        #except ValueError:
        #    print("File not found")

    def findCells(self, *args):

        # convert to greyscale
        im_original = self.im_original
        im = im_original.convert("L")
        # blur to reduce background noise
        im = im.filter(ImageFilter.BoxBlur(1))

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


        # return number of cells
        self.cellInfo = (cx, cy)

        # update progress bar
        self.progBar['value'] = 50
        root.update()

        # call next step
        root.after(1, self.isLive)

    def isLive(self, *args):
        
        # assign inputs
        cx = self.cellInfo[0]
        cy = self.cellInfo[1]
        im = self.im_original

        # assume cells are alive
        live = [1] * cx.size

        
        # subtract GB channels from R
        for i in range(im.size[0]):
            for j in range(im.size[1]):
                pixDiff = im.getpixel((i,j))[0] - np.max(im.getpixel((i,j))[1:2])
                if pixDiff < 0:
                    im.putpixel((i,j),(0,0,0))
                else:
                    im.putpixel((i,j),(pixDiff,0,0))


        im = im.filter(ImageFilter.MaxFilter(3))
        im = im.filter(ImageFilter.GaussianBlur(3))

        avgRed = np.max((20,np.mean(list(im.getdata(0)))))
        for i in range(len(cx)):
            # check if cell is red/dead
            if im.getpixel([cx[i],cy[i]])[0] > avgRed:
                live[i] = 0

        # Draw them
        fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 4))
        # convert to greyscale
        im = im.convert("L")
        image = color.gray2rgb(img_as_ubyte(im))
        # set radii
        radii = [10] * cx.size
        i = 0
        for center_y, center_x, radius in zip(cy, cx, radii):
            circy, circx = circle_perimeter(center_y, center_x, radius, shape=image.shape)
            if live[i] == 0:
                image[circy, circx] = (20, 20, 220)
            else:
                image[circy, circx] = (20, 220, 20)

        ax.imshow(image, cmap=plt.cm.gray)
        plt.show()

        # return number of cells
        self.live = live

        # update progress bar
        self.progBar['value'] = 80
        root.update()

        # call next step
        root.after(1, self.report)
        
    def report(self, *args):
        # return number of cells
        self.numCells.set(len(self.cellInfo[0]))
        self.deadCells.set(len(self.cellInfo[0]) - np.sum(self.live))
        self.liveCells.set(np.sum(self.live))

        # update progress bar
        self.progBar['value'] = 100
        root.update()

root = Tk()
CellCounter(root)
root.mainloop()