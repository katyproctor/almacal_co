import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.modeling import models, fitting
from astropy.modeling.models import custom_model
from astropy.modeling import Fittable1DModel, Parameter
from scipy import integrate

def limit_data(dat, low, upp, f0):
    # freq in GHz
    freq = dat[0]/1e9
    flux = dat[1]
    
    # use velocity rather than freq
    c = 3e8
    # velocity in km/s
    v = ((f0 - freq)/f0*c)/1e3
    
    # fit to velocity range between lower and upper limit
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
    delta = 20 # in km/s
    triple_model.mean_0.max = v1 + delta
    triple_model.mean_0.min = v1 - delta
    triple_model.mean_1.max = v2 + delta
    triple_model.mean_1.min = v2 - delta
    
    # perform fit
    fitter = fitting.LevMarLSQFitter()
    gaussian_fit = fitter(triple_model, v, flux)
    
    return gaussian_fit

def fit_gaussian(v, flux, a1, v1, s1):   
    
    # 2 gaussian components + vertical offset to account for issues in cont sub
    g1 = models.Gaussian1D(a1, v1, s1) # amplitude, vel, standard dev.
    offset = models.Polynomial1D(degree=0)
    
    double_model = g1 + offset

    # set limits on location of peak
    delta = 20 # in km/s
    double_model.mean_0.max = v1 + delta
    double_model.mean_0.min = v1 - delta
    
    # perform fit
    fitter = fitting.LevMarLSQFitter()
    gaussian_fit = fitter(double_model, v, flux)
    
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
    
def calc_flux(model, lowlim, uplim):
    '''return flux value in Jy.km/s'''
    # account for vertical offset
    offset = model[-1](lowlim)
    
    def offset_model(x):
        return model(x) - offset
    
    return integrate.quad(offset_model, lowlim, uplim)
    
    
def main():
    # load data and specify plot name
    dat = np.loadtxt('../data/J1229+0203/co2_1_omission.image_spectra_mask.txt').T
    outname = 'co2_1_omission'
    
    # range for fitting in km/s
    upp = 400
    low = -1000
    
    # observed frequency of line transition
    f0 = 199.0846
    
    # limit and plot data
    vel, flux = limit_data(dat, low, upp, f0)
    
    # provide initial guesses for fit values
    a1 = 0.01
    a2 = 0.01
    v1 = 125
    v2 = 350
    s1 = 130
    s2 = 50
    
    a1 = 0.008
    s1 = 210
    v1 = 100
    
    plot_spectra(v1, v2, vel, flux, outname)
    
    # fit spectral line and plot
    # use this for double gaussian
    #model = fit_three_component(vel, flux, a1, a2, v1, v2, s1, s2)
    
    
    # use this for single gaussian (co(2-1))
    model = fit_gaussian(vel, flux, a1, v1, s1)
    print(model[0], model[1])
    
    plot_result(low, upp, vel, flux, model, outname)
    
    # get flux between integral limits
    flux_up = 400
    flux_low = -100
    flux = calc_flux(model, flux_low, flux_up)
    print('Total flux = ', flux[0], ' Jy.km/s')
    
if __name__ == "__main__":
    main()    