#!/ccnc_bin/venv/bin/python

import os
import re
import shutil
import argparse
from os.path import join
import textwrap
import nibabel as nb


def main(args):
    ROIdir = join(args.dir, 'ROIs')
    mergedMap = join(args.dir, 'stats', 'all_{0}.nii.gz'.format(args.measure))
    splitDir = join(args.dir, 'FA_registered')

    makeDirectory(splitDir)
    if 'all_{measure}_skeletonised.nii.gz'.format(measure=args.measure) not in os.listdir(splitDir):
        print '-'*10,'copying all_{0}_skeletonised'.format(args.measure),'-'*10
        shutil.copy(allFa, splitDir)

    if 'split0091' not in os.listdir(splitDir):
        copied_mergedMap = join(splitdir, os.path.basename(mergedMap))
        print '-'*10,'spliting all_{0}_skeletonised'.format(args.measure),'-'*10
        os.system('fslsplit {0} {1}/split -t'.format(
            copied_mergedMap, splitDir))

    mapList = [x for x in os.listdir(splitDir) if x.startswith('split')]
    roiList = [x for x in os.listdir(ROIdir) if x.endswith('nii.gz')]

def get_mean_values(img, mask):
    img_data = nb.load(img).get_data()
    mask_data = nb.load(mask).get_data()

    img_masked = img_data[mask_data>0]
    return img_masked.mean()


def makeDirectory(directory):
    try:
        os.mkdir(directory)
    except:
        pass

def check():
    class args:
        def __init__(self):
            self.dir = '.'
            self.measure = 'FA'

    
    main(args)

if __name__=='__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            {codeName} : Preprocess skeleton images for longitudinal design TBSS
            ========================================
            eg) {codeName} -s /Users/kevin/TBSS
                where there are 'stats' and 'FA' directories.
            '''.format(codeName=os.path.basename(__file__))))
    parser.add_argument(
        '-d', '--dir',
        help='Data directory location, default=pwd',
        default=os.getcwd())
    parser.add_argument(
        '-m', '--measure',
        help='"FA", "AD", "MD" or "RD"',
        default="FA")
    args = parser.parse_args()

    if not args.dir:
        parser.print_help()
    else:
        main(args)
