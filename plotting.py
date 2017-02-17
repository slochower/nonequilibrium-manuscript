import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import colorConverter
import seaborn as sns
import numpy as np
from aesthetics import paper_plot


def plot_input(this, save=False, filename=None):
    """
    This function plots the unbound and bound input histograms associated with a simulation
    object. The input histograms are taken to be normalized populations derived from MD simulations.
    """
    bins = this.bins
    unbound_population = this.unbound_population
    bound_population = this.bound_population
    unbound_clr = this.unbound_clr
    bound_clr = this.bound_clr

    fig = plt.figure(figsize=(6 * 1.2, 6))
    gs = GridSpec(1, 1, wspace=0.2, hspace=0.5)
    ax1 = plt.subplot(gs[0, 0])
    ax1.plot(range(bins), unbound_population, c=unbound_clr)
    ax1.plot(range(bins), bound_population, c=bound_clr, ls='--')
    ax1.set_xticks([0, bins / 4, bins / 2, 3 * bins / 4, bins])
    ax1.set_xticklabels(
        [r'$-\pi$', r'$-\frac{1}{2}\pi{}$', r'$0$', r'$\frac{1}{2}\pi$', r'$\pi$'])
    ax1.set_xlabel(r'$\theta$ (rad)')
    ax1.set_ylabel(r'$p$ (input population)')
    paper_plot(fig, scientific=False)
    if save:
        plt.savefig(filename + '.png', dpi=300, bbox_inches='tight')
    # return fig


def plot_energy(this, save=False, filename=None):
    """
    This function plots the unbound and bound energies (i.e., chemical potentials)
    associated with a Simulation object.
    """

    bins = this.bins
    unbound_energy = this.unbound
    bound_energy = this.bound
    unbound_clr = this.unbound_clr
    bound_clr = this.bound_clr

    fig = plt.figure(figsize=(6 * 1.2, 6))
    gs = GridSpec(1, 1, wspace=0.2, hspace=0.5)
    ax1 = plt.subplot(gs[0, 0])
    ax1.plot(range(bins), unbound_energy, c=unbound_clr)
    ax1.plot(range(bins), bound_energy, c=bound_clr, ls='--')
    ax1.set_xticks([0, bins / 4, bins / 2, 3 * bins / 4, bins])
    ax1.set_xticklabels(
        [r'$-\pi$', r'$-\frac{1}{2}\pi{}$', r'$0$', r'$\frac{1}{2}\pi$', r'$\pi$'])
    ax1.set_xlabel(r'$\theta$ (rad)')
    ax1.set_ylabel(r'$\mu$ (kcal mol$^{-1}$)')
    paper_plot(fig, scientific=False)
    if save:
        plt.savefig(filename + '.png', dpi=300, bbox_inches='tight')
    # return fig


def plot_ss(this, save=False, filename=None):
    """
    This function plots the nonequilibrium steady-state distribution associated
    with a Simulation object.
    By default, this will plot the eigenvector-derived steady-state distribution.
    """

    bins = this.bins
    unbound_ss = this.ss[0:bins]
    bound_ss = this.ss[bins:2*bins]
    unbound_clr = this.unbound_clr
    bound_clr = this.bound_clr

    fig = plt.figure(figsize=(6 * 1.2, 6))
    gs = GridSpec(1, 1, wspace=0.2, hspace=0.5)
    ax1 = plt.subplot(gs[0, 0])
    ax1.plot(range(bins), unbound_ss, c=unbound_clr)
    ax1.plot(range(bins), bound_ss, c=bound_clr, ls='--')
    ax1.set_xticks([0, bins / 4, bins / 2, 3 * bins / 4, bins])
    ax1.set_xticklabels(
        [r'$-\pi$', r'$-\frac{1}{2}\pi{}$', r'$0$', r'$\frac{1}{2}\pi$', r'$\pi$'])
    ax1.set_xlabel(r'$\theta$ (rad)')
    ax1.set_ylabel(r'$p$ (probability)')
    paper_plot(fig, scientific=False)
    if save:
        plt.savefig(filename + '.png', dpi=300, bbox_inches='tight')
    # return fig


def print_parameter(label, value, unit):
    """
    This function pretty prints some class variables for the flux plots.
    :param label:
    :param value:
    :param unit:
    :return:
    """
    print('{:<25} {:<+10.2e} {:<10}'.format(label, value, unit))


def plot_flux(this, save=False, filename=None):
    """
    This function plots the intrasurface flux separately and as a sum. The intrasurface flux
    is the directional flux. This also prints the simulation parameters.
    """

    bins = this.bins
    C = this.C_intersurface
    D = this.D
    catalytic_rate = this.catalytic_rate
    cSubstrate = this.cSubstrate
    dt = this.dt
    unbound_flux = this.flux_u
    bound_flux = this.flux_b
    intersurface_flux = this.flux_ub
    unbound_clr = this.unbound_clr
    bound_clr = this.bound_clr
    load = this.load

    print_parameter('C', C, 'second**-1')
    print_parameter('D', D, 'degrees**2 second**-1')
    print_parameter('k_{cat}', catalytic_rate, 'second**-1')
    print_parameter('[S]', cSubstrate, 'M')
    print_parameter('dt', dt, 'second')
    print('-'*25)
    print_parameter('Intrasurface flux', np.mean(unbound_flux + bound_flux), 'cycle second**-1')
    print_parameter('Peak', np.max(np.hstack((unbound_flux, bound_flux))), 'cycle second**-1')
    if load:
        print('-' * 25)
        applied_load = this.load_slope
        power = applied_load * np.mean(unbound_flux + bound_flux)
        print_parameter('Applied load', applied_load, 'kcal mol**-1 cycle**-1')
        print_parameter('Power generated', power, 'kcal mol**-1 second**-1')

    fig = plt.figure(figsize=(6 * 1.2, 6))
    gs = GridSpec(1, 1, wspace=0.2, hspace=0.5)
    ax1 = plt.subplot(gs[0, 0])
    ax1.plot(range(bins), unbound_flux, c=unbound_clr)
    ax1.plot(range(bins), bound_flux,   c=bound_clr, ls='--')
    ax1.plot(range(bins), unbound_flux + bound_flux, c='k', ls='-', lw=2, alpha=0.5, zorder=-1, label='Net flux')
    ax1.set_xticks([0, bins / 4, bins / 2, 3 * bins / 4, bins])
    ax1.set_xticklabels(
        [r'$-\pi$', r'$-\frac{1}{2}\pi{}$', r'$0$', r'$\frac{1}{2}\pi$', r'$\pi$'])
    ax1.set_xlabel(r'$\theta$ (rad)')
    ax1.set_ylabel('Flux $J$ (cycle s$^{-1}$)')
    ax1.legend(frameon=True)
    paper_plot(fig, scientific=False)
    if save:
        plt.savefig(filename + '.png', dpi=300, bbox_inches='tight')


def plot_load(this, save=False, filename=None):
    """
    This function plots the unbound and bound energy surfaces with a constant added load.
    """

    bins = this.bins
    unbound_energy = this.unbound
    bound_energy = this.bound
    unbound_clr = this.unbound_clr
    bound_clr = this.bound_clr

    fig = plt.figure(figsize=(6 * 1.2, 6))
    gs = GridSpec(1, 1, wspace=0.2, hspace=0.5)
    ax1 = plt.subplot(gs[0, 0])
    ax1.plot(range(bins), [unbound_energy[i] + this.load_function(i) for i in range(bins)],
             c='k', ls='--', lw=2)
    ax1.plot(range(bins), unbound_energy, c=unbound_clr)
    ax1.plot(range(bins), [bound_energy[i] + this.load_function(i) for i in range(bins)],
             c='k', ls='--', lw=2)
    ax1.plot(range(bins), bound_energy, c=bound_clr, ls='--')

    ax1.set_xticks([0, bins / 4, bins / 2, 3 * bins / 4, bins])
    ax1.set_xticklabels(
        [r'$-\pi$', r'$-\frac{1}{2}\pi{}$', r'$0$', r'$\frac{1}{2}\pi$', r'$\pi$'])
    ax1.set_xlabel(r'$\theta$ (rad)')
    ax1.set_ylabel(r'$\mu$ (kcal mol$^{-1}$)')
    paper_plot(fig, scientific=False)
    if save:
        plt.savefig(filename + '.png', dpi=300, bbox_inches='tight')


# Now, these are summary plots.