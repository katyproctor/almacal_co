import os
import re
import json
import numpy as np
import matplotlib.pyplot as plt 
import analysisUtils as au

def read_spw(vis):
    """read the spectral windows
    """
    if isinstance(vis, str):
        vis = [vis, ]
    
    if not isinstance(vis, list):
        raise ValueError("read_spw: Unsupported measurements files!")
    
    spw_specrange = {}

    # Read the spectral window frequency ranges
    for v in vis:
        tb.open(v + '/SPECTRAL_WINDOW')
        col_names = tb.getvarcol('NAME')
        col_freq = tb.getvarcol('CHAN_FREQ')
        tb.close()

        for key in col_names.keys():
            freq_max = np.max(col_freq[key]) / 1e9
            freq_min = np.min(col_freq[key]) / 1e9
            spw_specrange[key] = [freq_min, freq_max]

    return spw_specrange


def calc_obs_freq(restfreq, zsource):

    f = restfreq/(zsource + 1)

    low_lim = round(f,1) - 0.5
    high_lim = round(f,1) + 0.5

    return [low_lim,high_lim]


def spw_stat(objfolder, vis=None, savedata=False, spw_list_path=None, z=0, lines=None, lines_names=None, debug=False):

    spw_list = {'B3':{'name':[], 'time':[], 'freq':[], 'spwid':[]},
                'B4':{'name':[], 'time':[], 'freq':[], 'spwid':[]},
                'B5':{'name':[], 'time':[], 'freq':[], 'spwid':[]},
                'B6':{'name':[], 'time':[], 'freq':[], 'spwid':[]},
                'B7':{'name':[], 'time':[], 'freq':[], 'spwid':[]},
                'B8':{'name':[], 'time':[], 'freq':[], 'spwid':[]},
                'B9':{'name':[], 'time':[], 'freq':[], 'spwid':[]},
                'B10':{'name':[], 'time':[], 'freq':[], 'spwid':[]},}
    filelist = []

    base_dir = objfolder
    obj = os.path.basename(objfolder)

    p_obs = re.compile('^uid___.*\d$')

    for obs in os.listdir(base_dir):
        if p_obs.match(obs):
            filelist.append(os.path.join(base_dir, obs))

    band_match = re.compile('_(?P<band>B\d{1,2})')

    for obs in filelist:
        try:
            if band_match.search(obs):
                band = band_match.search(obs).groupdict()['band']
                if debug:
                    print("Band: ", band)
            else:
                print("Error in band match.")

            spw_list[band]['name'].append(os.path.basename(obs))
            spw_specrange_buff = read_spw(obs)
            spw_specrange = spw_specrange_buff.values()
            spw_ids = spw_specrange_buff.keys()

            # Fix SPW ids
            for l in range(0, len(spw_ids)):
                if(spw_ids[l] == 'r1'):
                    spw_ids[l] = 0
                elif(spw_ids[l] == 'r2'):
                    spw_ids[l] = 1
                elif(spw_ids[l] == 'r3'):
                    spw_ids[l] = 2
                elif(spw_ids[l] == 'r4'):
                    spw_ids[l] = 3
                elif(spw_ids[l] == 'r5'):
                    spw_ids[l] = 4
                elif(spw_ids[l] == 'r6'):
                    spw_ids[l] = 5
                elif(spw_ids[l] == 'r7'):
                    spw_ids[l] = 6
 
            spw_list[band]['freq'].append(list(spw_specrange))
            spw_list[band]['spwid'].append(list(spw_ids))
        except:
            print("Error: in", obs)

    if savedata:
        with open(spw_list_path, 'w') as fp:
            json.dump(spw_list, fp)
    return spw_list


#function to find overlap in SPW freq and line freq ranges
def findOverlap(a, b, rtol = 1e-03, atol = 1e-03, equal_nan = False):
    overlap_indexes = []
    for i, item_a in enumerate(a):
        for item_b in b:
            if np.isclose(item_a, item_b, rtol = rtol, atol = atol, equal_nan = equal_nan):
                overlap_indexes.append(i)
    return overlap_indexes


def create_spw_list(ms_folder, linerange, savedata=False, spw_list_path = None):

	spw_stat_list = spw_stat(objfolder=ms_folder)
	spw_list = {'uid':[], 'spwid':[]}
        # TODO: ideally this would not be manual
        band = 'B7'

	print('Read in SPW frequency ranges...')
	for i in range(0, len(spw_stat_list[band]['name'])):
	    name = spw_stat_list[band]['name'][i]
	    freqs = spw_stat_list[band]['freq'][i]
	    spwid = spw_stat_list[band]['spwid'][i]
	    avail_spws = []
	    spw_avail = False

	    print('Checking frequency overlap for ' + str(name) + '...')
	    for k in range(0, len(freqs)):
	    	lin_arr = np.arange(linerange[0], linerange[1], step=0.1)
	    	freq_arr = np.arange(np.round(min(freqs[k]),decimals=2), np.round(max(freqs[k]), decimals=2), step=0.1)
	    	overlap = findOverlap(lin_arr, freq_arr)

	        if len(overlap) > 0:
	            avail_spws.append(spwid[k])
	            spw_avail = True

	    if spw_avail == True:
	    	print('Frequency overlap for ' + str(name) + ' SPWs: ' + str(avail_spws))
	    	print('')
	        spw_list['uid'].append(name)
	        spw_list['spwid'].append(avail_spws)
	    else:
	    	print('No frequency overlap for ' + str(name))
	    	print('')
	
	print('SPW List:')
	print(spw_list)
        print(len(spw_list['spwid']))

	if savedata:
		print('Saving SPW list in ' + str(spw_list_path))
		with open(spw_list_path, 'w') as fp:
			json.dump(spw_list, fp)

	print('Creating spw_list is done! \n \n')
	return spw_list

def read_json(file):
	with open(file) as f:
		data = json.load(f)
	return data


def main():

	# Set these two variables to the directory of the ms files
	ms_file_path = '/scratch-sata/gcalistr/ALMACAL/J1229+0203/'
	# Specify the range of the CO line [lower limit, upper limit] in GHz - or use calc_obs_freq to get 1GHz range around the observed line freq
	#linerange=[99.,100.]
        
        # co rest frequencies
        co1_0=115.27
        co2_1=230.54
        co3_2=345.80
        co4_3=461.04
        co5_4=576.27
        co6_5=691.47

        linerange = calc_obs_freq(restfreq = co3_2, zsource = 0.158)
        print(linerange)

	# Use this part instead if you want the SPW list saved, will read the SPW list from that file too afterwards
	spw_list_path = 'husemann_co3_2.txt'
	create_spw_list(ms_folder=ms_file_path, linerange=linerange, savedata=True, spw_list_path=spw_list_path)
#	spw_list_file = 'husemann_co3_2.txt'
#	spw_data = read_json(spw_list_file)

#	uid_list = spw_data['uid']
#	spw_list = spw_data['spwid']
        
        
        
if __name__ == "__main__":
    main()
