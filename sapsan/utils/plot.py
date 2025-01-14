'''
Plotting routines

You can adjust the style to your liking by changing 
params = {} in plot_params()

-pikarpov
'''

from logging import warning
from typing import List, Optional

import matplotlib.pyplot as plt
import matplotlib as mpl
import plotly.express as px
import pandas as pd
import numpy as np
import warnings

from scipy.stats import ks_2samp
from scipy.interpolate import interp1d
import sapsan.utils.hiddenlayer as hl

def plot_params():
    params = {'font.size': 14, 'legend.fontsize': 14, 
              'axes.labelsize': 20, 'axes.titlesize':24,
              'xtick.labelsize': 17,'ytick.labelsize': 17,
              'axes.linewidth': 1, 'patch.linewidth': 3, 'lines.linewidth': 3,
              'xtick.major.width': 1,'ytick.major.width': 1,
              'xtick.minor.width': 1,'ytick.minor.width': 1,
              'xtick.major.size': 4,'ytick.major.size': 4,
              'xtick.minor.size': 3,'ytick.minor.size': 3,
              'axes.formatter.limits' : [-7, 7], 'text.usetex': False}
    return params


def pdf_plot(series: List[np.ndarray], 
             bins: int = 100, 
             names: Optional[List[str]] = None, 
             figsize = (6,6),
             ax = None):
    """ PDF plot

    @param series: series of numpy arrays to build a pdf plot from
    @param bins: number of bins
    @param names: name of series in case of multiseries plot
    @return: pyplot object
    """
    mpl.rcParams.update(plot_params())
    if ax==None: 
        fig = plt.figure(figsize = figsize)
        ax = fig.add_subplot(111)                

    if not names:
        names = ["Data {}".format(i) for i in range(len(series))]

    for idx, data in enumerate(series):
        ax.hist(data.flatten(), bins=bins, density=True, histtype='step', label=names[idx])

    #ax.ticklabel_format(axis='both', style='sci', scilimits=(-2,2)) 
    ax.legend(loc=1)
    ax.set_yscale("log")
    ax.set_xlabel("Values")
    ax.set_ylabel("PDF")
    plt.tight_layout()

    return ax


def cdf_plot(series: List[np.ndarray], 
             names: Optional[List[str]] = None, 
             figsize = (6,6),
             ax = None):
    """ CDF plot

    @param series: series of numpy arrays to build a cdf plot
    @param names: name of series in case of multiseries plot
    @return: pyplot object
    """
    mpl.rcParams.update(plot_params())
    if ax==None: 
        fig = plt.figure(figsize = figsize)
        ax = fig.add_subplot(111)

    if not names:
        names = ["Data {}".format(i) for i in range(len(series))]

    func = []
    val = np.zeros((len(series),np.prod(np.shape(series[0]))))
    for idx, data in enumerate(series):
        val[idx] = np.sort(data.flatten())

        #cdf calculation via linear interpolation
        length = len(val[idx])
        yvals = np.linspace(0,length-1, length)/length
        ax.plot(val[idx], yvals, label=names[idx])
        func.append(interp1d(val[idx], yvals))  

        if idx==1:
            ks_stat, pvalue = ks_2samp(val[0], val[1])
            minima = max([min(val[0]), min(val[1])])
            maxima = min([max(val[0]), max(val[1])])

            xtest = np.linspace(minima, maxima, length*10)
            D = abs(func[0](xtest)-func[1](xtest))
            Dmax = max(D)
            Dpos = xtest[np.argmax(D)]
            ax.axvline(x=Dpos, linewidth=1, color='tab:red', linestyle='--')

            txt = ('pvalue = %.3e\n'%pvalue+
                     r'$\rm ks_{stat}$'+' = %.3e\n'%ks_stat+
                     #r'$\rm ks_{line}$'+' = %.3e\n'%Dmax+
                     r'$\rm line_{pos}$'+' = %.3e'%Dpos)

            ax.text(0.05, 0.55, txt, transform=ax.transAxes, fontsize=14)        

    #ax.ticklabel_format(axis='both', style='sci', scilimits=(-2,2)) 
    ax.legend()
    ax.set_xlabel('Values')
    ax.set_ylabel('CDF')
    plt.tight_layout()
    
    return ax


def slice_plot(series: List[np.ndarray], 
               names: Optional[List[str]] = None, 
               cmap = 'plasma',
               figsize = (16,6)):
    mpl.rcParams.update(plot_params())
    if not names:
        names = ["Data {}".format(i) for i in range(len(series))]
    
    #colormap range is based on the target slice
    vmin = np.amin(series[-1])
    vmax = np.amax(series[-1])
    
    fig = plt.figure(figsize = figsize)
    for idx, data in enumerate(series):
        ax = fig.add_subplot(121+idx)
        im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax = vmax)
        plt.colorbar(im).ax.tick_params(labelsize=14)
        ax.set_title(names[idx])
    plt.tight_layout()
    
    return ax


def line_plot(series: List[np.ndarray], 
              names: Optional[List[str]] = None, 
              plot_type = 'plot',
              figsize = (6,6),
              ax = None):
    mpl.rcParams.update(plot_params())
    if not names:
        names = ["Data {}".format(i) for i in range(len(series))]
        
    if ax==None: 
        fig = plt.figure(figsize = figsize)
        ax = fig.add_subplot(111)
        
    for idx, data in enumerate(series):
        if plot_type == 'plot': ax.plot(data[0], data[1], label = names[idx])
        elif plot_type == 'semilogx': ax.semilogx(data[0], data[1], label = names[idx])
        elif plot_type == 'semilogy': ax.semilogy(data[0], data[1], label = names[idx])
        elif plot_type == 'loglog': ax.loglog(data[0], data[1], label = names[idx])
            
    ax.legend(loc=0)
    plt.tight_layout()
    
    return ax

        
def log_plot(show_log = True, log_path = 'logs/logs/train.csv'):#log.txt'):
    
    plot_data = {'epoch':[], 'train_loss':[]}

    data = np.genfromtxt(log_path, delimiter=',', 
                      skip_header=1, dtype=np.float32)
    
    if len(data.shape)==1: data = np.array([data])

    plot_data['epoch'] = data[:, 0]
    plot_data['train_loss'] = data[:, 1]

    df = pd.DataFrame(plot_data)

    if len(plot_data['epoch']) == 1:
        plotting_routine = px.scatter
    else:
        plotting_routine = px.line
        
    if any(i<0 for i in plot_data['train_loss']): log_y=False
    else: log_y = True
        
    fig = plotting_routine(df, x="epoch", y="train_loss", log_y=log_y,
                  title='Training Progress', width=700, height=400)
    fig.update_layout(yaxis=dict(exponentformat='e'))
    fig.layout.hovermode = 'x' 

    if show_log: fig.show()

    return fig

    
def model_graph(model, shape: np.array, transforms = None):
    import torch
    
    if len(np.shape(shape)) != 1: raise ValueError("Error: please provide the 'shape', "
                                                   "not the input data array itself.")    
    
    if transforms == None:
        transforms = [
                        hl.transforms.Fold("Conv > MaxPool > Relu", "ConvPoolRelu"),
                        hl.transforms.Fold("Conv > MaxPool", "ConvPool"),    
                        hl.transforms.Prune("Shape"),
                        hl.transforms.Prune("Constant"),
                        hl.transforms.Prune("Gather"),
                        hl.transforms.Prune("Unsqueeze"),
                        hl.transforms.Prune("Concat"),
                        hl.transforms.Rename("Cast", to="Input"),
                        hl.transforms.FoldDuplicates()
                     ]

    shape = np.array(shape)
    if shape[1] != 1:
        shape[1] = 1
        warnings.warn("shape was changed to %s to draw a model graph."%str(shape))
    
    if len(shape) == 5: unit_input = torch.zeros(tuple(shape))
    elif len(shape) == 4: unit_input = torch.zeros(tuple(shape))
    else: raise ValueError('Input shape can be either of 2D or 3D data')
        
    graph = hl.build_graph(model, unit_input, transforms = transforms)
    graph.theme = hl.graph.THEMES["blue"].copy()
    
    return graph
    
    
class PlotUtils(object):
    @classmethod
    def plot_histograms(cls):
        pass

    @classmethod
    def plot_pdf(cls, data):
        return pdf_plot(data)
    
    @classmethod
    def plot_cdf(cls, data):
        return cdf_plot(data)

    @classmethod
    def plot_slice(cls, data):
        return slice_plot(data)
    
    @classmethod
    def plot_log(cls, data):
        return log_plot(data)

