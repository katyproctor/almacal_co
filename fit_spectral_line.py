import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.modeling import models, fitting
from astropy.modeling.models import custom_model
from astropy.modeling import Fittable1DModel, Parameter

def limit_data(dat, low, upp):
    # fit to frequency range between lower and upper limit
    ind = np.where((dat[0]/1e9 > low) & (dat[0]/1e9 < upp))
    # freq in GHz
    freq = dat[0][ind]/1e9
    flux = dat[1][ind]
    
    return freq, flux

def plot_spectra(freq, flux, outname):
    
    fig, ax = plt.subplots(figsize=(8,5))
    
    ax.plot(freq, flux, alpha=0.8, linewidth = 2)
    ax.axhline(0, c='grey', linestyle = '--')
    
    ax.axvline(99.42, c='red', linestyle = '--')
    ax.axvline(99.52, c='red', linestyle = '--')

    ax.set_xlabel('Frequency (GHz)', fontsize =14)
    ax.set_ylabel('Flux Density (Jy)', fontsize=14)
    plt.savefig('plots/' + str(outname) + '_spectra.png', dpi = 300)
    
    
def fit_three_component(freq, flux, a1, a2, f1, f2, s1, s2):   
    
    # 2 gaussian components + vertical offset to account for issues in cont sub
    g1 = models.Gaussian1D(a1, f1, s1) # amplitude, freq, standard dev.
    g2 = models.Gaussian1D(a1, f2, s2)
    offset = models.Polynomial1D(degree=0)
    
    triple_model = g1 + g2 + offset

    # set limits on location of peak
    delta = 0.03
    triple_model.mean_0.max = f1 + delta
    triple_model.mean_0.min = f1 - delta
    triple_model.mean_1.max = f2 + delta
    triple_model.mean_1.min = f2 - delta
    
    # perform fit
    fitter = fitting.LevMarLSQFitter()
    gaussian_fit = fitter(triple_model, freq, flux)
    
    return gaussian_fit

def plot_result(freq, flux, gaussian_fit, outname):
    
    fig, ax = plt.subplots(figsize=(8,5))
    
    ax.plot(freq, flux, color='k')
    ax.plot(freq, gaussian_fit(freq), color='darkorange')
    ax.set_xlabel('Frequency (GHz)', fontsize =14)
    ax.set_ylabel('Flux Density (Jy)', fontsize=14)
    
    plt.savefig('plots/'+ str(outname) + '_fit_result.png', dpi = 300)
    
    
def main():
    # load data and specify frequency bounds
    dat = np.loadtxt('../data/J1229+0203/co1_0_husemann_improved.image_spectra_mask.txt').T
    outname = 'husemann_improved'
    upp = 99.8
    low = 98.9
    
    # limit and plot data
    freq, flux = limit_data(dat, low, upp)
    plot_spectra(freq, flux, outname)
    
    # provide initial guesses
    a1 = 0.003
    a2 = 0.002
    f1 = 99.42
    f2 = 99.52
    s1 = 0.02
    s2 = 0.02
    
    # fit spectral line and plot
    model = fit_three_component(freq, flux, a1, a2, f1, f2, s1, s2)
    plot_result(freq, flux, model, outname)
    
if __name__ == "__main__":
    main()    