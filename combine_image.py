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

def image_line_emission(data_path, uid_list, spw_str):
    imgname = 'husemann_6uids'

    # clean continuum subtracted vis
    cont_sub_vis = [data_path+str(uid)+'.contsub' for uid in uid_list]
    print cont_sub_vis, spw_str 
    tclean(vis = cont_sub_vis,
       spw = spw_str,
       weighting = 'natural',
       imagename = data_path+imgname,
       imsize=500,
       cell = '0.2arcsec',
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
    
def main():
    
    # uids to combine - leave as empty list you want all in the .txt file
    uid_subset=['uid___A002_Xb66ea7_X6be9.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xba839d_X4e70.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xb66ea7_X5efb.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xb6e98e_X2489.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xb24884_X67e.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xb68dbd_X5b28.ms.split.cal.J1229+0203_B3']

    # read spw list
    spw_list_file = 'husemann_extra.txt'
    spw_data = read_json(spw_list_file)
    
    uid_list = spw_data['uid']
    spw_list = spw_data['spwid']

    if uid_subset:
        uid_list_all = uid_list
        spw_list_all = spw_list
        # subset spw_list to relevant uids
        uid_list = [uid_list_all[i] for i, entry in enumerate(uid_list_all) if entry in uid_subset]
        spw_list = [spw_list_all[i] for i, entry in enumerate(uid_list_all) if entry in uid_subset]
    
    # convert spw list to string for tclean
    spw_str = spw_list_to_str(spw_list)
    
    # where the visibility data is located 
    data_path = '/scratch-sata/gcalistr/ALMACAL/J1229+0203/katy_test/'

    for i,uid in enumerate(uid_list):
        uid_str = str(uid)
        print('subtracting continuum for uid number: ',i,)
        subtract_cont(data_path,uid_str)

    # image continuum subtracted together
    print 'Imaging...'
    image_line_emission(data_path,uid_list,spw_str)    
        
if __name__ == "__main__":
    main()
