# modis_mod09a1_hdf_vegindex_pt.pro
#
# It reads a tile of MOD09s1 file (eos-hdf fomat) and calculate vegetation indicies.
# MODIS has 7 spectral bands:
# band 1 -- red		(620 - 670nm)
# band 2 -- nir1	(841 - 875 nm)
# band 3 -- blue	(459 - 479 nm)
# band 4 -- green	(620 - 670 nm)
# band 5 -- nir2	(1230 - 1250 nm)
# band 6 -- swir1	(1628 - 1652 nm)
# band 7 -- swir2	(2105 - 2155 nm)
# ndvi = (nir1 - red) / (red + nir1)
# ndwi = (nir1 - nir2) / (nir1 + nir2)		from Gao (1996)
# lswi = (nir1 - swir1) / (nir1 + swir1) 	from Xiao et al., 2002
# ndsi = (green - swir1) / (green + swir1)	from Hall et al., 1998
# evi = G * (NIR1 - RED)/(NIR1 + C1*RED - C2*BLUE + L), 
# where L is the canopy background correction and sonw correction that addresses
# differential NIR and RED radiant transfer (transmittance) through a canopy,
# and C1 and C2 are the coefficient of the aerosol term, which uses BLUE band
# to correct for aerosol effects in the red band.
# Currently use G = 2.5, C1 = 6, C2 = 7.5, L = 1.0
# see Justice et al. 1998. Land remote sensing for global change research, IEEE
# Trans. Geosci. Remote Sensing, 36(4):1228-1249.
# H.Q. Liu and Heute, A.R. 1995. A feedback based modification of the NDVI to
# minimize canopy background and atmospheric noise. IEEE Trans.Geosci. Remote
# Sensing vol.33 pp457-465, March 1995
# the equation is 
#
# Scale method : MODIS product, MOD13A2 for ndvi and evi
# data type type -- 16-bit integer, 
# fill value = -20000, 
# valid range for NDVI,  min_ndvi= -2000, max_ndvi = 10000
# valid range for EVI,   min_evi = -2000, max_evi  = 10000
# valid range for NDWI,  min_ndwi = -10000, max_ndwi = 10000
# valid range for NDSI,  min_ndsi = -10000, max_ndsi = 10000
# scale factor = 10000


# output file is HDF format or envi format

# Delong Zhao
# zhaodelong@gmail.com
# July, 2011

# It calculates one vegetation index at a time. It helps to save disk space, while it takes
# slight longer time to process five vegetation indices (evi, ndvi, lswi, ndwi, ndsi)

# cybercommons: 129.15.41.81
#--------------------------------------------------------------------

import os, sys, time, numpy, fnmatch
from osgeo import gdal
from osgeo.gdalconst import *
import multiprocessing


# start timing


# information on MOD09A1 file
ncol = 2400
nrow = 2400
nband = 7		# band 1 to 7, quality flag 8-13 skipped
scalef = 10000		# scalefactor 
ocean_fillval = -3.0	# oceans
fillval = -2.0
# valid range -0.2 to 1.0
min_ndvi= -0.2
max_ndvi = 1.0
min_evi= -0.2
max_evi = 1.0
min_lswi= -1.0
max_lswi = 1.0




def return_band(mod09a1_file_name, band_number):
    #open mod09a1
    fn_mod09a1 = mod09a1_file_name

    if band_number < 14 and band_number > 0:
        #print 'Get band: ' + str(band_number)
        fn_mod09a1 = 'HDF4_EOS:EOS_GRID:'+fn_mod09a1+':MOD_Grid_500m_Surface_Reflectance:sur_refl_b0'+str(band_number)
        #print fn_mod09a1
        
        ds_mod09a1 = gdal.Open(fn_mod09a1,GA_ReadOnly)
        if ds_mod09a1 is None:
            print "Could not open " + fn_mod09a1
            sys.exit(1)

        geoTransform = ds_mod09a1.GetGeoTransform()
        proj = ds_mod09a1.GetProjection()
        
        rasterband = ds_mod09a1.GetRasterBand(1)
        #type(rasterband)
        band = rasterband.ReadAsArray(0,0,ncol,nrow)
        band = band.astype(numpy.float)

        return band,geoTransform,proj

        ds_mod09a1 = None
        band = None

def output_file(output_name,output_array,geoTransform,proj):
    format = "GTiff"
    driver = gdal.GetDriverByName( format )
    outDataset = driver.Create(output_name,2400,2400,1,GDT_Float32)
    outBand = outDataset.GetRasterBand(1)
    outBand.WriteArray(output_array,0,0)
    outBand.FlushCache()
    outBand.SetNoDataValue(fillval)
    outDataset.SetGeoTransform(geoTransform )
    outDataset.SetProjection(proj)

def normalize(band1,band2):
    var1 = numpy.subtract(band1,band2)
    var2 = numpy.add(band1,band2)

    numpy.seterr(all='ignore')
    ndvi = numpy.divide(var1,var2)

    return ndvi

def process_ndvi(mod09a1_file_name,ndvi_output_name):
    #open mod09a1
    fn_mod09a1 = mod09a1_file_name
    
    red,geoTransform,proj  = return_band(fn_mod09a1,1) # band 1 -- red		(620 - 670nm)
    nir1 = return_band(fn_mod09a1,2)[0] # band 2 -- nir1	(841 - 875 nm)    

    ocean_mask = numpy.where(red == -28672, 1, 0)
    red_mask = numpy.where(red <= 1 , 1, 0)
    nir1_mask = numpy.where(nir1 <= 1, 1, 0)
    
    
    ndvi = normalize(nir1,red)

    #ndvi = (nir1 - red) / (red + nir1 +0.00000000001)
    min_ndvi_mask = numpy.where(ndvi < min_ndvi, 1, 0)
    max_ndvi_mask = numpy.where(ndvi > max_ndvi, 1, 0)

    numpy.putmask(ndvi, min_ndvi_mask, min_ndvi)

    numpy.putmask(ndvi, max_ndvi_mask, max_ndvi)

    numpy.putmask(ndvi, red_mask, fillval)
    numpy.putmask(ndvi, nir1_mask, fillval)
    numpy.putmask(ndvi, ocean_mask, ocean_fillval)
    
    #output file
    
    output_file(ndvi_output_name,ndvi,geoTransform,proj)
        
    red = None
    nir1 = None
    ndvi = None
    min_ndvi_mask = None
    max_ndvi_mask = None
    ocean_mask = None

# band 1 -- red		(620 - 670nm)
# band 2 -- nir1	(841 - 875 nm)
# band 3 -- blue	(459 - 479 nm)
# band 4 -- green	(620 - 670 nm)
# band 5 -- nir2	(1230 - 1250 nm)
# band 6 -- swir1	(1628 - 1652 nm)
# band 7 -- swir2	(2105 - 2155 nm)
# ndvi = (nir1 - red) / (red + nir1)
# ndwi = (nir1 - nir2) / (nir1 + nir2)		from Gao (1996)
# lswi = (nir1 - swir1) / (nir1 + swir1) 	from Xiao et al., 2002
# ndsi = (green - swir1) / (green + swir1)	from Hall et al., 1998


def findfiles(root_dir):
    toprocess = []  # list to store paths for processing in
    for root,dir,files in os.walk(root_dir):
        for name in files:
            if fnmatch.fnmatch(name,'*.hdf'):
               toprocess.append( os.path.join(root, name) )
               print os.path.join(root, name)
    return toprocess

def creatoutputfolder(path,root_dir,output_dir,product):
    mod09a1_dir = os.path.dirname(path)
    name = os.path.basename(path)
    mod09a1 = os.path.join(mod09a1_dir,name)
    #print 'Processing: ', mod09a1

    relative_path = os.path.relpath(mod09a1_dir,root_dir)
    #print relative_path

    product_dir = os.path.join(output_dir,product)
    product_dir = os.path.join(product_dir,relative_path)
    if not os.path.exists(product_dir):
        os.makedirs(product_dir)
        print '    Creating dir: ',product_dir

def product_output_name(output_dir,mod09a1_name,relative_path,product):
    product_dir = os.path.join(output_dir,product)
    product_dir = os.path.join(product_dir,relative_path)
    #print product_dir
    product_output_name = mod09a1_name[:-4]+'.'+product+'.tif'
    #print product_output_name
    #print product_dir
    product_path_file = os.path.join(product_dir,product_output_name)
    #print '    Output file: ',product_path_file
    return product_path_file

def doprocess(path):
    t1 = time.time()
    mod09a1_dir = os.path.dirname(path)
    name = os.path.basename(path)
    mod09a1 = os.path.join(mod09a1_dir,name)
    #print 'Processing: ', mod09a1

    relative_path = os.path.relpath(mod09a1_dir,root_dir)
    #print relative_path

    
    ndvi = product_output_name(output_dir,name,relative_path,'ndvi')
    #print '    Processing: ',ndvi
    process_ndvi(mod09a1,ndvi)
    #print '\n'

    #evi = product_output_name(output_dir,name,relative_path,'evi')
    #print '    Processing: ',evi
    #process_evi(mod09a1,evi)
    
    #lswi = product_output_name(output_dir,name,relative_path,'lswi')
    #print '    Processing: ',lswi                
    #process_lswi(mod09a1,lswi)
    
    print 'Processing done: ',mod09a1
    t2 = time.time()
    print 'Onee process took :' +str(t2 - t1)+ ' seconds'
    #print '\n'

def run(root_dir_input,out_put_dir):
    #input mod09a1 root directory
    
    global root_dir
    global output_dir

    root_dir = root_dir_input
    output_dir = out_put_dir

    filelist = findfiles(root_dir)
    print root_dir
    print output_dir

    for f in filelist:
        creatoutputfolder(f,root_dir,output_dir,'ndvi')
        #creatoutputfolder(f,root_dir,output_dir,'evi')
        #creatoutputfolder(f,root_dir,output_dir,'lswi')
    
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    pool.map(doprocess,findfiles(root_dir))
    print 'Using ' +str(multiprocessing.cpu_count())+' cores.'


  



