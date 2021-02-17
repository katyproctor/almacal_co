import numpy as np
import analysisUtils as au
import csv
import os

### Output rms of combined image to a csv
image_filepath = '/scratch-sata/gcalistr/ALMACAL/J1229+0203/katy_test/'
file_names = os.listdir(image_filepath)

# add column husemann 8 uids as first entry, with uid list to contain the extra uid added
image_names = ['husemann.image']
uid_list = ['']
for file in file_names:
    try:
        folder_name = re.search('^.*plus_(.+?).image', file).group(0)
        uid_name = re.search('^.*plus_(.+?).image', file).group(1)
        
        uid_list.append(uid_name)
        image_names.append(folder_name)    
    except AttributeError:
    # plus_, .image not found in the original string
        print 'String not found'

csv_name = 'combined_stats.csv'
rms = []
maj_beam = []
min_beam=[]

for image in image_names:
    img_file = image_filepath+image
    print(img_file)
    rms.append(imstat(img_file, box='160,290,390,410', chans='0~12')['rms'][0]) 
    
    maj_beam_val = imhead(img_file, mode='list')['perplanebeams']['median area beam']['major']['value']
    min_beam_val = imhead(img_file, mode='list')['perplanebeams']['median area beam']['minor']['value']
    
    maj_beam.append(maj_beam_val)
    min_beam.append(min_beam_val)

# calculate the rms difference from the image using the 6 uids
rms_diff = [rms_uid - rms[0] for rms_uid in rms]
# add % improv column
rms_pc_diff = [diff/rms[0] for diff in rms_diff]

with open("/home/kproctor/combined_image_stats.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["image", "extra_uid", "rms", "rms_diff", "rms_pc_diff", "maj_beam", "min_beam"])
    writer.writerows(np.array([image_names, uid_list, rms, rms_diff, rms_pc_diff, maj_beam, min_beam]).T)
