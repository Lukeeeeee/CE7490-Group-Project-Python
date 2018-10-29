import numpy as np
import matplotlib
from pylab import rcParams

# matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
import json
import sys
import math as M
from scipy.interpolate import interp1d
from itertools import groupby
import seaborn as sns
import os
import glob

sns.set_style('ticks')


class Plotter(object):
    markers = ('+', 'x', 'v', 'o', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X')
    color_list = ['b', 'r', 'g', 'c', 'm', 'y', 'k', 'cyan', 'plum', 'darkgreen', 'darkorange', 'oldlace', 'chocolate',
                  'purple', 'lightskyblue', 'gray', 'seagreen', 'antiquewhite',
                  'snow', 'darkviolet', 'brown', 'skyblue', 'mediumaquamarine', 'midnightblue', 'darkturquoise',
                  'sienna', 'lightsteelblue', 'gold', 'teal', 'blueviolet', 'mistyrose', 'seashell', 'goldenrod',
                  'forestgreen', 'aquamarine', 'linen', 'deeppink', 'darkslategray', 'mediumseagreen', 'dimgray',
                  'mediumpurple', 'lightgray', 'khaki', 'dodgerblue', 'papayawhip', 'salmon', 'floralwhite',
                  'lightpink', 'gainsboro', 'coral', 'indigo', 'darksalmon', 'royalblue', 'navy', 'orangered',
                  'cadetblue', 'orchid', 'palegreen', 'magenta', 'honeydew', 'darkgray', 'palegoldenrod', 'springgreen',
                  'lawngreen', 'palevioletred', 'olive', 'red', 'lime', 'yellowgreen', 'aliceblue', 'orange',
                  'chartreuse', 'lavender', 'paleturquoise', 'blue', 'azure', 'yellow', 'aqua', 'mediumspringgreen',
                  'cornsilk', 'lightblue', 'steelblue', 'violet', 'sandybrown', 'wheat', 'greenyellow', 'darkred',
                  'mediumslateblue', 'lightseagreen', 'darkblue', 'moccasin', 'lightyellow', 'turquoise', 'tan',
                  'mediumvioletred', 'mediumturquoise', 'limegreen', 'slategray', 'lightslategray', 'mintcream',
                  'darkgreen', 'white', 'mediumorchid', 'firebrick', 'bisque', 'darkcyan', 'ghostwhite', 'powderblue',
                  'tomato', 'lavenderblush', 'darkorchid', 'cornflowerblue', 'plum', 'ivory', 'darkgoldenrod', 'green',
                  'burlywood', 'hotpink', 'cyan', 'silver', 'peru', 'thistle', 'indianred', 'olivedrab',
                  'lightgoldenrodyellow', 'maroon', 'black', 'crimson', 'darkolivegreen', 'lightgreen', 'darkseagreen',
                  'lightcyan', 'saddlebrown', 'deepskyblue', 'slateblue', 'whitesmoke', 'pink', 'darkmagenta',
                  'darkkhaki', 'mediumblue', 'beige', 'blanchedalmond', 'lightsalmon', 'lemonchiffon', 'navajowhite',
                  'darkslateblue', 'lightcoral', 'rosybrown', 'fuchsia', 'peachpuff']

    def __init__(self, log_path):
        self.log_path = log_path
        self.color_list = Plotter.color_list

        self.markers = Plotter.markers

    def plot_fig(self, fig_num, col_id, x, y, title, x_lable, y_label, label=' ', marker='*', save_path=None,
                 save_name='res'):
        rcParams['figure.figsize'] = 4, 3
        rcParams['figure.figsize'] = 8, 6
        sns.set_style("darkgrid")
        plt.figure(fig_num)
        plt.title(title)
        plt.xlabel(x_lable)
        plt.ylabel(y_label)
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))

        marker_every = max(int(len(x) / 10), 1)
        if len(np.array(y).shape) > 1:
            new_shape = np.array(y).shape

            res = np.reshape(np.reshape(np.array([y]), newshape=[-1]), newshape=[new_shape[1], new_shape[0]],
                             order='F').tolist()
            res = list(res)
            for i in range(len(res)):
                res_i = res[i]
                plt.subplot(len(res), 1, i + 1)
                plt.title(title + '_' + str(i))
                ax, = plt.plot(x, res_i, self.color_list[col_id], label=label + '_' + str(i), marker=marker,
                               markevery=marker_every, markersize=6, linewidth=1)
                col_id += 1
        else:
            ax, = plt.plot(x, y, self.color_list[col_id], label=label, marker=marker, markevery=marker_every,
                           markersize=6,
                           linewidth=1)
        if save_path:
            plt.savefig(save_path + save_name + '.pdf')
            plt.savefig(save_path + save_name + '.png')
        else:
            plt.savefig(self.log_path + save_name + '.pdf')
            plt.savefig(self.log_path + save_name + '.png')
        plt.legend()
        plt.show()


if __name__ == '__main__':
    # Plotter utility for visualization
    p = Plotter(log_path='.')
    p.plot_fig(fig_num=1,
               x=list(range(5)),
               y=list(range(5)),
               col_id=1,
               title='test',
               x_lable='x',
               y_label='y',
               label='label',
               marker=p.markers[5],
               save_path='./',
               save_name='test')
