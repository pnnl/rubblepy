#!/bin/usr/env python
# -*- coding: utf-8 -*-
"""
 *  Remote Sensing for Damage Assessment
 *
 *  rubble_detection_talbot.py
 *
 *  Created by Shari Matzner on 11/14/2015.
 *  Copyright © 2016, Battelle Memorial Institute.  All rights reserved.
 *
"""

# This code is based on the rubble detection algorithm in:
# Talbot, L. M. and Talbot, B. G. (2013). Fast-responder: Rapid mobile-phone 
#   access to recent remote sensing imagery for first responders. In Aerospace Conference, 2013 IEEE, 
#   pages 1-10. IEEE.

import numpy as np
import cv2 # openCV

def gradients(imgray, filtsize=3) :
    # Compute the derivates in the x and y directions at each pixel.
    # http://docs.opencv.org/doc/tutorials/imgproc/imgtrans/sobel_derivatives/sobel_derivatives.html
    dx = cv2.Sobel(imgray, cv2.CV_32F, 1, 0, ksize=filtsize)  
    dy = cv2.Sobel(imgray, cv2.CV_32F, 0, 1, ksize=filtsize) 
    #
    # Compute the gradient angle and magnitude at each pixel.
    (mag, psi) = cv2.cartToPolar(dx,dy,angleInDegrees=1)
    #
    return (mag,psi)

def integral_hist(im,bins) :
    numbins = len(bins) -1
    integral_bins = [None]*numbins # integral images for each orientation bin
    for k in range(0, numbins) :
        # threshold function: imbin = 0 if im > bins[k+1], else imbin = im 
        (rval,imbin) = cv2.threshold(im, bins[k+1], 1, cv2.THRESH_TOZERO_INV) 
        # threshold function: imbin1 = 1 if im > bins[k], else imbin = 0
        (rval,imbin1) = cv2.threshold(imbin, bins[k], 1, cv2.THRESH_BINARY) 
        integral_bins[k] = cv2.integral(imbin1) 
    #
    return (integral_bins)


def entropy(intbins, W) :
    # intbins is a tuple of integral images, with each image corresponding to one histogram bin
    # W is the window size (window is square)
    halfW = int(np.floor(0.5*W)) # half a window
    (ymax,xmax) = intbins[0].shape  # x is horizontal dim (columns), y is vertical dim (rows)
    H = np.zeros([ymax-1,xmax-1]) # entropy image
    S = np.zeros([ymax-1,xmax-1]) # count image
    kmax = len(intbins)   
    hist = np.zeros(kmax)
    Is = np.dstack(intbins)
    # TODO:  Decide how to handle borders
    for x in range(halfW,xmax-halfW) :
        for y in range(halfW,ymax-halfW) :
            hist = Is[y-halfW,x-halfW,:] + Is[y+halfW,x+halfW,:] - Is[y-halfW,x+halfW,:] - Is[y+halfW,x-halfW,:]
            s = sum(hist)
            if s > 0 :
                hist[hist<=0]=np.nan # Adam's suggestion; should never have <0
                p = hist/s
                H[y-1,x-1] = -sum(p * np.log2(p))
            S[y-1,x-1] = s
    H[np.isnan(H)] = 0 # define 0 log 0 as 0
    #
    return (H,S)



