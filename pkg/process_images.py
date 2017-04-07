#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
 *  Remote Sensing for Damage Assessment
 *
 *  process_images.py
 *
 *  Created by Shari Matzner on 11/14/2015.
 *  Copyright © 2016, Battelle Memorial Institute.  All rights reserved.
 *
"""
import sys, getopt  # command line args
import glob         # file name pattern matching
import time         # get time for output dir name
import shutil       # copy files
import os           # file paths
import numpy as np
import cv2 # openCV
import rubble_detection_talbot as rub

def imshow(im,sf=1) :
    cv2.namedWindow('image',cv2.WINDOW_AUTOSIZE)
    im_small = cv2.resize(im, (0,0), fx=sf, fy=sf, interpolation=cv2.INTER_AREA)
    cv2.imshow('image',im_small)
    cv2.waitKey(0)
    cv2.destroyWindow('image')

def copy_worldfiles(srcpath,destpath,ext='jgw') :
    srclist = glob.glob(srcpath + '*' + ext)
    for f in srclist :
        shutil.copy(f,destpath)

def rescale(a, oldrange, newrange) :
    anew = newrange[0] + ((a - oldrange[0])/(oldrange[1] - oldrange[0])) * (newrange[1] - newrange[0])
    return anew

def getgray(imfilepath,roi=None) :
    # Load the image.
    # NOTE:  Should get metadata like resolution.
    im = cv2.imread(f)
    #
    # Convert to grayscale.
    # NOTE:  This is necessary.
    im = np.float32(im) * (1.0/255.)  # convert to float and scale
    imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY);
    if roi is not None :
        imroi = imgray[roi[1]:roi[1]+roi[3],roi[0]:roi[0]+roi[2]]
        imgray = imroi
    #
    return imgray
    
def write_image(im,outfilename) :
    # assume im is dytpe float32
    imout = rescale(im,(im.min(),im.max()),(0.0,1.0))
    imout = np.uint16(imout * ((2**16)-1))
    print("Writing " + outfilename)
    cv2.imwrite(outfilename, imout);

def main(argv):
    # runtime options
    inpath = ''     # default is current dir
    imfile_ext = '.jpg' # default image type
    outpath = ''    # default is inpath with "-rubble" appended 
    numbins = 9      # number of oriented gradient histogram bins
    W = 6            # window size for entropy calculation
    gradthresh = 0.5 # magnitude of gradient must be greater than this
    WRITE_FILES = False;

    usage = "\nprocess_images.py -i [input directory] -e [image file extension] -o [output directory]\n"
    try:
        opts, args = getopt.getopt(argv,"hi:e:o:")
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt == '-i':
            inpath = arg
        elif opt == '-e':
            imfile_ext = arg
            if not imfile_ext[0] == '.':
                imfile_ext = '.' + imfile_ext
        elif opt == '-o':
            outpath = arg

    if inpath == '':
        print("Please specify an input directory.", usage)
        sys.exit(2)
# Ike test
#inpath = 'Data/HurricaneIke/NOAA_Rapid-Response/Test/' 
#imfile_ext = '.JPG'
# Sandy test, images converted to UTM projection
#inpath = 'Data/HurricaneSandy/NOAA_Rapid-Response/Test2/'
#imfile_ext = '.jpg'

# The image files are .JPG (Note the extension in all upper case.)
# Each image file has three companion files, with the same filename
# and the following extensions:
# .jgw -- world file, see http://en.wikipedia.org/wiki/World_file
# .met -- text file of metadata in Federal Geographic Data Commitee (FGDC) standard format
# .xml -- text file of metadata in xml formats
#-------------------------------------------------
    # Get list of image files in input directory.
    dirfilestr = os.path.join(inpath,'*' + imfile_ext)
    print("Getting list of image files ", dirfilestr)
    imfilelist = glob.glob(dirfilestr)
    if not len(imfilelist) > 0:
        print("No image files found.") 
        sys.exit(2)

    print("Processing", str(len(imfilelist)), "files")
    # Create output dir.
    if outpath == '':
        outpath = time.strftime("%Y-%m-%d_%H%M%S") + '_rubble/'
    print("Creating output directory " + outpath)
    os.makedirs(outpath)
    copy_worldfiles(inpath,outpath)
    #outfile_ext = '.png'

    # Process each file.
    for f in imfilelist:
        print(f)
        # test smaller region
        #roi = [4436, 2000, 800, 800] # [x,y,width,height]
        #imtest = getgray(f,roi)
        imtest = getgray(f)
        outfilename = outpath + os.path.splitext(os.path.basename(f))[0] + outfile_ext
        write_image(imtest, outfilename)
        #
        # Get gradient image.
        # Gradient is positive magnitude and angle in [0 360] degrees.
        (mag, psi) = rub.gradients(imtest)
        # Map gradient angle to [0 180]
        psi[psi>180] -= 180
        outfilename = outpath + os.path.splitext(os.path.basename(f))[0] + "-mag" + outfile_ext
        if WRITE_FILES: write_image(mag, outfilename)
        outfilename = outpath + os.path.splitext(os.path.basename(f))[0] + "-psi" + outfile_ext
        if WRITE_FILES: write_image(psi, outfilename)
        #
        # My innovation.  Make gradients with mag < thresh = "no gradient", because in those
        # cases, the angle is just noise.
        psi[mag<gradthresh] = -1.0 # no gradient
        outfilename = outpath + os.path.splitext(os.path.basename(f))[0] + "-mag" + '{0:03d}'.format(int(gradthresh*100)) + outfile_ext
        if WRITE_FILES: write_image(mag>=gradthresh, outfilename)
        outfilename = outpath + os.path.splitext(os.path.basename(f))[0] + "-psi" + '{0:03d}'.format(int(gradthresh*100)) + outfile_ext
        if WRITE_FILES: write_image(psi, outfilename)
        #
        # Generate integral histogram.
        #histpsi = np.histogram(psi,numbins,(0,180),new=True) # hist of psi for checking results
        print("Histogram of gradient angles: ")
        histpsi = np.histogram(psi,numbins,(0,180)) # hist of psi for checking results
        print(histpsi[0])
        print("Total gradient pixels: " + str(sum(histpsi[0])) + " out of " + str(imtest.size))
        int_bins = rub.integral_hist(psi,histpsi[1]) # integral historgram
        #
        # Calculate entropy image.
        print("Calculating entropy...")
        (H,S) = rub.entropy(int_bins,W)
        outfilename = outpath + os.path.splitext(os.path.basename(f))[0] + "-H" + str(W)+ outfile_ext
        if WRITE_FILES: write_image(H, outfilename)
        print("Histogram of entropy: ")
        histH = np.histogram(H,8)
        print(histH[0])
        print(histH[1])
        #
        # Output rubble detections.
        print("Saving output...")
        imrbl = np.zeros(imtest.shape,dtype=np.uint8)
        imrbl[H>histH[1][5]] = 255
        outfilename = outpath + os.path.splitext(os.path.basename(f))[0] + "-rbl" + str(W)+ '.jpg'
        params = list() # opencv params for jpeg
        params.append(cv2.IMWRITE_JPEG_QUALITY)
        params.append(100) # use 100% for lossless compression
        cv2.imwrite(outfilename, imrbl,params)
        # Copy the worldfile from original image.
        wrld1 = outpath + os.path.splitext(os.path.basename(f))[0] + '.jgw'
        wrld2 = outpath + os.path.splitext(os.path.basename(f))[0] + "-rbl" + str(W)+ '.jgw'
        shutil.copyfile(wrld1,wrld2)
        print("------------------")
        print("  ")


if __name__ == "__main__":
    main(sys.argv[1:])




