"""
visualization.py : Visualize fuzzy control systems.
"""
from __future__ import print_function, division

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from ..fuzzymath.fuzzy_ops import interp_membership


class FuzzyVariableVisualizer(object):
    """
    Visualize a fuzzy variable and its membership functions.

    Parameters
    ----------
    fuzzy_var : FuzzyVariable or Term
        Fuzzy variable to be plotted.

    Returns
    -------
    figure : matplotlib Figure
        Figure object containing the visualization.
    """

    def __init__(self, fuzzy_var):
        """
        Initialize the fuzzy variable plot.

        Parameters
        ----------
        fuzzy_var : FuzzyVariable or Term to plot
        """
        from .fuzzyvariable import FuzzyVariable, Term

        assert (isinstance(fuzzy_var, FuzzyVariable) or
                isinstance(fuzzy_var, Term))

        # self.term allows us to know if this is a Term quickly, later
        self.term = None
        if isinstance(fuzzy_var, Term):
            self.term = fuzzy_var.label
            self.fuzzy_var = fuzzy_var.parent_variable
        else:
            self.fuzzy_var = fuzzy_var

        self.fig, self.ax = plt.subplots()
        self.plots = {}

    def view(self, sim=None, *args, **kwargs):
        """
        Visualize this variable and its membership functions with Matplotlib.

        The current output membership function will be shown in bold.
        """
        from .controlsystem import (CrispValueCalculator, ControlSystem,
                                    ControlSystemSimulation)

        if sim is None:
            # Create an empty simulation so we can view with default values
            sim = ControlSystemSimulation(ControlSystem())

        self._init_plot()

        crispy = CrispValueCalculator(self.fuzzy_var, sim)
        output_mf, cut_mfs = crispy.find_memberships()

        # Plot the output membership functions
        cut_plots = {}
        zeros = np.zeros_like(self.fuzzy_var.universe, dtype=np.float64)

        for label, mf_plot in self.plots.items():
            # Only attempt to plot those with cuts
            if label in cut_mfs:
                # Harmonize color between mf plots and filled overlays
                color = mf_plot[0].get_color()
                cut_plots[label] = self.ax.fill_between(
                    self.fuzzy_var.universe, zeros, cut_mfs[label],
                    facecolor=color, alpha=0.4)

        # Plot crisp value if available
        if len(cut_mfs) > 0 and not all(output_mf == 0):
            crisp_value = None
            if hasattr(self.fuzzy_var, 'input'):
                crisp_value = self.fuzzy_var.input[sim]
            elif hasattr(self.fuzzy_var, 'output'):
                crisp_value = self.fuzzy_var.output[sim]

            if crisp_value is not None:
                y = interp_membership(self.fuzzy_var.universe,
                                      output_mf, crisp_value)
                # Small values are hard to see, so simply set them to 1 so
                #  we can see them
                if y < 0.1:
                    y = 1.
                self.ax.plot([crisp_value] * 2, [0, y],
                             color='k', lw=3, label='crisp value')

        return self.fig, self.ax

    def _init_plot(self):
        # Formatting: limits
        self.ax.set_ylim([0, 1.01])
        self.ax.set_xlim([self.fuzzy_var.universe.min(),
                          self.fuzzy_var.universe.max()])

        # Make the plots
        for key, term in self.fuzzy_var.terms.items():
            # If this is a Term, bold the active mf
            lw = 1
            if self.term == key:
                lw = 3

            self.plots[key] = self.ax.plot(self.fuzzy_var.universe,
                                           term.mf,
                                           label=key,
                                           linewidth=lw)

        # Place legend in upper left
        self.ax.legend(framealpha=0.5)

        # Turn off top/right axes
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.get_xaxis().tick_bottom()
        self.ax.get_yaxis().tick_left()

        # Ticks outside the axes
        self.ax.tick_params(direction='out')

        # Label the axes
        self.ax.set_ylabel('Membership')
        self.ax.set_xlabel(self.fuzzy_var.label)


class ControlSystemVisualizer(object):

    def __init__(self, control_system):
        """

        Parameters
        ----------
        control_system : ControlSystem

        Returns
        -------

        """
        self.ctrl = control_system

        self.fig, self.ax = plt.subplots()

    def view(self):
        nx.draw(self.ctrl.graph, ax=self.ax)
        return self.fig
