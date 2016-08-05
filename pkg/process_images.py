#!/usr/bin/python

"""
 *  Remote Sensing for Damage Assessment
 *
 *  process_images.py
 *
 *  Created by Shari Matzner on 11/14/2015.
 *  Copyright © 2016, Battelle Memorial Institute.  All rights reserved.
 *
"""


import glob
import time
import shutil
import os
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

# Process all the images in dirpath using func.
#-------------------------------------------------
# Entire Ike data set.
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep14C30' # 85 ?
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep14C31' # 73 2015-07-07_133355_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep14C32' # 47 2015-07-07_210438_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep14C33' # 48 2015-08-03_154222_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep14C34' # 10 2015-08-05_131136_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep14C35' # 10 2015-08-06_094130_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep14C36' # 8 2015-08-06_123901_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep14C37' # 3 2015-08-10_104350_out 
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep14C1' # 13 2015-08-10_124715_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep14C2' # 43 2015-08-10_165708_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep16C2' # 104 2015-08-12_140021_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep16C3' # 364
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep16C30' # 85 2015-08-20_120043_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep16C31' # 73 2015-08-21_132242_out 
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep16C32' # 47 2015-08-24_094147_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep16C33' # 48 2015-08-25_140607_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep16C34' # 26 2015-08-27_080024_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep16C35' # 18 2015-08-27_152604_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep16C36' # 18 2015-08-28_082644_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep16C37' # 16 2015-08-28_143335_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep16C38' # 16 2015-08-31_071956_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep16C39' # 17 2015-08-31_123445_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep16C4' # 269 2015-09-02_153423_out
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/FullRes/sep16C5' # 61 2015-08-14_101103_out
dirpath = 'tempdir/'
imfile_ext = '.JPG'
# Ike test
#dirpath = 'Data/HurricaneIke/NOAA_Rapid-Response/Test/' 
#imfile_ext = '.JPG'
# Sandy test, images converted to UTM projection
#dirpath = 'Data/HurricaneSandy/NOAA_Rapid-Response/Test2/'
#imfile_ext = '.jpg'

# The image files are .JPG (Note the extension in all upper case.)
# Each image file has three companion files, with the same filename
# and the following extensions:
# .jgw -- world file, see http://en.wikipedia.org/wiki/World_file
# .met -- text file of metadata in Federal Geographic Data Commitee (FGDC) standard format
# .xml -- text file of metadata in xml formats
#-------------------------------------------------
# Get list of image files in dir and subdirs.
print("Getting list of image files " + dirpath + "*" + imfile_ext)
imfilelist = glob.glob(dirpath + '*' + imfile_ext)
if not len(imfilelist) > 0:
    print("No image files found.") 

# Create output dir.
outpath = time.strftime("%Y-%m-%d_%H%M%S") + '_out/'
print("Creating output directory " + outpath)
os.makedirs(outpath)
copy_worldfiles(dirpath,outpath)
outfile_ext = '.png'
WRITE_FILES = False;

numbins = 9 # number of oriented gradient histogram bins
W = 6      # window size for entropy calculation
gradthresh = 0.5 # magnitude of gradient must be greater than this

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




