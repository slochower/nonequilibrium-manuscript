import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from mpl_toolkits.axes_grid1 import make_axes_locatable
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


def autolabel(rects):
    ''' Put labels on top of rectangles. '''
    for rect in rects:
        height = rect.get_height()
        i = rects.index(rect)
        plt.text(rect.get_x() + rect.get_width() / 2., 1.05 * height, '{:.4f} $\pm$ {:.4f}'.format(height, sems[i]),
                 ha='center', va='bottom')


def adjust_spines(ax, spines, plot_margin=0):
    ''' Inspired by Tufte-like axis limits. '''
    for loc, spine in ax.spines.items():
        if loc in spines:
            spine.set_position(('outward', 10))  # outward by 10 points
            spine.set_smart_bounds(True)
        else:
            spine.set_color('none')  # don't draw spine

    # turn off ticks where there is no spine
    if 'left' in spines:
        ax.yaxis.set_ticks_position('left')
    else:
        # no yaxis ticks
        ax.yaxis.set_ticks([])

    if 'bottom' in spines:
        ax.xaxis.set_ticks_position('bottom')
    else:
        # no xaxis ticks
        ax.xaxis.set_ticks([])

    x0, x1, y0, y1 = ax.axis()
    ax.axis((x0 - plot_margin,
             x1 + plot_margin,
             y0 - plot_margin,
             y1 + plot_margin))


def white_out(fig, facecolor='white'):
    ''' Make a white background on graphs, for better copy-paste functionality to Powerpoint.'''
    # See http://stackoverflow.com/questions/24542610/matplotlib-figure-facecolor-alpha-while-saving-background-color-transparency
    from matplotlib.colors import colorConverter
    if facecolor is False:
        # Not all graphs get color-coding
        facecolor = fig.get_facecolor()
        alpha = 1
    else:
        alpha = 0.5
    color_with_alpha = colorConverter.to_rgba(facecolor, alpha)
    fig.patch.set_facecolor(color_with_alpha)


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


def plot_scan(ax, xx, yy, zz, xlabel, ylabel, title, xlog=True, ylog=True, trip=False):
    ''' Plot a 2D parameter scan with x, y, and z values.'''

    if ylog == True:
        ax.set_yscale('log')
    if xlog == True:
        ax.set_xscale('log')
    ax.margins(x=0, y=0)
    cmap = mpl.cm.jet
    zz = np.array(zz)
    if ylog == True:
        im = ax.pcolor(xx, yy, zz,
                       norm=LogNorm(vmin=zz.min(), vmax=zz.max()),
                       cmap=cmap)
    elif trip == False:
        im = ax.pcolor(xx, yy, zz,
                       cmap=cmap)
    if trip:
        im = ax.tripcolor(xx, yy, zz,
                          cmap=cmap)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="10%", pad=0.05)
    cbar = plt.colorbar(im, cax=cax)
    ax.set_title(title, y=1.05)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    # pretty_label(ax)
    # plt.show()


def pretty_plot(fig, adjustment=0, scientific=True):
    sns.set()
    sns.set_context("notebook", font_scale=1.5, rc={"lines.linewidth": 2.5})
    sns.set_style("white")
    mpl.rc('text', usetex=True)
    mpl.rcParams['text.latex.preamble'] = [
        r'\usepackage{amsmath}',
        r'\usepackage{helvet}',
        r'\usepackage{sansmath}',
        r'\sansmath',
        r'\renewcommand{\familydefault}{\sfdefault}',
        r'\usepackage[T1]{fontenc}',
        r'\usepackage{graphicx}',
        # r'\usepackage{upgreek}',
    ]
    for ax in fig.axes:
        ax.tick_params(which='major', direction='out', length=10)
        ax.tick_params(which='minor', direction='out', length=5)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.xaxis.labelpad = 10
        ax.yaxis.labelpad = 10
        white_out(fig)
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
        r'\usepackage{relsize}',
        r'\newcommand{\bigpi}{\scalebox{5}{\ensuremath{\pi}}}'
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
        white_out(fig)
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