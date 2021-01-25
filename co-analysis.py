uid_list = ['uid___A002_Xb66ea7_X5efb', 'uid___A002_Xb24884_X67e',
           'uid___A002_Xb6e98e_X2489', 'uid___A002_Xb66ea7_X6be9',
           'uid___A002_Xba839d_X4e70'] # these are uids from the data used in the Husemann 2019 paper

def subtract_cont(uid):
    """Subtract continuum
    and plot spectra, after subtraction. 
    """
    vis = uid + '.ms.split.cal.J1229+0203_B3'

    # subtract continuum 
    # TODO: do only for relevant spw
    os.system('rm -rf' + vis + '.contsub')
    uvcontsub(vis = vis, 
              #linespw = , spectral window w line emission
              fitorder=1, solint=int)

    # plot continuum subtracted spectra
    plotms(vis=vis + '.contsub',spw='',xaxis='channel',yaxis='amp',
           avgtime='1e8',avgscan=True, iteraxis='spw', 
           plotfile = 'spectra/uv-subtracted/spectrum_contsub_' + uid + '.png', 
           expformat = 'png', exprange = 'all', overwrite=True)
    
def image_line_emission(uid_list):
    
    # co rest freq
    restfreq = '115.271201800GHz'
    imgname = 'J1229_0203_stacked_co'
    
    # clean the continuum subtracted vis for all uids
    cont_sub_vis = [uid +'.ms.split.cal.J1229+0203_B3.contsub' for uid in uid_list]
    
    os.system('rm -rf J1229_0203_stacked_co*')
    tclean(vis = cont_sub_vis,
       imagename = imgname,
       specmode = 'cube',
       outframe = 'LSRK',
       restfreq = restfreq,
       deconvolver= 'hogbom',
       gridder = 'standard')
    
    imview(imgname+'.image')
    
def main():
    for uid in uid_list:
        subtract_cont(uid)
        
    image_line_emission(uid_list)    
        
if __name__ == "__main__":
    main()