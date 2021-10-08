from ..grt import misc

from scipy.interpolate import griddata
from matplotlib.pyplot import figure
from pyhdf.SD import SD, SDC 
from pyhdf.HDF import *
from pyhdf.VS import *

from scipy.interpolate.interpnd import _ndim_coords_from_arrays
from scipy.spatial import cKDTree

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
import numpy as np
import seaborn as sns; sns.set()

from cartopy import config

import cartopy.crs as ccrs

##########################################################################################

def plot_modis_rgb_image(file):

    fig_style_dict = {}

    fig_style_dict['fig_type'] = 'analysis' #'analysis'

    fig_style_dict['facecolor'] = '#E8E8E8'
    fig_style_dict['label_font_size'] = 18
    fig_style_dict['title_font_size'] = 22
    fig_style_dict['heatmap_annot_font_size'] = 22

    fig_style_dict['facecolor'] = 'white'
    fig_style_dict['label_font_size'] = 12
    fig_style_dict['title_font_size'] = 14
    fig_style_dict['heatmap_annot_font_size'] = 14
    
    #file = SD(myd021km_granule, SDC.READ)

    selected_sds = file.select('EV_250_Aggr1km_RefSB')

    selected_sds_attributes = selected_sds.attributes()

    for key, value in selected_sds_attributes.items():
        if key == 'reflectance_scales':
            reflectance_scales_250_Aggr1km_RefSB = np.asarray(value)
        if key == 'reflectance_offsets':
            reflectance_offsets_250_Aggr1km_RefSB = np.asarray(value)

    sds_data_250_Aggr1km_RefSB = selected_sds.get()

    selected_sds = file.select('EV_500_Aggr1km_RefSB')

    selected_sds_attributes = selected_sds.attributes()

    for key, value in selected_sds_attributes.items():
        if key == 'reflectance_scales':
            reflectance_scales_500_Aggr1km_RefSB = np.asarray(value)
        if key == 'reflectance_offsets':
            reflectance_offsets_500_Aggr1km_RefSB = np.asarray(value)

    sds_data_500_Aggr1km_RefSB = selected_sds.get()

    print( reflectance_scales_500_Aggr1km_RefSB.shape)


    data_shape = sds_data_250_Aggr1km_RefSB.shape

    along_track = data_shape[1]
    cross_trak = data_shape[2]

    z = np.zeros((along_track, cross_trak,3))

    z[:,:,0] = ( sds_data_250_Aggr1km_RefSB[0,:,:] - reflectance_offsets_250_Aggr1km_RefSB[0] ) * reflectance_scales_250_Aggr1km_RefSB[0] 
    z[:,:,1] = ( sds_data_500_Aggr1km_RefSB[1,:,:] - reflectance_offsets_500_Aggr1km_RefSB[1] ) * reflectance_scales_500_Aggr1km_RefSB[1] 
    z[:,:,2] = ( sds_data_500_Aggr1km_RefSB[0,:,:] - reflectance_offsets_500_Aggr1km_RefSB[0] ) * reflectance_scales_500_Aggr1km_RefSB[0] 




    x = np.array([0,  30,  60, 120, 190, 255], dtype=np.uint8)
    y = np.array([0, 110, 160, 210, 240, 255], dtype=np.uint8)

    def scale_image(image, x, y):
        scaled = np.zeros((along_track, cross_trak), dtype=np.uint8)
        for i in range(len(x)-1):
            x1 = x[i]
            x2 = x[i+1]
            y1 = y[i]
            y2 = y[i+1]
            m = (y2 - y1) / float(x2 - x1)
            b = y2 - (m *x2)
            mask = ((image >= x1) & (image < x2))
            scaled = scaled + mask * np.asarray(m * image + b, dtype=np.uint8)

        mask = image >= x2
        scaled = scaled + (mask * 255)

        return scaled

    z_color_enh = np.zeros((along_track, cross_trak,3), dtype=np.uint8)

    z_color_enh[:,:,0] = scale_image(misc.bytescale(z[:,:,0]), x, y)
    z_color_enh[:,:,1] = scale_image(misc.bytescale(z[:,:,1]), x, y)
    z_color_enh[:,:,2] = scale_image(misc.bytescale(z[:,:,2]), x, y)



    fig = figure(num=None, figsize=(12, 10), dpi=80, facecolor=fig_style_dict['facecolor'], edgecolor='k')

    ax = fig.add_subplot(111)
        
    img = plt.imshow(np.fliplr(z_color_enh), interpolation='nearest', origin='lower')

    l = [int(i) for i in np.linspace(0,cross_trak,6)]
    plt.xticks(l, [i for i in reversed(l)], rotation=0, fontsize=11 )

    l = [int(i) for i in np.linspace(0,along_track,9)]
    plt.yticks(l, l, rotation=0, fontsize=11 )

    plt.xticks(fontsize=11)
    plt.yticks(fontsize=11)

    plt.title('MODIS RGB Image', fontsize=14)
    
    plt.grid(None) 
    
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    
    plt.savefig("rgb.png", bbox_inches='tight', facecolor=fig.get_facecolor())
    
    plt.show()
        
    plt.close()

    return z_color_enh
    
##########################################################################################

def plot_modis_rgb_image_with_orthographic_projection(myd021km, myd03_file):
    
    z_color_enh = plot_modis_rgb_image(myd021km)
    
    myd03_Latitude = myd03_file.select('Latitude')
    myd03_Longitude = myd03_file.select('Longitude')

    myd03_Latitude_data = myd03_Latitude.get()
    myd03_Longitude_data = myd03_Longitude.get()

    myd03_Latitude_data = np.fliplr(myd03_Latitude_data)
    myd03_Longitude_data = np.fliplr(myd03_Longitude_data)
    
    myd03_Latitude_shape = myd03_Latitude_data.shape
    
    z = z_color_enh / 256.0

    z = np.fliplr(z)
    
    along_track = myd03_Latitude_shape[0]
    cross_trak = myd03_Latitude_shape[1]
    
    proj = ccrs.PlateCarree()
    
    lat_long_grid = proj.transform_points(                 
                        x = myd03_Longitude_data,
                        y = myd03_Latitude_data,
                        src_crs = proj)
    
    x_igrid = lat_long_grid[:,:,0] ## long
    y_igrid = lat_long_grid[:,:,1] ## lat
    
    xul = np.min(myd03_Longitude_data)
    xlr = np.max(myd03_Longitude_data)

    yul = np.min(myd03_Latitude)
    ylr = np.max(myd03_Latitude)

    z_igrid_01 = np.zeros((along_track, cross_trak))
    z_igrid_02 = np.zeros((along_track, cross_trak))
    z_igrid_03 = np.zeros((along_track, cross_trak))

    z_igrid_01[:,:] = z[:,:,0]
    z_igrid_02[:,:] = z[:,:,1]
    z_igrid_03[:,:] = z[:,:,2]

    x1_igrid = x_igrid.ravel()
    y1_igrid = y_igrid.ravel()

    z_igrid_01 = z_igrid_01.ravel()
    z_igrid_02 = z_igrid_02.ravel()
    z_igrid_03 = z_igrid_03.ravel()

    xy1_igrid = np.vstack((x1_igrid, y1_igrid)).T
    xi, yi = np.mgrid[xul:xlr:1000j, yul:ylr:1000j]

    z_01 = griddata(xy1_igrid, z_igrid_01, (xi, yi), method='nearest')
    z_02 = griddata(xy1_igrid, z_igrid_02, (xi, yi), method='nearest')
    z_03 = griddata(xy1_igrid, z_igrid_03, (xi, yi), method='nearest')

    THRESHOLD = 0.2

    tree = cKDTree(xy1_igrid)
    arr_x = _ndim_coords_from_arrays((xi, yi))
    dists, indexes = tree.query(arr_x)

    z_01[dists > THRESHOLD] = np.nan
    z_02[dists > THRESHOLD] = np.nan
    z_03[dists > THRESHOLD] = np.nan

    rgb_projected = np.zeros((1000, 1000,3))

    rgb_projected[:,:,0] = z_01[:,:]
    rgb_projected[:,:,1] = z_02[:,:]
    rgb_projected[:,:,2] = z_03[:,:]

    whereAreNaNs = np.isnan(rgb_projected);
    rgb_projected[whereAreNaNs] = 0.;

    min_long = np.min(myd03_Longitude_data)
    max_long = np.max(myd03_Longitude_data)

    min_lat = np.min(myd03_Latitude)
    max_lat = np.max(myd03_Latitude)

    plt.figure(figsize=(12,12))

    proj = ccrs.PlateCarree()

    offset = 0.0

    ease_extent = [min_long-offset, 
                   max_long+offset, 
                   min_lat-offset, 
                   max_lat+offset]

    ax = plt.axes(projection=proj)

    ax.set_extent(ease_extent, crs=proj) 


    swe_extent = [xul, xlr, yul, ylr]

    ax.imshow(np.rot90(np.fliplr(rgb_projected)), extent=swe_extent, transform=proj, origin='lower', aspect=1.7)


    ax.gridlines(color='gray', linestyle='--')

    ax.coastlines()

    plt.tight_layout()

    return rgb_projected