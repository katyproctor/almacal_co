# ALMACAL Analysis

### spw_list.py
- For a given source, will produce list of visibilities that have observations in the frequency range of interest
- Need to supply redshift of source, rest frequency of line transition, and folder containing visibilities 

### individual_quality_check.py
- Check rms and baseline properties of individual observations to assess which visibilities to combine for final image

### combine_image.py 
- Takes list of visibilities as input as combines to form an image

### image_stats.py
- Calculates statistics of combined image (rms, beam size, etc.)
