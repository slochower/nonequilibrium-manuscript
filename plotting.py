import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import colorConverter
import seaborn as sns
import numpy as np
from aesthetics import paper_plot
from simulation import *
from tqdm import tqdm


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


def plot_fluxes_and_velocity(concentrations, directional_flux, reciprocating_flux, velocity,
                             ymin1=None, ymax1=None, label=None):
    cmap = sns.color_palette("Paired", 10)
    fig = plt.figure(figsize=(6 * 1.2, 6))
    gs = GridSpec(1, 1, wspace=0.2, hspace=0.5)
    ax1 = plt.subplot(gs[0, 0])

    ax1.plot(concentrations, velocity, c=cmap[1])
    ax1.set_xscale('log')
    ax1.set_ylim([ymin1, ymax1])
    ax1.set_ylabel(r'Catalytic rate (turnover s$^{{-1}}$)', color=cmap[1])
    ax2 = ax1.twinx()
    ax2.plot(concentrations, [abs(i) for i in directional_flux], c=cmap[3])
    ax2.plot(concentrations, [abs(i) for i in reciprocating_flux], c=cmap[3], ls='--')
    ax2.set_ylabel('Directional and reciprocating flux\n(cycle s$^{{-1}}$)', color=cmap[3])
    ax2.set_ylim([ymin1, ymax1])
    for tl in ax1.get_yticklabels():
        tl.set_color(cmap[1])
    for tl in ax2.get_yticklabels():
        tl.set_color(cmap[3])
    ax1.set_xlabel('Substrate concentration (M)')
    for ax in fig.axes:
        ax.tick_params(which='major', direction='out', length=10, pad=10)
        ax.tick_params(which='minor', direction='out', length=5)
        ax.xaxis.set_tick_params(width=2)
        ax.yaxis.set_tick_params(width=2)
        ax.xaxis.set_ticks_position('bottom')
        ax.spines["top"].set_visible(False)
        ax.xaxis.labelpad = 15
        ax.yaxis.labelpad = 15
    if label:
        ax.annotate(r'{}'.format(label), xy=(0.5, 0.5), xytext=(0.18, 0.9), xycoords='figure fraction', fontsize=20)
    fig.patch.set_facecolor('white')

def plot_flux_over_threshold(concentrations, number_above_thresholds, colors, names,
                             threshold_labels=None, xmin=10**-6, xmax=10**-2, ymin=0, ymax=140):
    fig = plt.figure(figsize=(6 * 1.2, 6))
    gs = GridSpec(1, 1, wspace=0.2, hspace=0.5)
    ax = plt.subplot(gs[0, 0])
    linestyles = ['-', '--']
    # For simplicity, I think I should enforce paired plotting. That is, to plot the number of angles over two
    # thresholds for each system, with the line styles given above. We should be able to handle an arbitrary number of
    # pairs.
    pairs = [number_above_thresholds[x:x+2] for x in range(0, len(number_above_thresholds), 2)]
    for system, color, name in zip(pairs, colors, names):
        ax.plot(concentrations, system[0], ls='-', c=color, label=name)
        ax.plot(concentrations, system[1], ls='--', c=color)


    handles, labels = ax.get_legend_handles_labels()
    display = (0, 1, 2)
    artists = []
    for threshold_label, style in zip(threshold_labels, linestyles):
        artists.append(plt.Line2D((0, 1), (0, 0), color='k', linestyle=style))

    ax.legend([handle for i, handle in enumerate(handles) if i in display] + artists,
              [label for i, label in enumerate(labels) if i in display] + threshold_labels,
              loc='upper left', frameon=True)
    ax.set_xlabel('Substrate concentration (M)')
    ax.set_ylabel('Number of angles over threshold')
    ax.set_xscale('log')
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    paper_plot(fig)

# Below, these helper functions are necessary for the summary plots that are designed mostly to read in pandas
# dataframes
def return_concentration_slice(df, concentration):
    """
    This helper function makes slicing dataframes easy.
    :param df: a dataframe that contains a column named 'Concentration'
    :param concentration: a target concentration, that will be rounded
    :return: the dataframe slice at the given concentration
    """
    tmp = df[np.round(df['Concentration'], 1) ==  np.round(concentration, 1)]
    return tmp


def return_fluxes_and_velocity(protein, name, concentrations):
    """
    This helper function will return the turnover rate and the fluxes over a concentration range.
    :param protein: one of the recognized protein systems in the class
    :param name: filename of the torsion
    :param concentrations: a list concentrations
    :return:
    """
    directional_flux, reciprocating_flux, velocity = [], [], []
    for concentration in tqdm(concentrations):
        this = Simulation(data_source=protein)
        this.name = name
        this.cSubstrate = concentration
        this.simulate()
        directional_flux.append(np.mean(this.flux_u + this.flux_b))
        reciprocating_flux.append(np.max(np.hstack((abs(this.flux_u), abs(this.flux_b)))))
        velocity.append(np.sum(this.ss[this.bins:2*this.bins]) * this.catalytic_rate)
    return directional_flux, reciprocating_flux, velocity


def find_above_threshold(df, quantity, threshold):
    concentrations = []
    number_above_threshold = []
    for concentration in tqdm(np.unique(df['Concentration'].values)):
        tmp = return_concentration_slice(df, concentration)
        concentrations.append(10**concentration)
        number_above_threshold.append(sum(tmp[str(quantity)].abs() > threshold))
    return concentrations, number_above_threshold
