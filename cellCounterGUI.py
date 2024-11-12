# Matthew Beltran
# 10/22/2024

from tkinter import *
from tkinter import ttk

#import countCells as cc
import numpy as np
import matplotlib.pyplot as plt

from PIL import Image, ImageFilter

from skimage import color
from skimage.transform import hough_circle, hough_circle_peaks
from skimage.feature import canny
from skimage.draw import circle_perimeter
from skimage.util import img_as_ubyte


print("cell counter GUI")


class CellCounterGUI:

    def __init__(self, root):

        print("init")

        root.title("Cell Counter")

        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
       

        self.fileLocation = "test_image.tif"
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

        self.progress = 0
        ttk.Progressbar(mainframe, orient='horizontal', variable=self.progress, maximum=3).grid(column=1, row=4, sticky=W)

        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        file_entry.focus()
        root.bind("<Return>", self.countCells)

    def countCells(self, *args):
        # open image
        im = Image.open(self.fileLocation, mode='r')

        # track progress
        print("counting cells")
        self.progress+=1

        cx, cy = self.findCells(im)

        print("countCells - counting dead cells")
        self.progress+=1

        ld = self.liveOrDead(im, cx, cy)

        # return number of cells
        self.numCells.set(len(cx))
        self.deadCells.set(red_cell_count)
        self.liveCells.set(len(radii) - red_cell_count)

    def findCells(im_original):

        # convert to greyscale
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

        # return number of cells
        cellInfo = (cx, cy)

        return cellInfo

    def liveOrDead(im, cx, cy):
        
        # Count Dead cells

        
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

        avgRed = np.mean(list(im.getdata(0)))
        red_cell_count = 0
        for i in range(len(cx)):
            if im.getpixel([cx[i],cy[i]])[0] > avgRed:
                red_cell_count+= 1



        # return number of cells
        
        

root = Tk()
CellCounterGUI(root)
root.mainloop()