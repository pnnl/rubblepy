# Welcome to rubblepy!
This code can be used to generate a damage map based on the presence of rubble.  Rubble is often detectable in images with submeter resolution, and can indicate damage to structures from high winds or earthquakes.  The process_images.py script outputs a mask indicating the pixels in the original image where rubble was detected.  The mask can be used in a geospatial software application like ArcMap to generate a damage map based on the rubble density.  The rubble detection mask will contain some false positives which are usually more isolated than true rubble, so a density map will provide a more accurate indication of affected areas than the indivdidual rubble detections will.   

usage:
   python process_images.py [options]

options:

-i *input_directory*       directory containing image files to process, default is '.'

-e *image file extension*  extension of image files, default is .jpg 

-o *output directory*      directory for output files, default is input dir with "-rubble" appended


requires:  openCV

The script processes all the image files in the input directory and writes the output to
the output directory.  The output is a binary image file for each input file, where each
pixel is either 0 if no rubble was detected at this location in the input image, or 255 if
rubble was detected.  The output files are named the same as the input files with "-rblX" 
appended, where X is an integer indicating the size of the neighborhood used (see inline
comments for further details.)  The world files from the original input images are copied
to the output directory and named to match the output files.  

A sample input file is provided from NOAA's Emergency Response Imagery 
(http://storms.ngs.noaa.gov/eri_page/index.html) from Hurricane Ike.  The image size is
7154 x 7154 pixels with 34 cm pixel resolution.  Note that the processing takes 
approximately 15 minutes on a desktop PC with a 3 GHz CPU and 16 Gb of RAM.

This code is based on the rubble detection algorithm in:

 > Talbot, L. M. and Talbot, B. G. (2013). Fast-responder: Rapid mobile-phone 
 > access to recent remote sensing imagery for first responders. In Aerospace Conference, 2013 IEEE, 
 > pages 1-10. IEEE.
