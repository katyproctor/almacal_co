import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.modeling import models, fitting
from astropy.modeling.models import custom_model
from astropy.modeling import Fittable1DModel, Parameter

def limit_data(dat, low, upp):
    # freq in GHz
    freq = dat[0]/1e9
    flux = dat[1]
    
    # use velocity rather than freq
    f0 = 99.5
    c = 3e8
    # velocity in km/s
    v = ((f0 - freq)/f0*c)/1e3
    
    # fit to frequency range between lower and upper limit
    ind = np.where((v > low) & (v < upp))

    v = v[ind]
    flux=flux[ind]
    
    return v, flux

def plot_spectra(low, upp, v, flux, outname):
    
    fig, ax = plt.subplots(figsize=(8,5))
    
    ax.plot(v, flux, alpha=0.8, linewidth = 2)
    ax.axhline(0, c='grey', linestyle = '--')
    
    ax.axvline(low, c='red', linestyle = '--')
    ax.axvline(upp, c='red', linestyle = '--')

    ax.set_xlabel('Velocity (km/s)', fontsize =14)
    ax.set_ylabel('Flux Density (Jy)', fontsize=14)
    
    plt.savefig('plots/' + str(outname) + '_spectra.png', dpi = 300)
    
    
def fit_three_component(v, flux, a1, a2, v1, v2, s1, s2):   
    
    # 2 gaussian components + vertical offset to account for issues in cont sub
    g1 = models.Gaussian1D(a1, v1, s1) # amplitude, vel, standard dev.
    g2 = models.Gaussian1D(a1, v2, s2)
    offset = models.Polynomial1D(degree=0)
    
    triple_model = g1 + g2 + offset

    # set limits on location of peak
    delta = 10 # in km/s
    triple_model.mean_0.max = v1 + delta
    triple_model.mean_0.min = v1 - delta
    triple_model.mean_1.max = v2 + delta
    triple_model.mean_1.min = v2 - delta
    
    # perform fit
    fitter = fitting.LevMarLSQFitter()
    gaussian_fit = fitter(triple_model, v, flux)
    
    return gaussian_fit

def plot_result(low, upp, vel, flux, gaussian_fit, outname):
    
    fig, ax = plt.subplots(figsize=(8,5))
    
    ax.plot(vel, flux, color='k')
    
    # plot model at higher resolution
    v_arr = np.arange(low, upp, 1e-3)
    ax.plot(v_arr, gaussian_fit(v_arr), color='darkorange')
    ax.set_xlabel('Velocity (km/s)', fontsize =14)
    ax.set_ylabel('Flux Density (Jy)', fontsize=14)
    
    plt.savefig('plots/'+ str(outname) + '_fit_result.png', dpi = 300)
    
    
def main():
    # load data and specify plot name
    dat = np.loadtxt('../data/J1229+0203/co1_0_husemann_improved_highres.image_spectra_mask.txt').T
    outname = 'husemann_improved_highres'
    
    # range for fitting in km/s
    upp = 1400
    low = -700
    
    # limit and plot data
    vel, flux = limit_data(dat, low, upp)
    
    # provide initial guesses for fit values
    a1 = 0.004
    a2 = 0.0025
    v1 = -30
    v2 = 240
    s1 = 70
    s2 = 70
    
    plot_spectra(v1, v2, vel, flux, outname)
    
    # fit spectral line and plot
    model = fit_three_component(vel, flux, a1, a2, v1, v2, s1, s2)
    plot_result(low, upp, vel, flux, model, outname)
    
if __name__ == "__main__":
    main()    