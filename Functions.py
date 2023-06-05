import os
from scipy import signal as sig
from datfiles_lib_parallel import *
from os import listdir
import pandas as pd
from sklearn.neighbors import NearestNeighbors

def replace_locations(sessionID:int, RXfile:str, TXfile:str, dir:str):
    """function for replacing reciever GPS with more accurate location

    Args:
        sessionID (int): data ID number
        RXfile (str): RX file
        TXfile (str): TX file
        dir (str): data directory to raw data
    """
    # load Rx file from csv
    rxfile = pd.read_csv(os.path.join(dir, RXfile))
    rxfile = rxfile.to_numpy()
    rx_utm = rxfile[:,[2,3]]
    # fit nearest neighbour to rx pts
    nbrs = NearestNeighbors(n_neighbors=3,algorithm='ball_tree',p=2).fit(rx_utm)

    # load Tx file from csv
    txfile = pd.read_csv(os.path.join(dir, TXfile))

    # load in data file gps pts
    all_folds = [x[0] for x in os.walk(dir)]
    dat_folds = all_folds[1:]

    for m in range(len(dat_folds)):
        # get files within data folder
        only_files = [f for f in listdir(dat_folds[m])]
        for idx in range(len(only_files)):
                node = os.path.join(dat_folds[m], '', only_files[idx])
                fIn = open(node, 'r', encoding="utf8", errors=""'ignore')
                linesFIn = fIn.readlines()
                fIn.close()

                time, data = read_data(linesFIn)
                gps = get_average_gps(linesFIn)
                
                # convert gps to UTM
                gps_UTM = utm.from_latlon(gps[0],gps[1])
                gps_UTM_pt = np.array([gps_UTM[0],gps_UTM[1]])

                # find closest neighbour to gps pt
                dists, inds = nbrs.kneighbors([gps_UTM_pt])

                # get closest gps pt from rx file
                closest = rxfile[inds[0,0]]

                # check accuracy
                # print(f'diff1= ',gps_UTM_pt[0]-closest[2],'diff2= ',gps_UTM_pt[1]-closest[3])

                # convert closest pt back to lat lon # TODO check error on this, maybe stick to UTM
                closest_latlon = utm.to_latlon(closest[2],closest[3],gps_UTM[2],gps_UTM[3])

                force_file(node,closest_latlon[0],closest_latlon[1],closest[4],False,1)



def force_file(path:str, latitude:float, longitude:float, elevation:float, flag_new:bool, sid: int) -> None:
    """forces node files to a specified easting, northing, elevation

    Args:
        path (str): raw directory ID
        latitude (float): known latitude
        longitude (float): known longitude
        elevation (float): elevation
        flag_new (bool): _description_
        sid (int): session bucket ID
    """