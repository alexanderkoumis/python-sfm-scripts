#!/usr/bin/python

# Usage:
# python ./run-openmvg.py <path_to_binaries> <path_to_dataset> <output_path>

import os          # path.join
import sys         # argv
import subprocess  # check_call

def binary_name(bin_dir, bin_name):
    name = os.path.join(bin_dir, bin_name)
    if not os.path.isfile(name):
        print 'Error! ' + name + ' is not a valid binary!'
        exit(1)
    return name

def make_bins(bin_dir):
    bins = {}
    bin_names = ['openMVG_main_CreateList',  'openMVG_main_computeMatches',
                 'openMVG_main_IncrementalSfM']
    for bin_name in bin_names:
        bins[bin_name] = os.path.join(bin_dir, bin_name)
    return bins

def make_out_dirs(out_dir):
    out_dirs = {}
    out_subdirs = ['images', 'matches', 'outReconstruction']
    # out_pmvs_subdirs = ['visualize', 'txt', 'models']

    if os.path.isdir(out_dir):
        warning_str = 'Warning! ' + out_dir + ' is already a directory! ' + \
                      'Overwrite? (\'n\' will halt script) [y]/n: '
        while True:
            user_input = raw_input(warning_str).lower()
            if user_input == 'y' or user_input == '':
                shutil.rmtree(out_dir)
                break
            elif user_input == 'n':
                exit(0)

    os.makedirs(out_dir)
    for out_subdir in out_subdirs:
        full_out_dir = os.path.join(out_dir, out_subdir)
        out_dirs[out_subdir] = full_out_dir
        os.makedirs(full_out_dir)

    # out_pmvs_dir = out_dirs['pmvs']
    # for out_pmvs_subdir in out_pmvs_subdirs:
    #     full_out_pmvs_subdir = os.path.join(out_pmvs_dir, out_pmvs_subdir)
    #     out_dirs[out_pmvs_subdir] = full_out_pmvs_subdir
    #     os.makedirs(full_out_pmvs_subdir)
    return out_dirs

def main():
    # grabbing command line arguments
    argv = sys.argv
    bin_dir = argv[1]
    img_dir = argv[2]
    data_dir = argv[3]

    bins = make_bins(bin_dir)
    out_dirs = make_out_dirs(out_dir)

    # session subdirectories
    image_dir = os.path.join(data_dir, 'images')
    matches_dir = os.path.join(data_dir, 'matches')
    outreconstruction_dir = os.path.join(data_dir, 'outReconstruction')
    pmvs_dir = os.path.join(data_dir, 'pmvs')

    # pmvs subdirectories
    models_dir = os.path.join(pmvs_dir, 'models')
    txt_dir = os.path.join(pmvs_dir, 'txt')
    vis_dir = os.path.join(pmvs_dir, 'visualize')


    # data file names
    list_txt = os.path.join(matches_dir, 'list.txt')
    matches_f_txt = os.path.join(matches_dir, 'matches.f.txt')

    # shell commands
    createlist_cmd = ' '.join([openMVG_main_CreateList, '-i', image_dir, '-o', matches_dir, '-f 1400'])
    computematches_cmd = ' '.join([openMVG_main_computeMatches, '-i', image_dir, '-o', matches_dir, '-g f'])

    subprocess.check_call(createlist_cmd, shell=True)
    subprocess.check_call(computematches_cmd, shell=True)






if __name__ == "__main__":
    main()