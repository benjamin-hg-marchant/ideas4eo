from matplotlib.pyplot import figure

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
import numpy as np
import seaborn as sns; sns.set()

##########################################################################################

def plot_data(data):
    
    #data = np.copy( data_obj.data )
    
    #data[ data != -99999 ] = data[ data != -99999 ] * data_obj.sds_attributes['scale_factor']
    #data = data * data_obj.sds_attributes['scale_factor']
    
    figure(num=None, figsize=(12, 10), dpi=80, facecolor='w', edgecolor='k')
    
    vmin = np.min(data[ data != -99 ])
    vmax = np.max(data[ data != -99 ])
    
    print(vmin,vmax)
    
    plt.imshow(np.fliplr(data), origin='lower', cmap='jet', vmin=vmin, vmax=vmax)

    plt.colorbar()

    plt.title('Solar Azimuth', fontsize=16)

    l = [int(i) for i in np.linspace(0,data.shape[1],6)]
    plt.xticks(l, [i for i in reversed(l)], rotation=0, fontsize=11 )

    l = [int(i) for i in np.linspace(0,data.shape[0],9)]
    plt.yticks(l, l, rotation=0, fontsize=11 )

    plt.xticks(fontsize=11)
    plt.yticks(fontsize=11)

    plt.show()

##########################################################################################

def plot_MODIS_L2_Cloud_Mask_1km(cloud_mask_flag):
    
    figure(num=None, figsize=(12, 10), dpi=80, facecolor='w', edgecolor='k')
    
    #cmap =  [(1.0,1.0,1.0)] + [(1.0, 0.0, 0.0)] + [(65.0/255,105.0/255,225.0/255)] + [(0.0,0.0,0.0)]
    #cmap = sns.mpl_palette("Set1", 4)
    
    cmap = sns.color_palette("RdBu", n_colors=4)
    cmap = mpl.colors.ListedColormap(cmap)
    
    bounds = [-0.5, 0.5, 1.5, 2.5, 3.5]
    
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    
    img = plt.imshow(np.fliplr(cloud_mask_flag), cmap=cmap, norm=norm,interpolation='none', origin='lower')
    
    cbar_bounds = [-0.5, 0.5, 1.5, 2.5, 3.5]
    
    cbar_ticks = [ 0, 1, 2, 3]  
    
    cbar_labels = ['Confident Cloudy', 'Probably Cloudy','Probably Clear ','Confident Clear']  
    
    cbar = plt.colorbar(img, cmap=cmap, norm=norm, boundaries=cbar_bounds, ticks=cbar_ticks)
    
    cbar.ax.set_yticklabels(cbar_labels, fontsize=11)
    
    plt.title('MODIS MYD06 C6 Cloud Mask 1km', fontsize=11)
    
    l = [int(i) for i in np.linspace(0,cloud_mask_flag.shape[1],6)]
    plt.xticks(l, [i for i in reversed(l)], rotation=0, fontsize=11 )
    
    l = [int(i) for i in np.linspace(0,cloud_mask_flag.shape[0],9)]
    plt.yticks(l, l, rotation=0, fontsize=11 )
    
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=11)
    
    plt.show()