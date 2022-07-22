import math
import sys
import statistics
import cv2
import pytesseract
from pathlib import Path
from PIL import Image, ImageFilter
from matplotlib import pyplot
from matplotlib.patches import Rectangle
from webcolors import rgb_to_name

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
sys.setrecursionlimit(5000)

# import our basic, light-weight png reader library
import imageIO.png

# this function reads an RGB color png file and returns width, height, as well as pixel arrays for r,g,b
def readRGBImageToSeparatePixelArrays(input_filename):

    image_reader = imageIO.png.Reader(filename=input_filename)
    # png reader gives us width and height, as well as RGB data in image_rows (a list of rows of RGB triplets)
    (image_width, image_height, rgb_image_rows, rgb_image_info) = image_reader.read()

    print("read image width={}, height={}".format(image_width, image_height))

    # our pixel arrays are lists of lists, where each inner list stores one row of greyscale pixels
    pixel_array_r = []
    pixel_array_g = []
    pixel_array_b = []

    for row in rgb_image_rows:
        pixel_row_r = []
        pixel_row_g = []
        pixel_row_b = []
        r = 0
        g = 0
        b = 0
        for elem in range(len(row)):
            # RGB triplets are stored consecutively in image_rows
            if elem % 3 == 0:
                r = row[elem]
            elif elem % 3 == 1:
                g = row[elem]
            else:
                b = row[elem]
                pixel_row_r.append(r)
                pixel_row_g.append(g)
                pixel_row_b.append(b)

        pixel_array_r.append(pixel_row_r)
        pixel_array_g.append(pixel_row_g)
        pixel_array_b.append(pixel_row_b)

    return (image_width, image_height, pixel_array_r, pixel_array_g, pixel_array_b)


# a useful shortcut method to create a list of lists based array representation for an image, initialized with a value
def createInitializedGreyscalePixelArray(image_width, image_height, initValue = 0):

    new_array = [[initValue for x in range(image_width)] for y in range(image_height)]
    return new_array

def turncolor(pixr, pixg, pixb, image_width, image_height):
    finallist = createInitializedGreyscalePixelArray(image_width, image_height)
    for rows in range(image_height):
        for nums in range(image_width):
            r = pixr[rows][nums]
            g = pixg[rows][nums]
            b = pixb[rows][nums]
            grey = int(round(0.33333 * r + 0.33333 * g + 0.33333 * b))
            if grey > 255:
                grey = 255
            elif grey < 0:
                grey = 0
            finallist[rows][nums] = grey
    return finallist

def turngrey(pixr, pixg, pixb, image_width, image_height):
    finallist = createInitializedGreyscalePixelArray(image_width, image_height)
    for rows in range(image_height):
        for nums in range(image_width):
            r = pixr[rows][nums]
            g = pixg[rows][nums]
            b = pixb[rows][nums]
            grey = int(round(0.299 * r + 0.587 * g + 0.114 * b))
            if grey > 255:
                grey = 255
            elif grey < 0:
                grey = 0
            finallist[rows][nums] = grey
    return finallist

def stretch(pixel_array, image_width, image_height):
    finallist = createInitializedGreyscalePixelArray(image_width, image_height)
    maxi = 0
    mini = 999
    for rows in pixel_array:
        for nums in rows:
            if nums > maxi:
                maxi = nums
                
            if nums < mini:
                mini = nums
                
    if maxi == mini:
        return finallist
    
    for rows in range(image_height):
        for nums in range(image_width):
            if pixel_array[rows][nums] == mini:
                pixel_array[rows][nums] = 0
            elif pixel_array[rows][nums] == maxi:
                pixel_array[rows][nums] = 255
            else:
                pixel_array[rows][nums] = round((255 / (maxi - mini)) * (pixel_array[rows][nums] - mini))
    return pixel_array

def compmean5x5(pixel_array, image_width, image_height):
    finallist = createInitializedGreyscalePixelArray(image_width, image_height)
    for rows in range(image_height):
        for nums in range(image_width):
            list1=[]
            rowv = [-2,-1,0,1,2]
            numv = [-2,-1,0,1,2]
            for row in rowv:
                for num in numv:
                    try:
                        list1.append(pixel_array[row+rows][num+nums])
                    except(IndexError):
                        list1.append(0)
            finallist[rows][nums] = round(statistics.pstdev(list1))
    return finallist

def thresh(pixel_array, image_width, image_height):
    finallist = createInitializedGreyscalePixelArray(image_width, image_height)
    for rows in range(image_height):
        for nums in range(image_width):
            if pixel_array[rows][nums] < 150:
                finallist[rows][nums] = 0
            else:
                finallist[rows][nums] = 255
    return finallist

def dilute(pixel_array, image_width, image_height):
    finallist = createInitializedGreyscalePixelArray(image_width, image_height)
    for rows in range(image_height):
        for nums in range(image_width):
            list1 = []
            rowv = [-1, 0, 1]
            numv = [-1, 0, 1]
            for r in rowv:
                for n in rowv:
                    try:
                        list1.append(pixel_array[r+rows][n+nums])
                    except(IndexError):
                        nothing=1
            if max(list1) > 0:
                finallist[rows][nums] = 1
    return finallist

def erode(pixel_array, image_width, image_height):
    finallist = createInitializedGreyscalePixelArray(image_width, image_height)
    for rows in range(1, image_height-1):
        for nums in range(1, image_width-1):
            list1 = []
            rowv = [-1, 0, 1]
            numv = [-1, 0, 1]
            for r in rowv:
                for n in rowv:
                    list1.append(pixel_array[r+rows][n+nums])
            if min(list1) > 0:
                finallist[rows][nums] = 1
    return finallist

def fire(counter, pixel_array, finallist, rows, nums):
    ind1 = 0
    ind2 = 0
    ind3 = 0
    ind4 = 0
    if pixel_array[rows+1][nums] > 0 and finallist[rows+1][nums] == 0:
        finallist[rows+1][nums] = counter
        ind1 = 1
        
    if pixel_array[rows-1][nums] > 0 and finallist[rows-1][nums] == 0:
        finallist[rows-1][nums] = counter
        ind2 = 1
        
    if pixel_array[rows][nums+1] > 0 and finallist[rows][nums+1] == 0:
        finallist[rows][nums+1] = counter
        ind3 = 1
        
    if pixel_array[rows][nums-1] > 0 and finallist[rows][nums-1] == 0:
        finallist[rows][nums-1] = counter
        ind4 = 1

    if ind1 == 1:
        finallist = fire(counter, pixel_array, finallist, rows+1, nums)

    if ind2 == 1:
        finallist = fire(counter, pixel_array, finallist, rows-1, nums)

    if ind3 == 1:
        finallist = fire(counter, pixel_array, finallist, rows, nums+1)

    if ind4 == 1:
        finallist = fire(counter, pixel_array, finallist, rows, nums-1)
    
    return finallist

def connected(pixel_array, image_width, image_height):
    finallist = createInitializedGreyscalePixelArray(image_width, image_height)
    counter = 1
    list1 = [0] * 100
    for rows in range(image_height):
        for nums in range(image_width):
            if pixel_array[rows][nums] > 0 and finallist[rows][nums] == 0:
                finallist[rows][nums] = counter
                finallist = fire(counter, pixel_array, finallist, rows, nums)
                counter += 1
            if finallist[rows][nums] > 0:
                list1[finallist[rows][nums]-1] += 1

    ratio = 0
    while ratio < 1.5 or ratio > 5:
        minr = 999
        minn = 999
        maxr = 0
        maxn = 0
        maxind = list1.index(max(list1)) + 1
        for rows in range(image_height):
            for nums in range(image_width):
                if finallist[rows][nums] == maxind:
                    if rows < minr:
                        minr = rows
                    if nums < minn:
                        minn = nums
                    if rows > maxr:
                        maxr = rows
                    if nums > maxn:
                        maxn = nums
        width = maxn - minn
        height = maxr - minr
        ratio = (width / height)
        if ratio < 1.5 or ratio > 5:
            list1[list1.index(max(list1))] = 0
    return(maxn, minn, maxr, minr)

    
    
    
# This is our code skeleton that performs the license plate detection.
# Feel free to try it on your own images of cars, but keep in mind that with our algorithm developed in this lecture,
# we won't detect arbitrary or difficult to detect license plates!
def main():

    command_line_arguments = sys.argv[1:]

    SHOW_DEBUG_FIGURES = True

    # this is the default input image filename
    input_filename = "numberplate1.png"

    if command_line_arguments != []:
        input_filename = command_line_arguments[0]
        SHOW_DEBUG_FIGURES = False

    output_path = Path("output_images")
    if not output_path.exists():
        # create output directory
        output_path.mkdir(parents=True, exist_ok=True)

    output_filename = output_path / Path(input_filename.replace(".png", "_output.png"))
    if len(command_line_arguments) == 2:
        output_filename = Path(command_line_arguments[1])


    # we read in the png file, and receive three pixel arrays for red, green and blue components, respectively
    # each pixel array contains 8 bit integer values between 0 and 255 encoding the color values
    (image_width, image_height, px_array_r, px_array_g, px_array_b) = readRGBImageToSeparatePixelArrays(input_filename)

    px_array = turngrey(px_array_r, px_array_g, px_array_b, image_width, image_height)
    px_array = stretch(px_array, image_width, image_height)
    
    contpx_array = compmean5x5(px_array, image_width, image_height)
    contpx_array = stretch(contpx_array, image_width, image_height)

    threshpx_array = thresh(contpx_array, image_width, image_height)

    dilutedpx_array = dilute(threshpx_array, image_width, image_height)
    dilutedpx_array = dilute(dilutedpx_array, image_width, image_height)
    dilutedpx_array = dilute(dilutedpx_array, image_width, image_height)
    dilutedpx_array = dilute(dilutedpx_array, image_width, image_height)
    dilutedpx_array = dilute(dilutedpx_array, image_width, image_height)
    

    erodedpx_array = erode(dilutedpx_array, image_width, image_height)
    erodedpx_array = erode(erodedpx_array, image_width, image_height)
    erodedpx_array = erode(erodedpx_array, image_width, image_height)
    erodedpx_array = erode(erodedpx_array, image_width, image_height)
    erodedpx_array = erode(erodedpx_array, image_width, image_height)
    

    fig1, axs1 = pyplot.subplots(3, 3)
    axs1[0, 0].set_title('Input image in grey scale')
    axs1[0, 0].imshow(px_array, cmap='gray')
    axs1[0, 1].set_title('Input image after std dev')
    axs1[0, 1].imshow(contpx_array, cmap='gray')
    axs1[0, 2].set_title('Input image after dilution and erosion')
    axs1[0, 2].imshow(erodedpx_array, cmap='gray')
    listc = connected(erodedpx_array,image_width, image_height)
    
    newimage = Image.open(input_filename)
    newimage1 = newimage.crop((listc[1], listc[3], listc[0], listc[2]))

    textimage = pytesseract.image_to_string(newimage1, lang='eng',config='--psm 6 --oem 3')
    textimage = filter(str.isalnum, textimage)
    textimage = "".join(textimage)
    if len(textimage) > 7:
        textimage = textimage[-7:]
    
    axs1[1, 1].set_title("Number plate is: " + textimage)
    axs1[1, 1].imshow(newimage1, cmap='gray')

    
    imcc1 = newimage.getpixel((listc[0] - (listc[0]-listc[1])/2, abs(listc[3] - 150)))
    imcc2 = newimage.getpixel((listc[0] - (listc[0]-listc[1])/2, abs(listc[3] - 100)))
    imcc3 = newimage.getpixel((listc[0] - (listc[0]-listc[1])/2, abs(listc[3] - 50)))
    imcl1 = newimage.getpixel((listc[1], abs(listc[3] - 150)))
    imcl2 = newimage.getpixel((listc[1], abs(listc[3] - 100)))
    imcl3 = newimage.getpixel((listc[1], abs(listc[3] - 50)))
    imcr1 = newimage.getpixel((listc[0], abs(listc[3] - 150)))
    imcr2 = newimage.getpixel((listc[0], abs(listc[3] - 100)))
    imcr3 = newimage.getpixel((listc[0], abs(listc[3] - 50)))

    iml1 = newimage.getpixel((abs(listc[1] - 150), listc[2]))
    iml2 = newimage.getpixel((abs(listc[1] - 100), listc[2]))
    iml3 = newimage.getpixel((abs(listc[1] - 50), listc[2]))
    imr1 = newimage.getpixel((abs(listc[0] + 150), listc[2]))
    imr2 = newimage.getpixel((abs(listc[0] + 100), listc[2]))
    imr3 = newimage.getpixel((abs(listc[0] + 50), listc[2]))

    rlist = [imcc1[0], imcc2[0], imcc3[0], imcl1[0], imcl2[0], imcl3[0], imcr1[0], imcr2[0], imcr3[0], iml1[0], iml2[0], iml3[0], imr1[0], imr2[0], imr3[0]]
    glist = [imcc1[1], imcc2[1], imcc3[1], imcl1[1], imcl2[1], imcl3[1], imcr1[1], imcr2[1], imcr3[1], iml1[1], iml2[1], iml3[1], imr1[1], imr2[1], imr3[1]]
    blist = [imcc1[2], imcc2[2], imcc3[2], imcl1[2], imcl2[2], imcl3[2], imcr1[2], imcr2[2], imcr3[2], iml1[2], iml2[2], iml3[2], imr1[2], imr2[2], imr3[2]]

    rlist = sorted(rlist)
    glist = sorted(glist)
    blist = sorted(blist)
    
    rlist.pop(0)
    glist.pop(0)
    blist.pop(0)
    rlist.pop(-1)
    glist.pop(-1)
    blist.pop(-1)
    rlist.pop(0)
    glist.pop(0)
    blist.pop(0)
    rlist.pop(-1)
    glist.pop(-1)
    blist.pop(-1)

    imc = (round(statistics.mean(rlist)), round(statistics.mean(glist)), round(statistics.mean(blist)))

    try:
        namedcolor = rgb_to_name(imc, spec='css3')
        printer = "The car is: " + namedcolor
    except(ValueError):
        printer = "This is the car color"

    
    colorimage = Image.new("RGB", (image_width, image_height))
    data = [imc for y in range(colorimage.size[1]) for x in range(colorimage.size[0])]
    colorimage.putdata(data)

    axs1[1, 2].set_title(printer)
    axs1[1, 2].imshow(colorimage, cmap=None)

    blurring = newimage1.filter(ImageFilter.GaussianBlur(radius=10))
    newimage.paste(blurring, (listc[1], listc[3], listc[0], listc[2]))

    axs1[2, 0].set_title("Original image with license plate blurred")
    axs1[2, 0].imshow(newimage, cmap=None)

    axs1[2, 1].set_title("None")
    
    axs1[2, 2].set_title("None")
    
    # compute a dummy bounding box centered in the middle of the input image, and with as size of half of width and height
    bbox_min_x = listc[1]
    bbox_max_x = listc[0]
    bbox_min_y = listc[3]
    bbox_max_y = listc[2]


    # Draw a bounding box as a rectangle into the input image
    axs1[1, 0].set_title('Final image of detection')
    axs1[1, 0].imshow(px_array, cmap='gray')
    rect = Rectangle((bbox_min_x, bbox_min_y), bbox_max_x - bbox_min_x, bbox_max_y - bbox_min_y, linewidth=1,
                     edgecolor='g', facecolor='none')
    axs1[1, 0].add_patch(rect)



    # write the output image into output_filename, using the matplotlib savefig method
    extent = axs1[1, 0].get_window_extent().transformed(fig1.dpi_scale_trans.inverted())
    pyplot.savefig(output_filename, bbox_inches=extent, dpi=600)

    if SHOW_DEBUG_FIGURES:
        # plot the current figure
        pyplot.show()


if __name__ == "__main__":
    main()
