import calcndvi as veg
#import modis_mod09a1_hdf_cloud_masks_desktop as cloud
#import modis_mod09a1_hdf_ocean_masks_desktop as ocean
#import modis_mod09a1_hdf_snow_masks_desktop as snow
#import produce_flood_desktop_version_ocean_snow as flood
#import produce_drought_desktop_version as drought
#import produce_evergreen_desktop_version_ocean_snow as evergreen
import time

mod09a1_path = "/media/denis/seagate/PB/MODIS/myd09a1/1309"
geotiff_path = "/media/denis/seagate/PB/MODIS/myd09a1/t1309"
startTime = time.time()


vegstartTime = time.time()
veg.run(mod09a1_path,geotiff_path)
vegendtime = time.time()

mod09a1_path = "/media/denis/seagate/PB/MODIS/myd09a1/1310"
geotiff_path = "/media/denis/seagate/PB/MODIS/myd09a1/t1310"
startTime = time.time()


vegstartTime = time.time()
veg.run(mod09a1_path,geotiff_path)
vegendtime = time.time()


mod09a1_path = "/media/denis/seagate/PB/MODIS/myd09a1/1409"
geotiff_path = "/media/denis/seagate/PB/MODIS/myd09a1/t1409"
startTime = time.time()


vegstartTime = time.time()
veg.run(mod09a1_path,geotiff_path)
vegendtime = time.time()

mod09a1_path = "/media/denis/seagate/PB/MODIS/myd09a1/1410"
geotiff_path = "/media/denis/seagate/PB/MODIS/myd09a1/t1410"
startTime = time.time()


vegstartTime = time.time()
veg.run(mod09a1_path,geotiff_path)
vegendtime = time.time()