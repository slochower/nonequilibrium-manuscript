#!/usr/bin/env python
"""
This module contains the code to calculate probability flux given two equilibrium
population distributions.
"""

import math as math
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from scipy.ndimage.filters import gaussian_filter
from matplotlib.gridspec import GridSpec
import scipy as sc
import aesthetics
import seaborn as sns


class simulation(object):
    def __init__(self, data_source):
        """
        These values are assigned to a new object, unless overridden later.
        """
        # Model parameters
        self.kT = 0.6  # RT = 0.6 kcal per mol
        # The butane-derived D value is 3 * 10 ** 15, but we've now shown that
        # a lower value can be safely used without changing the results much.
        self.D = 3 * 10 ** 12  # degree**2 per second
        # By default, don't iteratively refine the steady state population.
        self.iterations = 0
        # Implementation parameters
        self.dir = None
        self.data_source = data_source
        if self.data_source == 'pka_md_data' or self.data_source == 'pka_reversed':
            self.C_intersurface = 0.24 * 10 ** 6  # per mole per second
            self.offset_factor = 6.0  # kcal per mol
            self.catalytic_rate = 140  # per second
            self.cSubstrate = 2 * 10 ** -3 # ATP concentration (M)
        elif self.data_source == 'adk_md_data':
            self.C_intersurface = 10 ** 6  # per mole per second
            self.offset_factor = 5.7  # kcal per mol
            self.catalytic_rate = 312  # per second
            # Let's say ATP concentration = 9 * 10**-3 M and AMP concentration = 2.8 * 10**-4 M
            # Absolute metabolite concentrations and implied enzyme active site occupancy in
            # Escherichia coli (2009), Nat Chem Biol
            self.cSubstrate = 2.5 * 10 ** -6   # ATP.AMP concentration (M) as a single concentration
        elif self.data_source == 'hiv_md_data':
            self.C_intersurface = 10 ** 6  # per mole per second
            self.offset_factor = 4.5  # kcal per mol
            self.catalytic_rate = 0.3  # per second
            self.cSubstrate = 2 * 10 ** -3 # Gag concentration (M)
        elif self.data_source == 'manual':
            print('Using manual parameters, specify C, offset, and catalytic rate.')
        else:
            print('No data source; no values for C, offset, and catalytic rate')

        # The name needs to be provided at runtime, unless the data source is manual.
        self.name = None
        # The initial populations are empty, until parsed from the files.
        self.unbound_population = []
        self.bound_population = []
        # The PDFs are derived from the populations.
        self.PDF_unbound = None
        self.PDF_bound = None
        # The rates will be calculated from the energy surfaces.
        self.forward_rates = None
        self.backward_rates = None
        # The transition matrix is composed from the rates.
        self.tm = None
        # The time step `dt` is determined so all elements in the transition matrix are in [0, 1).
        self.dt = None
        # The eigenvalues and steady state population are calculated from the transition matrix.
        self.eigenvalues = None
        self.ss = None
        # The surface fluxes are calculated using the rates and the populations.
        self.flux_u = None
        self.flux_b = None
        self.flux_ub = None


        # By default, we run without any applied load on the motor.
        self.load = False
        if self.load:
            self.load_slope = self.bins  # kcal per mol per (2 * pi) radians
        else:
            self.load_slope = 0


    def plot_input(self, save=False, filename=None):
        """
        This function plots the unbound and bound input histograms associated with a simulation object.
        The input histograms are taken to be normalized populations derived from MD simulations.
        """

        fig = plt.figure(figsize=(6 * 1.2, 6))
        gs = GridSpec(1, 1, wspace=0.2, hspace=0.5)
        ax1 = plt.subplot(gs[0, 0])
        ax1.plot(range(self.bins), self.unbound_population, c=self.unbound_clr)
        ax1.plot(range(self.bins), self.bound_population, c=self.bound_clr, ls='--')
        ax1.set_xticks([0, self.bins / 4, self.bins / 2, 3 * self.bins / 4, self.bins])
        ax1.set_xticklabels([r'$-\pi$', r'$-\frac{1}{2}\pi{}$', r'$0$', r'$\frac{1}{2}\pi$', r'$\pi$'])
        ax1.set_xlabel('Dihedral angle (rad)')
        ax1.set_ylabel(r'$p$ (input population)')
        aesthetics.paper_plot(fig, scientific=False)
        if save:
            plt.savefig(filename + '.png', dpi=300, bbox_inches='tight')
            
    def plot_energy(self, save=False, filename=None):
        """
        This function plots the unbound and bound energies (i.e., chemical potentials) associated with a
        simulation object.
        """

        fig = plt.figure(figsize=(6 * 1.2, 6))
        gs = GridSpec(1, 1, wspace=0.2, hspace=0.5)
        ax1 = plt.subplot(gs[0, 0])
        ax1.plot(range(self.bins), self.unbound, c=self.unbound_clr)
        ax1.plot(range(self.bins), self.bound, c=self.bound_clr, ls='--')
        ax1.set_xticks([0, self.bins / 4, self.bins / 2, 3 * self.bins / 4, self.bins])
        ax1.set_xticklabels([r'$-\pi$', r'$-\frac{1}{2}\pi{}$', r'$0$', r'$\frac{1}{2}\pi$', r'$\pi$'])
        ax1.set_xlabel(r'$\theta$ (rad)')
        ax1.set_ylabel(r'$\mu$ (kcal mol$^{-1}$)')
        aesthetics.paper_plot(fig, scientific=False)
        if save:
            plt.savefig(filename + '.png', dpi=300, bbox_inches='tight')

    def plot_ss(self, save=False, filename=None):
        """
        This function plots the nonequilibrium steady-state distribution associated with a simulation object.
        By default, this will plot the eigenvector-derived steady-state distribution.
        """

        fig = plt.figure(figsize=(6 * 1.2, 6))
        gs = GridSpec(1, 1, wspace=0.2, hspace=0.5)
        ax1 = plt.subplot(gs[0, 0])
        ax1.plot(range(self.bins), self.ss[0:self.bins], c=self.unbound_clr)
        ax1.plot(range(self.bins), self.ss[self.bins:2 * self.bins], c=self.bound_clr, ls='--')
        ax1.set_xticks([0, self.bins / 4, self.bins / 2, 3 * self.bins / 4, self.bins])
        ax1.set_xticklabels([r'$-\pi$', r'$-\frac{1}{2}\pi{}$', r'$0$', r'$\frac{1}{2}\pi$', r'$\pi$'])
        ax1.set_xlabel('Dihedral angle (rad)')
        ax1.set_ylabel(r'$p$ (probability)')
        aesthetics.paper_plot(fig, scientific=False)
        if save:
            plt.savefig(filename + '.png', dpi=300, bbox_inches='tight')

    def plot_flux(self, save=False, filename=None):
        """
        This function plots the intrasurface flux separately and as a sum. The intrasurface flux is the directional
        flux. This also prints the simulation parameters.
        """

        print('{:<25} {:<+10.2e} {:<10}'.format('C', self.C_intersurface, 'second**-1'))
        print('{:<25} {:<+10.2e} {:<10}'.format('D', self.D, 'degrees**2 second**-1'))
        print('{:<25} {:<+10.2e} {:<10}'.format('k_{cat}', self.catalytic_rate, 'second**-1'))
        print('{:<25} {:<+10.2e} {:<10}'.format('[S]', self.cSubstrate, 'M'))
        print('{:<25} {:<+10.2e} {:<10}'.format('dt', self.dt, 'second**-1'))
        print('{:<25} {:<10} {:<10}'.format('-----------------', '---------', '---------'))
        print('{:<25} {:<+10.2e} {:<10}'.format('Intrasurface flux', np.mean(self.flux_u + self.flux_b),
                                                'cycle second**-1'))
        print('{:<25} {:<+10.2e} {:<10}'.format('Peak intrasurface flux', np.max(np.hstack((abs(self.flux_u),
                                                                                            abs(self.flux_b)))),
                                                                                            'cycle second**-1'))
        print('{:<25} {:<+10.2e} {:<10}'.format('Intersurface flux', np.mean(self.flux_ub),
                                                'cycle second**-1'))
        if self.load:
            print('{:<25} {:<10} {:<10}'.format('-----------------', '---------', '---------'))
            print('{:<25} {:<+10.2e} {:<10}'.format('Applied load', self.load_slope, 'kcal mol**-1 cycle**-1'))
            print('{:<25} {:<+10.2e} {:<10}'.format('Power', self.load_slope * np.mean(self.flux_u + self.flux_b),
                                                    'kcal mol**-1 second**-1'))
        fig = plt.figure(figsize=(6 * 1.2, 6))
        gs = GridSpec(1, 1, wspace=0.2, hspace=0.5)
        ax1 = plt.subplot(gs[0, 0])
        ax1.plot(range(self.bins), self.flux_u, c=self.unbound_clr, label='U')
        ax1.plot(range(self.bins), self.flux_b, c=self.bound_clr, label='B', ls='--')
        ax1.plot(range(self.bins), self.flux_b + self.flux_u, c='k', label='U+B')
        ax1.yaxis.set_major_formatter(mpl.ticker.ScalarFormatter(useMathText=True, useOffset=False))
        # ax1.set_title(r'{0:0.2f} $\pm$ {1:0.2f} cycle second$^{{-1}}$'.format(np.mean(self.flux_u + self.flux_b),
        #                                                                       np.std(self.flux_u + self.flux_b)))
        ax1.set_xticks([0, self.bins / 4, self.bins / 2, 3 * self.bins / 4, self.bins])
        ax1.set_xticklabels([r'$-\pi$', r'$-\frac{1}{2}\pi{}$', r'$0$', r'$\frac{1}{2}\pi$', r'$\pi$'])
        ax1.set_xlabel(r'$\theta$ (rad)')
        ax1.set_ylabel('Flux $J$ (cycle s$^{-1}$)')
        aesthetics.paper_plot(fig, scientific=False)
        if save:
            plt.savefig(filename + '.png', dpi=300, bbox_inches='tight')

    def plot_intersurface_flux(self, save=False, filename=None):
        """
        This function plots the intersurface flux, this is useful for considering driven, oar-like motion.
        """

        fig = plt.figure(figsize=(6 * 1.2, 6))
        gs = GridSpec(1, 1, wspace=0.2, hspace=0.5)
        ax1 = plt.subplot(gs[0, 0])
        ax1.plot(range(self.bins), self.flux_ub, c='k', label='U+B')
        ax1.yaxis.set_major_formatter(mpl.ticker.ScalarFormatter(useMathText=True, useOffset=False))
        ax1.set_xticks([0, self.bins / 4, self.bins / 2, 3 * self.bins / 4, self.bins])
        ax1.set_xticklabels([r'$-\pi$', r'$-\frac{1}{2}\pi{}$', r'$0$', r'$\frac{1}{2}\pi$', r'$\pi$'])
        ax1.set_xlabel('Dihedral angle (rad)')
        ax1.set_ylabel(r'Flux $J_{0 \leftrightarrow 1}$ (cycle second$^{-1}$)')
        aesthetics.paper_plot(fig, scientific=False)
        if save:
            plt.savefig(filename + '.png', dpi=300, bbox_inches='tight')

    def plot_load(self, save=False, filename=None):
        """
        This function plots the unbound and bound energy surfaces with a constant added load.
        """

        fig = plt.figure(figsize=(6 * 1.2, 6))
        gs = GridSpec(1, 1, wspace=0.2, hspace=0.5)
        ax1 = plt.subplot(gs[0, 0])

        ax1.plot(np.arange(self.bins),
                 [self.unbound[i] + self.load_function(i) for i in np.arange(self.bins)],
                 c='k', ls='--', lw=2)
        ax1.plot(np.arange(self.bins), self.unbound, c=self.unbound_clr)
        ax1.plot(np.arange(self.bins), [self.bound[i] + self.load_function(i) for i in
                                                       np.arange(self.bins)],
                 c='k', ls='--', lw=2)
        ax1.plot(np.arange(self.bins), self.bound, c=self.bound_clr)

        ax1.set_xticks([0, self.bins / 4, self.bins / 2, 3 * self.bins / 4, self.bins])
        ax1.set_xticklabels([r'$-\pi$', r'$-\frac{1}{2}\pi{}$', r'$0$', r'$\frac{1}{2}\pi$', r'$\pi$'])
        ax1.set_xlabel('Dihedral angle (rad)')
        ax1.set_ylabel(r'$\mu$ (kcal mol$^{-1}$)')
        aesthetics.paper_plot(fig, scientific=False)
        if save:
            plt.savefig(filename + '.png', dpi=300, bbox_inches='tight')

    def plot_load_extrapolation(self, save=False, filename=None):
        """
        This function plots the unbound and bound energy surfaces with a constant added load over a larger range
        to check the continuity of the load function is different than the ordinary PBCs on the energy surfaces.
        :return:
        """
        fig = plt.figure(figsize=(6 * 1.2, 6))
        gs = GridSpec(1, 1, wspace=0.2, hspace=0.5)
        ax1 = plt.subplot(gs[0, 0])

        extended_u = np.concatenate((self.unbound, self.unbound, self.unbound))
        extended_b = np.concatenate((self.bound, self.bound, self.bound))

        ax1.plot(np.arange(-1 * self.bins / 2, self.bins + self.bins / 2),
                 [extended_u[i] + self.load_function(i) for i in
                  np.arange(-1 * self.bins / 2, self.bins + self.bins / 2)],
                 c='k', ls='--', lw=2)
        ax1.plot(np.arange(self.bins), self.unbound, c=self.unbound_clr)
        ax1.plot(np.arange(-1 * self.bins / 2, self.bins + self.bins / 2),
                 [extended_b[i] + self.load_function(i) for i in
                  np.arange(-1 * self.bins / 2, self.bins + self.bins / 2)],
                 c='k', ls='--', lw=2)
        ax1.plot(np.arange(self.bins), self.bound, c=self.bound_clr)

        ax1.set_xticks([-1 * self.bins / 2, 0, self.bins / 2, self.bins, self.bins + self.bins / 2])
        ax1.set_xticklabels([r'$-\pi$', '$0$', r'$\pi$', r'$2\pi$', r'$3\pi$'])
        ax1.set_xlabel('Dihedral angle (rad)')
        ax1.set_ylabel(r'$\mu$ (kcal mol$^{-1}$)')
        aesthetics.paper_plot(fig, scientific=False)
        if save:
            plt.savefig(filename + '.png', dpi=300, bbox_inches='tight')

    def data_to_energy(self, histogram):
        """
        This function takes in population histograms from Chris' PKA data and
        (a) smooths them with a Gaussian kernel with width 1;
        (b) eliminates zeros by setting any zero value to the minimum of the data;
        (c) turns the population histograms to energy surfaces.
        """

        histogram_smooth = gaussian_filter(histogram, 1)
        histogram_copy = np.copy(histogram_smooth)
        for i in range(len(histogram)):
            if histogram_smooth[i] != 0:
                histogram_copy[i] = histogram_smooth[i]
            else:
                histogram_copy[i] = min(histogram_smooth[np.nonzero(histogram_smooth)])
        histogram_smooth = histogram_copy
        assert (not np.any(histogram_smooth == 0))
        histogram_smooth = histogram_smooth / np.sum(histogram_smooth)
        energy = -self.kT * np.log(histogram_smooth)
        return energy

    def calculate_boltzmann(self):
        """
        This function calculates the normalized steady state probability density, given populations.
        """
        boltzmann_unbound = np.exp(-1 * np.array(self.unbound) / self.kT)
        boltzmann_bound = np.exp(-1 * np.array(self.bound) / self.kT)
        self.PDF_unbound = boltzmann_unbound / np.sum(boltzmann_unbound)
        self.PDF_bound = boltzmann_bound / np.sum(boltzmann_bound)

    def calculate_intrasurface_rates(self, energy_surface):
        """
        This function calculates intrasurface rates using the energy difference between adjacent bins.
        """

        forward_rates = self.C_intrasurface * np.exp(-1 * np.diff(energy_surface) / float(2 * self.kT))
        backward_rates = self.C_intrasurface * np.exp(+1 * np.diff(energy_surface) / float(2 * self.kT))
        rate_matrix = np.zeros((self.bins, self.bins))
        for i in range(self.bins - 1):
            rate_matrix[i][i + 1] = forward_rates[i]
            rate_matrix[i + 1][i] = backward_rates[i]
        rate_matrix[0][self.bins - 1] = self.C_intrasurface * np.exp(
            -(energy_surface[self.bins - 1] - energy_surface[0]) / float(2 * self.kT))
        rate_matrix[self.bins - 1][0] = self.C_intrasurface * np.exp(
            +(energy_surface[self.bins - 1] - energy_surface[0]) / float(2 * self.kT))
        return rate_matrix

    def calculate_intrasurface_rates_with_load(self, energy_surface):
        """
        This function calculates intrasurface rates using the energy difference between adjacent bins,
        this function is distinct from `calculate_intrasurface_rates` because the load function
        has different boundary conditions than the energy function. The energy function has perfect periodic
        boundary conditions, but the load must continue to decrease or increase across the boundaries.
        """
        surface_with_load = np.hstack(([energy_surface[i] + self.load_function(i) for i in range(self.bins)]))
        # This should handle the interior elements just fine.
        self.forward_rates = self.C_intrasurface * \
                             np.exp(-1 * np.diff(surface_with_load) / float(2 * self.kT))
        self.backward_rates = self.C_intrasurface * \
                              np.exp(+1 * np.diff(surface_with_load) / float(2 * self.kT))
        rate_matrix = np.zeros((self.bins, self.bins))
        
        for i in range(self.bins - 1):
            rate_matrix[i][i + 1] = self.forward_rates[i]
            rate_matrix[i + 1][i] = self.backward_rates[i]

        # But now the PBCs are a little tricky...
        rate_matrix[0][self.bins - 1] = self.C_intrasurface * np.exp(
            -(energy_surface[self.bins - 1] + self.load_function(-1) -
              (energy_surface[0] + self.load_function(0))) / float(2 * self.kT))

        rate_matrix[self.bins - 1][0] = self.C_intrasurface * np.exp(
            +(energy_surface[self.bins - 1] + self.load_function(self.bins - 1) -
              (energy_surface[0] + self.load_function(self.bins))) / float(2 * self.kT))

        return rate_matrix

    def calculate_intersurface_rates(self, unbound_surface, bound_surface):
        """
        This function calculates the intersurface rates in two ways.
        For bound to unbound, the rates are calculated according to the energy difference and the catalytic rate.
        For unbound to bound, the rates depend on the prefactor and the concentration of substrate.
        """

        bu_rm = np.empty((self.bins))
        ub_rm = np.empty((self.bins))
        for i in range(self.bins):
            bu_rm[i] = (self.C_intersurface *
                        np.exp(-1 * (unbound_surface[i] - bound_surface[i]) / float(self.kT)) +
                        self.catalytic_rate)
            ub_rm[i] = self.C_intersurface * self.cSubstrate
        return ub_rm, bu_rm

    def compose_tm(self, u_rm, b_rm, ub_rm, bu_rm):
        """
        We take the four rate matrices (two single surface and two intersurface) and inject them
        into the transition matrix.
        """

        tm = np.zeros((2 * self.bins, 2 * self.bins))
        tm[0:self.bins, 0:self.bins] = u_rm
        tm[self.bins:2 * self.bins, self.bins:2 * self.bins] = b_rm
        for i in range(self.bins):
            tm[i, i + self.bins] = ub_rm[i]
            tm[i + self.bins, i] = bu_rm[i]
        self.tm = self.scale_tm(tm)
        return

    def scale_tm(self, tm):
        """
        The transition matrix is scaled by `dt` so all rows sum to 1 and all elements are less than 1.
        This should not use `self` subobjects, except for `dt` because we are mutating the variables.
        """

        row_sums = tm.sum(axis=1, keepdims=True)
        maximum_row_sum = int(math.log10(max(row_sums)))
        self.dt = 10 ** -(maximum_row_sum + 1)
        tm_scaled = self.dt * tm
        row_sums = tm_scaled.sum(axis=1, keepdims=True)
        if np.any(row_sums > 1):
            print('Row sums unexpectedly greater than 1.')
        for i in range(2 * self.bins):
            tm_scaled[i][i] = 1.0 - row_sums[i]
        return tm_scaled

    def calculate_eigenvector(self):
        """
        The eigenvectors and eigenvalues of the transition matrix are computed and the steady-state population is
        assigned to the eigenvector with an eigenvalue of 1.
        """

        self.eigenvalues, eigenvectors = np.linalg.eig(np.transpose(self.tm))
        ss = abs(eigenvectors[:, self.eigenvalues.argmax()].astype(float))
        self.ss = ss / np.sum(ss)
        return

    def calculate_flux(self, ss, tm):
        """
        This function calculates the intrasurface flux using the steady-state distribution and the transition matrix.
        The steady-state distribution is a parameter so this function can be run with either the eigenvector-derived
        steady-state distribution or the interated steady-state distribution.
        """

        flux_u = np.empty((self.bins))
        flux_b = np.empty((self.bins))
        flux_ub = np.empty((self.bins))
        for i in range(self.bins):
            if i == 0:
                flux_u[i] = -1 * (- ss[i] * tm[i][i + 1] / self.dt + ss[i + 1] * tm[i + 1][i] / self.dt)
            if i == self.bins - 1:
                flux_u[i] = -1 * (- ss[i] * tm[i][0] / self.dt + ss[0] * tm[0][i] / self.dt)
            else:
                flux_u[i] = -1 * (- ss[i] * tm[i][i + 1] / self.dt + ss[i + 1] * tm[i + 1][i] / self.dt)
        for i in range(self.bins, 2 * self.bins):
            if i == self.bins:
                flux_b[i - self.bins] = -1 * (- ss[i] * tm[i][i + 1] / self.dt + ss[i + 1] * tm[i + 1][i] / self.dt)
            if i == 2 * self.bins - 1:
                flux_b[i - self.bins] = -1 * (
                    - ss[i] * tm[i][self.bins] / self.dt + ss[self.bins] * tm[self.bins][i] / self.dt)
            else:
                flux_b[i - self.bins] = -1 * (- ss[i] * tm[i][i + 1] / self.dt + ss[i + 1] * tm[i + 1][i] / self.dt)
        for i in range(self.bins):
            flux_ub[i] = -1 * (
                            - ss[i] * tm[i][i + self.bins] / self.dt + ss[i + self.bins] * tm[i + self.bins][i] / self.dt)
           
        self.flux_u = flux_u
        self.flux_b = flux_b
        self.flux_ub = flux_ub
        return

    def iterate(self, iterations=None):
        """
        A template population distribution is multiplied by the transition matrix.
        By default, iterations are 0. The output of this command is set to
        `self.iterative_ss` which can be passed to `calculate_flux`.
        The new population can be set to a normalized random distribution or the eigenvector-derived
        steady-state distribution.
        """

        print('Running iterative method with {} iterations'.format(self.iterations))
        # Instead of starting with a random population, I'm going to start with a population spike 
        # in the first bin.
        # population = np.random.rand(2 * self.bins)

        def gaussian(x, mu, sig):
            return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

        def calculate_msd(population, mu):
            msd = []
            for position in range(2 * self.bins):
                msd.append(population[position] * ((position - mu) * (360 / self.bins)) ** 2)
            return np.sum(msd)

        population = np.zeros((2 * self.bins))
        population = np.array([gaussian(i, self.bins / 2, 2) for i in range(2 * self.bins)])
        row_sums = population.sum(axis=0, keepdims=True)
        population = population / row_sums
        # Now, keep track of the center of mass of the population.
        self.iterative_com = []
        self.iterative_com.append(sc.ndimage.measurements.center_of_mass(population))
        fig = plt.figure(figsize=(6 * 1.2, 6))
        gs = GridSpec(1, 1, wspace=0.2, hspace=0.5)
        ax1 = plt.subplot(gs[0, 0])

        ax1.plot(range(self.bins), population[0:self.bins], c='k', alpha=1)

        new_population = np.copy(population)
        self.msd = np.empty((self.iterations + 1))
        self.msd[0] = calculate_msd(population, self.bins / 2)

        for i in range(self.iterations):
            new_population = np.dot(new_population, self.tm)
            self.msd[i + 1] = calculate_msd(new_population, self.bins / 2)
            print('MSD = {}'.format(self.msd[i]))
            ax1.plot(range(self.bins), new_population[0:self.bins], c=self.unbound_clr, alpha=0.1)
            self.iterative_com.append(sc.ndimage.measurements.center_of_mass(new_population))
        self.iterative_ss = new_population
        ax1.set_xticklabels(['$0$', r'$\frac{1}{2}\pi{}$', r'$\pi$', r'$\frac{3}{2}\pi$', r'$2\pi$'])
        ax1.set_xlabel('Dihedral angle (rad)')
        ax1.set_ylabel('Population')
        aesthetics.paper_plot(fig, scientific=False)
        return

    def simulate(self, plot=False, user_energies=False, catalysis=True):
        """
        Now this function takes in a file(name) and determins the energy surfaces automatically,
        so I don't forget to do it in an interactive session.
        This function runs the `simulation` which involves:
        (a) setting the unbound intrasurface rates,
        (b) setting the bound intrasurface rates,
        (c) setting the intersurface rates,
        (d) composing the transition matrix,
        (e) calculating the eigenvectors of the transition matrix,
        (f) calculating the intrasurface flux,
        and optionally (g) running an interative method to determine the steady-state distribution.
        """
        if self.data_source == 'pka_md_data':
            self.dir = '../../md-data/pka-md-data'
            try:
                self.unbound_population = np.genfromtxt(self.dir + '/apo/' + self.name +
                                                        '_chi_pop_hist_targ.txt',
                                                        delimiter=',',
                                                        skip_header=1)
                self.bound_population = np.genfromtxt(self.dir + '/atpmg/' + self.name +
                                                      '_chi_pop_hist_ref.txt',
                                                      delimiter=',',
                                                      skip_header=1)
            except IOError:
                print('Cannot read {} from {}.'.format(self.name, self.dir))
            cmap = sns.color_palette("Paired", 10)
            self.unbound_clr = cmap[6]
            self.bound_clr = cmap[7]

        elif self.data_source == 'pka_reversed':
            self.dir = '../../md-data/pka-md-reversed-and-averaged'
            try:
                self.unbound_population = np.genfromtxt(self.dir + '/apo/' + self.name +
                                                        '_chi_pop_hist_targ.txt',
                                                        delimiter=',',
                                                        skip_header=1)
                self.bound_population = np.genfromtxt(self.dir + '/atpmg/' + self.name +
                                                    '_chi_pop_hist_ref.txt',
                                                    delimiter=',',
                                                    skip_header=1)

            except IOError:
                print('Cannot read {} from {}.'.format(self.name, self.dir))

            cmap = sns.color_palette("Paired", 10)
            self.unbound_clr = cmap[6]
            self.bound_clr = cmap[7]

        elif self.data_source == 'adk_md_data':
            self.dir = '../../md-data/adenylate-kinase'
            try:
                self.unbound_population = np.genfromtxt(self.dir + '/AdKDihedHist_apo-4ake/' +
                                                        self.name + '.dat',
                                                        delimiter=' ',
                                                        skip_header=1,
                                                        usecols=1)
                self.bound_population = np.genfromtxt(self.dir + '/AdKDihedHist_ap5-3hpq/' +
                                                      self.name + '.dat',
                                                      delimiter=' ',
                                                      skip_header=1,
                                                      usecols=1)

            except IOError:
                print('Cannot read {} from {}.'.format(self.name, self.dir))

            cmap = sns.color_palette("Paired", 10)
            # self.unbound_clr = cmap[0]
            self.unbound_clr = cmap[3]
            self.bound_clr = cmap[1]

        elif self.data_source == 'hiv_md_data':
            self.dir = '../../md-data/hiv-protease'
            try:
                self.unbound_population = np.genfromtxt(self.dir + '/1hhp_apo/' +
                                                        self.name + '.dat',
                                                        delimiter=' ',
                                                        skip_header=1,
                                                        usecols=1)
                self.bound_population = np.genfromtxt(self.dir + '/1kjf_p1p6/' +
                                                      self.name + '.dat',
                                                      delimiter=' ',
                                                      skip_header=1,
                                                      usecols=1)

            except IOError:
                print('Cannot read {} from {}.'.format(self.name, self.dir))

            cmap = sns.color_palette("Paired", 10)
            self.unbound_clr = cmap[2]
            self.bound_clr = cmap[3]

        elif self.data_source == 'manual':
            # Populations are supplied manually.
            cmap = sns.color_palette("Paired", 10)
            self.unbound_clr = cmap[8]
            self.bound_clr = cmap[9]
            pass
        else:
            print('No populations.')
        if user_energies:
            pass
        else:
            self.unbound = self.data_to_energy(self.unbound_population)
            self.bound = self.data_to_energy(self.bound_population) - self.offset_factor

        self.bins = len(self.unbound)
        self.tm = np.zeros((self.bins, self.bins))
        self.C_intrasurface = self.D / (360. / self.bins) ** 2  # per degree per second

        if not self.load:
            u_rm = self.calculate_intrasurface_rates(self.unbound)
            b_rm = self.calculate_intrasurface_rates(self.bound)
        if self.load:
            u_rm = self.calculate_intrasurface_rates_with_load(self.unbound)
            b_rm = self.calculate_intrasurface_rates_with_load(self.bound)

        ub_rm, bu_rm = self.calculate_intersurface_rates(self.unbound, self.bound)
        self.compose_tm(u_rm, b_rm, ub_rm, bu_rm)
        self.calculate_eigenvector()
        self.calculate_boltzmann()
        self.calculate_flux(self.ss, self.tm)
        if plot:
            self.plot_input()
            if not self.load:
                self.plot_energy()
            else:
                self.plot_load()
            self.plot_ss()
            self.plot_flux()
            self.plot_intersurface_flux()
        if self.iterations != 0:
            self.iterate(self.iterations)
            self.calculate_flux(self.iterative_ss, self.tm)
            if plot:
                self.plot_flux()
        return

    def load_function(self, x):
        return x * self.load_slope / self.bins


