### Combine individual UIDs to create stacked image
### 

import json
import analysisUtils as au
import numpy as np

def read_json(file):
    with open(file) as f:
        data = json.load(f)
    return data

def subtract_cont(data_path,uid):
    """Subtract continuum
    """
    print(data_path+uid)
    uvcontsub(vis = data_path+uid, 
              fitorder=1, solint=int)

def dirty_image(data_path, uid_list, spw_str, imgname):
    # clean continuum subtracted vis
    cont_sub_vis = [data_path+str(uid)+'.contsub' for uid in uid_list]

    tclean(vis = cont_sub_vis,
       spw = spw_str,
       weighting = 'natural',
       imagename = data_path+imgname+'_dirty',
       imsize=500,outframe='LSRK',
       restfreq = '153.0743GHz',
       cell = '0.2arcsec',
       specmode = 'cube')

    # calculate rms in relevant channels, in region that excludes the source
    rms = imstat(data_path+imgname+'_dirty.image', box='185,175,318,225')['rms'][0]
   
    return rms

def image_line_emission(data_path, uid_list, spw_str, rms, imgname):

    # clean continuum subtracted vis
    cont_sub_vis = [data_path+str(uid)+'.contsub' for uid in uid_list]
    cutoff = 1.5*rms # threshold in Jy    
    
    tclean(vis = cont_sub_vis,
       spw = spw_str,
       weighting = 'natural',
       imagename = data_path+imgname,
       imsize=500,outframe='LSRK',
       restfreq = '153.0743GHz',
       cell = '0.2arcsec',
       threshold = 1.5*rms,
       mask='box[[230pix,230pix],[280pix,260pix]]',
       niter = 10000,
       specmode = 'cube')

def spw_list_to_str(spw_list):
    '''Convert spw/list of spws to strings for tclean input'''
    
    spw_str = [',']*len(spw_list)

    for i in range(len(spw_list)):
        if isinstance(spw_list[i], list):
            spw_str[i] = str(','.join([str(elem) for elem in spw_list[i]]))
        else:
            spw_str[i] = str(spw_list[i])
    return spw_str
   
def subset_lists(uid_list, spw_list, uid_subset):
    uid_list_all = uid_list
    spw_list_all = spw_list
    # subset spw_list to relevant uids
    uid_list = [uid_list_all[i] for i, entry in enumerate(uid_list_all) if entry in uid_subset]
    spw_list = [spw_list_all[i] for i, entry in enumerate(uid_list_all) if entry in uid_subset]
    return uid_list, spw_list

def main():
    imgname = 'hcn_images/hcn_2_1_limited'

    husemann =['uid___A002_Xb66ea7_X6be9.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xba839d_X4e70.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xb66ea7_X5efb.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xb6e98e_X2489.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xb24884_X67e.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xb68dbd_X5b28.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xba3ea7_Xe79.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xba3ea7_X781.ms.split.cal.J1229+0203_B3']
    
    # open text file containing uids that improve the image
    f = open("hcn2_1_low_rms_uids.txt", "r")
    extra = f.read().splitlines() 
    
    # subset of uids to combine - leave as an empty list if you want all uids in spw_list_file
    #uid_subset = husemann+extra
    uid_subset = extra
    #uid_subset = []

    # read list of all possible uids
    spw_list_file = 'J1229+0203_hcn2_1.txt'
    spw_data = read_json(spw_list_file)
    
    uid_list = spw_data['uid']
    spw_list = spw_data['spwid']
    
    # subset file list to uid_subset if not empty
    if uid_subset:
        uid_list, spw_list = subset_lists(uid_list, spw_list, uid_subset)
 
    # convert spw list to string for tclean
    spw_str = spw_list_to_str(spw_list)
    
    # where the visibility data is located 
    data_path = '/scratch-sata/gcalistr/ALMACAL/J1229+0203/'
    print uid_list
    #for i,uid in enumerate(uid_list):
        #uid_str = str(uid)
        #print('subtracting continuum for uid number: ',i,)
        #subtract_cont(data_path,uid_str)

    # image continuum subtracted together
    print 'Imaging...'
    rms = dirty_image(data_path, uid_list, spw_str, imgname)
    print 'rms =', rms
    #image_line_emission(data_path,uid_list,spw_str, rms, imgname)    
if __name__ == "__main__":
    main()
