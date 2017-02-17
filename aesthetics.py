import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import colorConverter
import seaborn as sns
import numpy as np

def update_label(old_label, exponent_text):
    if exponent_text == "":
        return old_label
    try:
        units = old_label[old_label.index("(") + 1:old_label.rindex(")")]
    except ValueError:
        units = ""
    label = old_label.replace("({})".format(units), "")
    exponent_text = exponent_text.replace("$\\times$", "")
    return "{} ({} {})".format(label, exponent_text, units)


def pretty_label(ax, axis='both'):
    ''' Format the label string with the exponent from the ScalarFormatter '''
    try:
        ax.xaxis
    except:
        ax = plt.gca()

    ax.ticklabel_format(axis=axis, style='sci')
    axes_instances = []
    if axis in ['x', 'both']:
        axes_instances.append(ax.xaxis)
    if axis in ['y', 'both']:
        axes_instances.append(ax.yaxis)
    for ax in axes_instances:
        ax.major.formatter._useMathText = True
        plt.draw()  # Update the text
        exponent_text = ax.get_offset_text().get_text()
        label = ax.get_label().get_text()
        ax.offsetText.set_visible(False)
        ax.set_label_text(update_label(label, exponent_text))


def paper_plot(fig, adjustment=0, scientific=False):
    sns.set()
    # Increase font size
    sns.set_context("notebook", font_scale=2, rc={"lines.linewidth": 5})
    sns.set_style("white")
    mpl.rc('text', usetex=True)
    mpl.rcParams['text.latex.preamble'] = [
        r'\usepackage{amsmath}',
        r'\usepackage{helvet}',
        r'\usepackage[EULERGREEK]{sansmath}',
        r'\sansmath',
        r'\renewcommand{\familydefault}{\sfdefault}',
        r'\usepackage[T1]{fontenc}',
        r'\usepackage{graphicx}',
        r'\usepackage{relsize}'
        ]

    for ax in fig.axes:
        # Increase padding
        ax.tick_params(which='major', direction='out', length=10, pad=10)
        ax.tick_params(which='minor', direction='out', length=5)
        # If plotting with pi, increase the x tick size specifically
        # ax.tick_params(axis='x', labelsize=40, pad=-10)
        # Increase tick thickness
        ax.xaxis.set_tick_params(width=2)
        ax.yaxis.set_tick_params(width=2)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        # Increase padding
        ax.xaxis.labelpad = 15
        ax.yaxis.labelpad = 15
        # Make the background color white
        facecolor = 'white'
        if facecolor is False:
            facecolor = fig.get_facecolor()
        alpha = 1
        color_with_alpha = colorConverter.to_rgba(facecolor, alpha)
        fig.patch.set_facecolor(color_with_alpha)
        # Stick the scientific notation into the axis label, instead of the 
        # default position which in the corner, which really makes no sense.
        if ax.xaxis.get_scale() == 'linear':
            if scientific:
                pretty_label(ax)
            ax.get_xaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.get_yaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
        elif ax.xaxis.get_scale() == 'log':
            pass
        # For scatter plots, where points get cut off
        if adjustment != 0:
            x0, x1, y0, y1 = ax.axis()
            ax.xaxis((x0 - adjustment,
                    x1 + adjustment,
                    ))
        # Make axes thicker
        for axis in ['top','bottom','left','right']:
            ax.spines[axis].set_linewidth(2)

def generic_plot(x, y, xlabel=None, ylabel=None, scientific=False, c=None):
    fig = plt.figure(figsize=(6 * 1.2, 6))
    gs = GridSpec(1, 1, wspace=0.2, hspace=0.5)
    ax = plt.subplot(gs[0, 0])
    if c:
        ax.plot(x, y, 'o', markersize=10, markeredgecolor='k', markeredgewidth=0.8, alpha=0.5, mfc=c)
    else:
        ax.plot(x, y, 'o', markersize=10, markeredgecolor='k', markeredgewidth=0.8, alpha=0.5, mfc='b')
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if scientific:
        pretty_label(ax)
    ax.margins(None)
    paper_plot(fig)
    return ax