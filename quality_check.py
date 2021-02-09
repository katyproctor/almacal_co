### Check data quality of individual UIDs
### Script subtracts continuum for relevant spw
### images each individually
### plots uv-coverage & outputs rms/beam properties

import os
import re
import json
import numpy as np
import matplotlib.pyplot as plt 
import analysisUtils as au
import csv

def read_json(file):
    with open(file) as f:
        data = json.load(f)
    return data

def image(data_path, uid, spw_list_str,imgname):
    '''Clean the continuum subtracted vis for all uids'''
    vis = data_path+uid 
    
    tclean(vis = vis,
           spw = spw_list_str,
           weighting = 'natural',
       imagename = data_path+'katy_imaging/'+imgname,
       specmode = 'cube')    
    
def plot_uv(data_path,uid, spw):
    '''Plot uv-coverage for a given uid'''
    plotms(vis = data_path+uid, spw = spw,
           xaxis='u', yaxis='v',
           averagedata=True, avgchannel='',
          plotfile = '/home/kproctor/uv_plots/' + uid + spw + '.png', 
            expformat = 'png', exprange = 'all', overwrite=True)

def get_uv_stats(data_path, uid):
    '''Beasline statistics'''
    uvstats = au.getBaselineStats(data_path+uid)
    
    # save select stats
    n_bls = uvstats[0]
    min_bl = uvstats[1]
    max_bl = uvstats[2]
    med_bl = uvstats[3]
    mean_bl = uvstats[4]
    stddev_bl = uvstats[5]
    
    25pc_bl = uvstat[7]
    75pc_bl = uvstats[9]

    return [n_bls, min_bl, max_bl, med_bl, mean_bl, stddev_bl, 25pc_bl, 75pc_bl]
   
def get_img_stats(data_path,imgname):
    '''Get rms, major and minor beam axis of clean image'''
    imgfilename = data_path+'katy_imaging/'+imgname+'.image'
    rms = imstat(imgfilename)['rms'][0]      
    # resolution info
    maj_beam_val = imhead(imgfilename, mode='list')['perplanebeams']['median area beam']['major']['value']
    maj_beam_unit = imhead(imgfilename, mode='list')['perplanebeams']['median area beam']['major']['unit']
    
    min_beam_val = imhead(imgfilename, mode='list')['perplanebeams']['median area beam']['minor']['value']
    min_beam_unit = imhead(imgfilename, mode='list')['perplanebeams']['median area beam']['minor']['unit']
    
    return [imgname, rms, maj_beam_val, maj_beam_unit,
            min_beam_val, min_beam_unit]

def output_to_csv(stats):
    with open("/home/kproctor/summary_stats_all.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["image", "rms", "maj_beam", "units",
                    "min_beam", "units", 
                         "n_bls", "min_bl", "max_bl", 
                         "med_bl", "mean_bl", "stddev_bl", 
                         "25pc_bl", "75pc_bl"])
        writer.writerows(stats)

def spw_list_to_str(spw_list):
    '''Convert spw/list of spws to strings for tclean input'''
    
    spw_str = [',']*len(spw_list)

    for i in range(len(spw_list)):
        if isinstance(spw_list[i], list):
            spw_str[i] = str(','.join([str(elem) for elem in spw_list[i]]))
        else:
            spw_str[i] = str(spw_list[i])
    return spw_str

def main():
    # read spw list
    spw_list_file = 'J1229+0203_all.txt'
    spw_data = read_json(spw_list_file)
    
    uid_list = spw_data['uid']
    spw_list = spw_data['spwid']
    spw_str = spw_list_to_str(spw_list)
     
    # where the visibility data is located 
    data_path = '/scratch-sata/gcalistr/ALMACAL/J1229+0203/'
    summary_stats = []
    
    # for every uid, image separately and get stats
    for i, uid in enumerate(uid_list):
        print('Imaging ', i,uid)
        uid_str = str(uid)
        imgname = uid_str + '_co'
        
        # image each uid individually
        image(data_path, uid_str, spw_str[i], imgname)
    
        # gets stats and uv-coverage
        uv_stats = get_uv_stats(data_path, uid_str)
        summary_stats.append(get_img_stats(data_path,imgname)+uv_stats)
        #plot_uv(data_path,uid_str, spw_str[i])
        
    output_to_csv(summary_stats)    
    
if __name__ == "__main__":
    main()    
