import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
import numpy as np
import seaborn as sns; sns.set()

def create_2d_filters(theta, show_filter):
 
    sun_azimuth_direction = (0,1)
    
    theta_rad = np.radians(theta)
    c, s = np.cos(theta_rad), np.sin(theta_rad)
    R = np.array(((c, -s), (s, c)))
    
    sun_azimuth_direction = np.dot(R,sun_azimuth_direction)
    #print(sun_azimuth_direction)

    x = np.linspace(-2, 2, 5)
    y = np.linspace(-2, 2, 5)

    xx, yy = np.meshgrid(x, y, sparse=False)
    
    F = xx * sun_azimuth_direction[0] + yy * sun_azimuth_direction[1]
    
    F[ F > 0.01 ] = 1.0
    F[ F <= 0.01 ] = -1.0
    
    #plt.imshow(F,cmap='gist_gray', origin='lower')
    
    if show_filter:
    
        plt.imshow(F,cmap='gist_gray')
    
        plt.grid()
        plt.title('2D Filter')
        plt.colorbar()
        plt.savefig("filter_{}.png".format(theta), bbox_inches='tight', dpi=100)
        plt.show()
    
    return F

