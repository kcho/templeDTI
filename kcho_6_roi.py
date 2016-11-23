#!/home/kangik/anaconda2/bin/python

import os
import re
import shutil
import argparse
from os.path import join
import textwrap
import nibabel as nb
from multiprocessing import Pool
import pandas as pd


def main(args):

    if lower(args.template) != 'mni':
        ROIdir = join(args.dir, 'ROIs_template_reg')
    else:
        ROIdir = join(args.roidir)

    mergedMap = join(args.dir, 'stats', 'all_{0}.nii.gz'.format(args.measure))
    splitDir = join(args.dir, '{0}_registered'.format(args.measure))

    makeDirectory(splitDir)
    if 'all_{measure}.nii.gz'.format(measure=args.measure) not in os.listdir(splitDir):
        print '-'*10,'copying all_{0}'.format(args.measure),'-'*10
        shutil.copy(mergedMap, splitDir)

    if 'split0091' not in os.listdir(splitDir):
        copied_mergedMap = join(splitDir, os.path.basename(mergedMap))
        print '-'*10,'spliting all_{0}_skeletonised'.format(args.measure),'-'*10
        os.system('fslsplit {0} {1}/split -t'.format(
            copied_mergedMap, splitDir))

        # Name change
        mapList = [x for x in os.listdir(splitDir) if x.startswith('split')]
        nameList = [x for x in os.listdir(join(args.dir, 'origdata')) if x.endswith('nii.gz')]

        mapList.sort()
        nameList.sort()

        print '-'*10,'Changing names of the split fies','-'*10
        for i,j in zip(mapList, nameList):
            shutil.move(join(splitDir, i), join(splitDir, j))

    subjectImgs = [x for x in os.listdir(splitDir) if not x.startswith('all')]
    roiList = [x for x in os.listdir(ROIdir) if x.endswith('nii.gz')]

    #pool = Pool(processes = args.core)
    pool = Pool()

    inputs = []
    for subjectImg in subjectImgs:
        for roiImg in roiList:
            inputs.append((join(splitDir, subjectImg), join(ROIdir, roiImg)))

    
    print '-'*10,'Calculating mean values ...','-'*10
    data =  pool.map(get_mean_values, inputs)

    df = pd.DataFrame(data, columns = ['subject','roi','mean {0}'.format(args.measure)])


    df = df.pivot_table(values='mean {0}'.format(args.measure), 
                       index='subject',
                       columns='roi')

    df = df.sort_index()
    df['timeline'] = df.index.str.split('_').str[1]
    df.index = df.index.str.split('_').str[0]

    cols = df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df = df[cols]
    df.to_csv('Template_specific_ROI_{0}.csv'.format(args.measure))
    newDf = df.reset_index()
    newDf = newDf.groupby(['index','timeline']).mean().unstack('timeline')
    newDf.to_csv('Template_specific_ROI_{0}_rearranged.csv'.format(args.measure))

    print '-'*10,'Completed','-'*10


def get_mean_values(img_and_mask_tup):
    img = img_and_mask_tup[0]
    mask = img_and_mask_tup[1]

    imgName = os.path.basename(img).split('.')[0]
    maskName = os.path.basename(mask).split('.')[0]

    img_data = nb.load(img).get_data()
    mask_data = nb.load(mask).get_data()

    img_masked = img_data[mask_data>0]
    return (imgName, maskName, img_masked.mean())


def makeDirectory(directory):
    try:
        os.mkdir(directory)
    except:
        pass


def makeROIs(roiDirectory):
    fslDir=os.environ['FSLDIR']
    fslAtlasesDir = join(fslDir, 'data', 'atlases')
    JHU_label_1mm = join(fslAtlasesDir, 'JHU', 'JHU-ICBM-labels-1mm.nii.gz')
    JHU_label_1mm_nb = nb.load(JHU_label_1mm)
    JHU_label_1mm_data = JHU_label_1mm_nb.get_data()
    JHU_label_xml = join(fslAtlasesDir, 'JHU-labels.xml')

    with open(JHU_label_xml, 'r') as f:
        lines = f.readlines()
    searchedLines = [re.search('index="(\d+)".*>([A-Za-z \(\)\/-]+)<',x) for x in lines]
    layer_num_name = dict([(x.group(1), x.group(2)) for x in searchedLines if x!=None])


    for roiNum in range(1, JHU_label_1mm_data.max()):
        roiName = re.sub('[^A-Za-z0-9\- ]+', '_', layer_num_name[str(roiNum)])
        re.sub('[^A-Za-z0-9]+', '', mystring)
        mask_data = JHU_label_1mm_data[JHU_label_1mm_data == roiNum]
        nb.Nifti1Image(mask_data, JHU_label_1mm_nb.affine).to_filename(join(roiDirectory,
                                                                            roiName))

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
        '-r', '--roidir',
        help='ROI directory location, default="ROIs"',
        default=os.getcwd()+'/ROIs')
    parser.add_argument(
        '-m', '--measure',
        help='"FA", "AD", "MD" or "RD"',
        default="FA")
    parser.add_argument(
        '-c', '--core',
        help='Number of cores to use',
        default=8)
    parser.add_argument(
        '-t', '--template',
        help='Template image, "MNI" or "others"',
        default='MNI')
    args = parser.parse_args()

    if not args.dir:
        parser.print_help()
    else:
        main(args)
