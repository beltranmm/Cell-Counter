# Matthew Beltran
# 10/22/2024



import countCells as cc
#import cellCounterGUI


def main():
    # generate UI
    print("Welcome to cell counter")

    #imageLoc = input("Enter file location: ")
    imageLoc = "test_image.tif"

    # call cell counter
    cc.countCells(imageLoc)

if __name__ == "__main__":
    main()