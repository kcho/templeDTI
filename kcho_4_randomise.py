#!/ccnc_bin/venv/bin/python
import os
import re
import argparse
import textwrap
import difflib


def main(args):
    dataDir  = args.dir
    skeletonDirectory = os.path.join(dataDir,
            'skeleton_images_'+args.measure,
            'splitSkeleton',
            'post_m_pre')

    design_con='''/NumWaves 2
/NumContrasts 2
/PPheights 1 1
/Matrix
1 -1
-1 1
'''

    subjectOrigFiles = [x for x in os.listdir(dataDir+'/origdata') if x.endswith('nii.gz')]
    groups = list(set([x[:3] for x in subjectOrigFiles]))
    groups.sort()

    # divided by two because it's longitudinal design
    subjectNum = len(subjectOrigFiles) / 2
    firstGroupNum = len([x for x in subjectOrigFiles if x.startswith(groups[0])]) / 2
    secondGroupNum = len([x for x in subjectOrigFiles if x.startswith(groups[1])]) / 2

    design_mat='''/NumWaves 2
/NumPoints {subjectNum}
/PPheights 1 1
/Matrix
{firstGroupMat}{secondGroupMat}'''.format(subjectNum=subjectNum,
                                        firstGroupMat = '1 0\n'*firstGroupNum,
                                        secondGroupMat = '0 1\n'*secondGroupNum)

    if os.path.isfile(skeletonDirectory+'/design.con'):
        print skeletonDirectory+'/design.con exists ! Please remove or rename design.con'
    else:
        with open(skeletonDirectory+'/design.con','w') as f:
            f.write(design_con)
        with open(skeletonDirectory+'/design.mat','w') as f:
            f.write(design_mat)

    command='randomise \
-i {skeletonDirectory}/post_minus_pre_merged.nii.gz \
-o {skeletonDirectory}/tbss_post_m_pre \
-m {dataDir}/stats/mean_FA_skeleton_mask \
-d {skeletonDirectory}/design.mat \
-t {skeletonDirectory}/design.con \
-n 5000 \
--T2'.format(skeletonDirectory=skeletonDirectory, dataDir = dataDir)

    print command
    os.system(command)

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
