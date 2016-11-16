#!/ccnc_bin/venv/bin/python
import os
import re

skeletonDirectories = [
    'skeleton_images/splitSkeleton/post_m_pre',
    'skeleton_images/splitSkeleton/pre_m_post']

def main():
    for skeletonDirectory in skeletonDirectories:
        design_con='''/NumWaves 2
    /NumContrasts 2
    /PPheights 1 1
    /Matrix
    1 -1
    -1 1
    '''
        design_mat='''/NumWaves 2
    /NumPoints 46
    /PPheights 1 1
    /Matrix
    {0}{1}'''.format('1 0\n'*17,'0 1\n'*29)


        with open(skeletonDirectory+'/design.con','w') as f:
            f.write(design_con)
        with open(skeletonDirectory+'/design.mat','w') as f:
            f.write(design_mat)


    command='randomise \
            -i {skeletonDirectory}/pre_minus_post_merged.nii.gz \
            -o {skeletonDirectory}/tbss_pre_m_post \
            -m fa_collection/stats/mean_FA_skeleton_mask \
            -d {skeletonDirectory}/design.mat \
            -t {skeletonDirectory}/design.con \
            -n 5000 \
            --T2'.format(skeletonDirectory=skeletonDirectories[1])

    os.system(command)

    command='randomise \
            -i {skeletonDirectory}/post_minus_pre_merged.nii.gz \
            -o {skeletonDirectory}/tbss_post_m_pre \
            -m fa_collection/stats/mean_FA_skeleton_mask \
            -d {skeletonDirectory}/design.mat \
            -t {skeletonDirectory}/design.con \
            -n 5000 \
            --T2'.format(skeletonDirectory=skeletonDirectories[0])

    os.system(command)


if __name__=='__main__':
    main()
