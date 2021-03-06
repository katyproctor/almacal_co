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
    path = data_path+'katy_test/'
    cont_sub_vis = [data_path+str(uid)+'.contsub' for uid in uid_list]
    
    tclean(vis = cont_sub_vis,
       spw = spw_str,
       weighting = 'natural',
       imagename = path+imgname+'_dirty',
       imsize=500,
       width = '50km/s',
       cell = '0.2arcsec',
       specmode = 'cube')

     # calculate rms in relevant channels, in region that excludes the source
    rms = imstat(path+imgname+'_dirty.image', box='160,290,390,410', chans = '0~12')['rms'][0]
    return rms

def image_line_emission(data_path, uid_list, spw_str, rms, imgname):

    # clean continuum subtracted vis in source region
    cont_sub_vis = [data_path+str(uid)+'.contsub' for uid in uid_list]
    cutoff = 1.5*rms # threshold in Jy    

    tclean(vis = cont_sub_vis,
       spw = spw_str,
       weighting = 'natural',
       imagename = data_path+'katy_test/'+imgname,
       imsize=500,
       width = '50km/s',
       cell = '0.2arcsec',
       threshold = 1.5*rms,
       mask='box[[230,230],[280,260]]',
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
    
def main():
    # where the visibility data is located 
    data_path = '/scratch-sata/gcalistr/ALMACAL/J1229+0203/'

    # uids to combine - leave as empty list you want all in the .txt file
    husemann =['uid___A002_Xb66ea7_X6be9.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xba839d_X4e70.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xb66ea7_X5efb.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xb6e98e_X2489.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xb24884_X67e.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xb68dbd_X5b28.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xba3ea7_Xe79.ms.split.cal.J1229+0203_B3',
              'uid___A002_Xba3ea7_X781.ms.split.cal.J1229+0203_B3']
    
    #for uid in husemann:
     #   subtract_cont(data_path,str(uid))   
    
    # read spw list
    spw_list_file = 'husemann_extra.txt'
    spw_data = read_json(spw_list_file)
    uid_list = spw_data['uid']
    spw_list = spw_data['spwid']
   
    # test the addition of every other uid 
    extras = [item for item in uid_list if item not in husemann]
    
    count = 0
    # add uid from extras to Husemann list individually
    for extra in extras:
        count += 1
        print count, 'out of', len(extras)
    	uid_subset = husemann + [extra]

    	imgname = 'husemann_plus_' + str(extra)
        uid_list = spw_data['uid']
        spw_list = spw_data['spwid']
    	
        # subset to relevant uids and spws
    	if uid_subset:
            uid_list_all = uid_list
            spw_list_all = spw_list
            # subset spw_list to relevant uids
            uid_list = [uid_list_all[i] for i, entry in enumerate(uid_list_all) if entry in uid_subset]
            spw_list = [spw_list_all[i] for i, entry in enumerate(uid_list_all) if entry in uid_subset]
    
    	spw_str = spw_list_to_str(spw_list)
        
        # subtract continuum from new visibilities
        subtract_cont(data_path,str(extra))

        print 'Calculating rms of dirty image...'
        rms = dirty_image(data_path, uid_list, spw_str, imgname)
        print'RMS = ', rms
        print 'Imaging...'
        image_line_emission(data_path,uid_list,spw_str, rms, imgname)    
        print 'Done!'
if __name__ == "__main__":
    main()
