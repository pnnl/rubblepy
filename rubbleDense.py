# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        rubbleDense.py
# Purpose:     The script prepares rubble detection results for GIS usage and
#              viewing. Inputs images in a dir, isolates clumps of rubble, finds
#              the centerpoint of the clump and calculates rubble density based 
#	       on points, in units of clumps per hectare. Output is images with
#              pixels size set by "Cell size" variable where pixel value reprents
#              the density of rubble in detections/hectare.
#              NOTE: Assumes the raw images input to rubble script are in UTM 
#
# Author:      Jerry Tagestad & Sadie Montgomery
#              
# Dependencies: ArcGIS Spatial Analyst license
# Created:     03-10-2017, modified 08-19-2016
# Copyright:   © 2017, Battelle Memorial Institute.  All rights reserved.
#
# Usage rubbleDense.py [Input Workspace] [Output Workspace] [UTM Zone of orig]
# -------------------------------------------------------------------------------

# Import arcpy module
import arcpy
import os
import sys

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

# Local variables:
Workspace = sys.argv[1]
Outspace = sys.argv[2]
ZoneNum = sys.argv[3] 
arcpy.env.workspace = Workspace
Const0 = "0" # Constant value to use when conditional statement "False"
Const1 = "1" # Constant value to use when consditional statement "True"
CellSize = 10 # Output raster pixel size

# Find images that match the output naming of the rubble detection script
Rasters = arcpy.ListRasters("*rbl6.jpg")

# Process: Iterate Rasters
ct=0

for ras in Rasters:
    ct+=1
    arcpy.env.extent = "{0}/{1}".format(Workspace,ras)
    f = arcpy.Raster(ras)
    f1 = ras[0:20]
    # Process: Define Projection
    arcpy.DefineProjection_management(f, "PROJCS['NAD_1983_UTM_Zone_"+ZoneNum+"N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-93.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]")
    # Process: Con
    arcpy.gp.Con_sa(f, Const1, Outspace+f1+"con.tif", Const0, "Value > 250")
    # Process: Boundary Clean
    arcpy.gp.BoundaryClean_sa(Outspace+f1+"con.tif", Outspace+f1+"cln.tif", "NO_SORT", "TWO_WAY")
    # Process: Raster to Polygon
    arcpy.RasterToPolygon_conversion(Outspace+f1+"cln.tif", Outspace+f1+"ply.shp", "SIMPLIFY", "Value")
    # Process: Feature To Point
    arcpy.FeatureToPoint_management(Outspace+f1+"ply.shp", Outspace+f1+"pnt.shp", "INSIDE")
    # Process: Kernel Density
    arcpy.gp.KernelDensity_sa(Outspace+f1+"pnt.shp", "NONE", Outspace+f1+"kd.tif", CellSize, "100", "HECTARES")

    sys.stdout.write('\r')
    sys.stdout.write('%.2f%% complete' % (ct / 963 * 100,))
    sys.stdout.flush()







