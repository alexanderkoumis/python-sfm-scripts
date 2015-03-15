# Usage:
# python ./run-bundler.py <path_to_binaries> <path_to_dataset> <output_path>

import sys        # argv
import os         # getcwd, chdir, path.join, path.isfile
import shutil     # copy, rmtree
import subprocess # check_call


def binary_name(bin_dir, bin_name):
    name = os.path.join(bin_dir, bin_name)
    if not os.path.isfile(name):
        print 'Error! ' + name + ' is not a valid binary!'
        exit(1)
    return name

def make_bins(bin_dir):
    bins = {}
    bin_names = ['sift',  'KeyMatchFull', 'bundler', 'Bundle2Vis',
                 'Bundle2PMVS', 'RadialUndistort']
    for bin_name in bin_names:
        bins[bin_name] = os.path.join(bin_dir, bin_name)
    return bins

def make_out_dirs(out_dir):
    out_dirs = {}
    out_subdirs = ['images', 'matches', 'bundle', 'pmvs']
    if os.path.isdir(out_dir):
        warning_str = 'Warning! ' + out_dir + ' is already a directory! ' + \
                      'Overwrite? (\'n\' will halt script) [y]/n: '
        while True:
            user_input = raw_input(warning_str).lower()
            if user_input == 'y' || user_input == '':
                shutil.rmtree(out_dir)
                break
            elif user_input == 'n':
                exit(0)
    os.makedirs(out_dir)
    for out_subdir in out_subdirs:
        full_out_dir = os.path.join(out_dir, out_subdir)
        out_dirs[out_subdir] = full_out_dir
        os.makedirs(full_out_dir)
    return out_dirs

def make_src_img_list(img_dir):
    min_imgs = 4;
    src_img_list = [os.path.join(img_dir, img) for img in os.listdir(img_dir) \
                if img.endswith('.jpg')]
    if (len(src_img_list) < min_imgs):
        print 'Need more images (Limit currently at ' + str(min_imgs) + '.' + \
              'See script line 37.'
        exit(1)
    return src_img_list

def prepare_imgs(src_list, dst_list, out_img_dir, out_matches_dir):
    n = 0
    dst_imgs = []
    img_list_file = open(dst_list, 'w')
    print 'Copying/Converting images...'
    for src_img in src_list:
        img_prefix = str(n).zfill(8)
        full_dst_img_prefix = os.path.join(out_img_dir, img_prefix)
        dst_img_jpg = full_dst_img_prefix + '.jpg'
        dst_img_pgm = full_dst_img_prefix + '.pgm'
        dst_img_key = full_dst_img_prefix + '.key'
        dst_imgs.append({
            'jpg': dst_img_jpg,
            'pgm': dst_img_pgm,
            'key': dst_img_key
        })
        shutil.copyfile(src_img, dst_img_jpg)
        img_list_file.write(dst_img_jpg + '\n')
        convert_cmd = 'convert ' + dst_img_jpg + ' ' + dst_img_pgm
        subprocess.check_call(convert_cmd, shell=True)
        n += 1
    img_list_file.close
    return dst_imgs

def run_sift(sift_bin, key_list, out_imgs):
    key_list_file = open(key_list, 'w')
    for out_img in out_imgs:
        out_img_pgm = out_img['pgm']
        out_img_key = out_img['key']
        sift_cmd = sift_bin + ' <' + out_img_pgm + '>' + out_img_key
        subprocess.check_call(sift_cmd, shell=True)
        key_list_file.write(out_img_key + '\n')
        print 'Wrote key file ' + out_img_key
    key_list_file.close()
    return key_list

def run_keymatcher(keymatch_bin, matches, key_list):
    keymatch_cmd = keymatch_bin + ' ' + key_list + ' ' + matches
    subprocess.check_call(keymatch_cmd, shell=True)
    print 'Wrote matches to ' + matches

def run_bundler(bundler_bin, dst_img_list, matches, bundle_dir):
    bundler_cmd = ' '.join([
        bundler_bin, dst_img_list, '--match_table', matches, '--output',
        'bundle.out', '--output_dir', bundle_dir, '--init_focal_length',
        str(1400), '--variable_focal_length', '--run_bundle'
    ])
    orig_wd = os.getcwd()
    os.chdir(bundle_dir)
    subprocess.check_call(bundler_cmd, shell=True)
    os.chdir(orig_wd)

def export_bundler(bins, img_list, out_dir, out_dirs):
    bundle_out = os.path.join(out_dirs['bundle'], 'bundle.out')
    bundle_rd_out = os.path.join(out_dirs['pmvs'], 'bundle.rd.out')
    vis_dat = os.path.join(out_dirs['pmvs'], 'vis.dat')

    shared_args = img_list + ' ' + bundle_out + ' pmvs/'
    bundle2pmvs_cmd = bins['Bundle2PMVS'] + ' ' + shared_args
    radialundistort_cmd = bins['RadialUndistort'] + ' ' + shared_args
    bundle2vis_cmd = bins['Bundle2Vis'] + ' ' + bundle_rd_out + ' ' + vis_dat
    
    os.chdir(out_dir)

    subprocess.check_call(bundle2pmvs_cmd, shell=True)
    subprocess.check_call(radialundistort_cmd, shell=True)
    subprocess.check_call(bundle2vis_cmd, shell=True)

def main():

    bin_dir = sys.argv[1]
    img_dir = sys.argv[2]
    out_dir = sys.argv[3]

    bins = make_bins(bin_dir)
    src_img_list = make_src_img_list(img_dir)
    out_dirs = make_out_dirs(out_dir)

    dst_img_list = os.path.join(out_dirs['matches'], 'img_list.txt')
    key_list = os.path.join(out_dirs['matches'], 'key_list.txt')
    matches = os.path.join(out_dirs['matches'], 'matches.txt')

    out_imgs = prepare_imgs(src_img_list, dst_img_list, out_dirs['images'],
                            out_dirs['matches'])

    run_sift(bins['sift'], key_list, out_imgs)
    run_keymatcher(bins['KeyMatchFull'], matches, key_list)
    run_bundler(bins['bundler'], dst_img_list, matches, out_dirs['bundle'])
    export_bundler(bins, dst_img_list, out_dir, out_dirs)

#    convert_jpg_to_pgm(img_list)

    # bundler_cmd = ' '.join([bundler, list_txt, '--match_table', matches_f_txt, '--output', bundle_out, "--output_dir", bundle_dir, '--init_focal_length', str(1400), '--variable_focal_length', '--run_bundle'])

    # subprocess.check_call(bundler_cmd, shell=True)


if __name__ == "__main__":
    main()