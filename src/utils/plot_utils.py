import matplotlib.pyplot as plt
import os
from distutils.dir_util import copy_tree
import seaborn as sns
import numpy as np


def save_plots(file_name, subfolder=None, extensions=None, copy_to_paper=False):
    if extensions is None or "pdf" not in extensions:
        extensions = ['pdf', 'png']
    for extension in extensions:
        file_name_new = file_name + '.' + extension
        print("new file name: ", file_name_new)
        if subfolder is None:
            src_file_name = str(os.getcwd()) + '/../../plots/' + extension + '/' + file_name_new
        else:
            src_file_name = str(os.getcwd()) + '/../../plots/' + extension + '/' + subfolder + '/' + file_name_new
        print(src_file_name)
        plt.tight_layout()
        plt.savefig(src_file_name, bbox_inches='tight')

def set_paper_style():
    sns.set(style="white")
    # plt.subplots(figsize=(22, 12))
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.size'] = 24
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['ps.fonttype'] = 42
    plt.rcParams['axes.labelsize'] = 38
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titlesize'] = 15
    plt.rcParams['axes.linewidth'] = 3
    plt.rcParams['xtick.labelsize'] = 38
    plt.rcParams['ytick.labelsize'] = 38
    plt.rcParams['legend.fontsize'] = 26
    plt.rcParams['figure.titlesize'] = 28
    plt.rcParams['lines.linewidth'] = 5.0
    plt.rcParams.update({'figure.max_open_warning': 0})
    plt.rcParams['ps.useafm'] = True
    plt.rcParams['pdf.use14corefonts'] = True


def plot_figure(x1_vals, y1_vals, x2_vals, y2_vals,
                label_1, label_2,
                file_name,
                x3_vals=None, y3_vals=None,
                xlabel= None, ylabel= None, title= None,
                label_3=None,
                color_1='blue', color_2='green',
                color_3='orange',
                extensions=None, subfolder=None,
                copy_to_paper=False):
    set_paper_style()
    #  Plotting the data with the first y-axis
    fig, ax1 = plt.subplots(figsize=(12, 6))
    # Plot average listing prices
    ax1.plot(x1_vals, y1_vals, marker='o', label=label_1, color=color_1)
    # Plotting the data with the second y-axis
    ax1.plot(x2_vals, y2_vals, marker='o', label=label_2, color=color_2)
    if x3_vals is not None and y3_vals is not None:
        # Plotting the data with the third y-axis
        ax1.plot(x3_vals, y3_vals, marker='o', label=label_3, color=color_3)

    # Adding labels and title for the first y-axis
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax1.set_title(title)
    # ax1.legend(loc="lower center")
    # ax1.grid(True)
    N = len(x1_vals)
    x2 = list(range(1,N+1))
    plt.xticks(x2, x1_vals)

    # Rotate x-axis labels by 45 degrees
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')

    save_plots(file_name, subfolder, extensions, copy_to_paper)

