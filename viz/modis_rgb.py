from matplotlib.pyplot import figure
from pyhdf.SD import SD, SDC 
from pyhdf.HDF import *
from pyhdf.VS import *

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
import numpy as np
import seaborn as sns; sns.set()

##########################################################################################

def plot_modis_rgb_image(myd021km_granule):

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
    
    file = SD(myd021km_granule, SDC.READ)

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



    norme = 0.4 # factor to increase the brightness ]0,1]

    rgb = np.zeros((along_track, cross_trak,3))

    rgb = z / norme

    rgb[ rgb > 1 ] = 1.0
    rgb[ rgb < 0 ] = 0.0

    fig = figure(num=None, figsize=(12, 10), dpi=80, facecolor=fig_style_dict['facecolor'], edgecolor='k')

    ax = fig.add_subplot(111)
        
    img = plt.imshow(np.fliplr(rgb)*2.0, interpolation='nearest', origin='lower')

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

    return rgb