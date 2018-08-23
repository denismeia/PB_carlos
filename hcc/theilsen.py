import sys
sys.path.append("/home/wardlow/denis/mypy")
import xuleta as xu
from scipy.stats import *
#import pylab as plt
from scipy import interpolate
from glob import glob
import numpy as np

#Folder
folder = "/home/wardlow/denis/work/BRASIL/MODIS/MOD16A2H/h13v11/ET"

#list
lista = [x for x in sorted(glob(folder+"/*.tif")) if x[-9:-7] in ['11','12','01','02']]

#create ndarray
arrays = []
for i in lista:
    a,m = xu.TifToArray(i)
    arrays.append(a)
arrays3 = np.asarray(arrays)
arrays3 = np.reshape(arrays3,(arrays3.shape[0],arrays3.shape[1]*arrays3.shape[2]))

####
#Theil-Sen slopes
####
x = np.arange(len(lista))

# creating matrices for outputs
medslope = np.zeros(arrays3.shape[1])
medintercept = np.zeros(arrays3.shape[1])
lo_slope = np.zeros(arrays3.shape[1])
up_slope = np.zeros(arrays3.shape[1])

for i in range(arrays3.shape[1]): #range(1,2000000,1)
    ts_results = stats.theilslopes(arrays3[:,i],x)
    medslope[i] = ts_results[0]
    medintercept[i] = ts_results[1]
    lo_slope[i] = ts_results[2]
    up_slope[i] = ts_results[3]
medslope = medslope.reshape(a.shape[0],a.shape[1])
medintercept = medintercept.reshape(a.shape[0],a.shape[1])
lo_slope = lo_slope.reshape(a.shape[0],a.shape[1])
up_slope = up_slope.reshape(a.shape[0],a.shape[1])

#saving outputs as tif
xu.ArrayToTif(Array=medslope, Filename='medslope.tif',Folder='../outputs/ET/',Metadata=m,Type=3)
xu.ArrayToTif(Array=medintercept, Filename='medintercept.tif',Folder='../outputs/ET/',Metadata=m,Type=3)
xu.ArrayToTif(Array=lo_slope, Filename='lo_slope.tif',Folder='../outputs/ET/',Metadata=m,Type=3)
xu.ArrayToTif(Array=up_slope`, Filename='up_slope.tif',Folder='../outputs/ET/',Metadata=m,Type=3)


# savind outputs as numpy files
np.save('../outputs/ET/ET_medslope',medslope)
np.save('../outputs/ET/ET_medintercept',medintercept)
np.save('../outputs/ET/ET_lo_slope',lo_slope)
np.save('../outputs/ET/ET_up_slope',up_slope)

