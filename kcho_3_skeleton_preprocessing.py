#!/ccnc_bin/venv/bin/python

import os
import re
import shutil

skeltDir = 'skeleton_images'
splitDir = skeltDir+'/splitSkeleton'
preDir = splitDir+'/pre'
postDir = splitDir+'/post'
post_m_preDir = splitDir+'/post_m_pre'
pre_m_postDir = splitDir+'/pre_m_post'

def main():
    print os.getcwd()
    makeDirectory(skeltDir)
    if 'all_FA_skeletonised.nii.gz' not in os.listdir(skeltDir):
        print '-'*10,'copying all_FA_skeletonised','-'*10
        shutil.copy('stats/all_FA_skeletonised.nii.gz',skeltDir)
    makeDirectory(splitDir)
    makeDirectory(postDir)
    makeDirectory(preDir)
    makeDirectory(post_m_preDir)
    makeDirectory(pre_m_postDir)

    if 'skeleton0091' not in os.listdir(splitDir) and \
            'pre_0091.nii.gz' not in os.listdir(postDir):
        print '-'*10,'spliting all_FA_skeletonised','-'*10
        os.system('fslsplit {0}/all_FA_skeletonised.nii.gz {1}/skeleton -t'.format(
            skeltDir,splitDir))

    skeletonList = [x for x in os.listdir(splitDir) if x.startswith('skeleton')]
    print '-'*10,'pre-post all_FA_skeletonised','-'*10


    for skeleton in skeletonList:
        num = re.search('\d{4}',skeleton).group()
        if int(num)%2 == 0:
            #post comes first alphabetically
            shutil.move(os.path.join(splitDir,skeleton),
                        postDir+'/post_'+num+'.nii.gz')
        else:
            shutil.move(os.path.join(splitDir,skeleton),
                        preDir+'/pre_'+num+'.nii.gz')

    for preImg, postImg in zip(os.listdir(preDir),os.listdir(postDir)):
        print preImg, postImg
        preNum = int(re.search('\d{4}',preImg).group())
        postNum = int(re.search('\d{4}',postImg).group())

        command1 = 'fslmaths {pre} -sub {post} {pre_m_post}'.format(
                    pre=preDir+'/'+preImg,
                    post=postDir+'/'+postImg,
                    pre_m_post= pre_m_postDir + \
                            '/pre_minus_post_' + \
                            str(postNum) + '_' + str(preNum))
        print command1

        command2 = 'fslmaths {post} -sub {pre} {post_m_pre}'.format(
                    pre=preDir+'/'+preImg,
                    post=postDir+'/'+postImg,
                    post_m_pre= post_m_preDir + \
                            '/post_minus_pre_' + \
                            str(postNum) + '_' + str(preNum))
        print command2

        #os.popen(command1).read()
        #os.popen(command2).read()


    post_m_pre_imgs= [x for x in os.listdir(post_m_preDir)]
    pre_m_post_imgs = [x for x in os.listdir(pre_m_postDir)]

    command3 =  'fslmerge -t {location}/{output} {inputs}'.format(
            location = post_m_preDir,
            output = 'post_minus_pre_merged',
            inputs = ' '.join([post_m_preDir+'/'+x for x in post_m_pre_imgs]))

    command4 =  'fslmerge -t {location}/{output} {inputs}'.format(
            location = pre_m_postDir,
            output = 'pre_minus_post_merged',
            inputs = ' '.join([pre_m_postDir+'/'+x for x in pre_m_post_imgs]))

    print command3
    os.popen(command3).read()
    print command4
    os.popen(command4).read()

def makeDirectory(directory):
    try:
        os.mkdir(directory)
    except:
        pass

if __name__=='__main__':
    main()






#cd fa_collection
#mkdir subj_diff

#for i in origdata/*post*
#do
    #subjName=`echo ${i} | awk -F '_' '{print $1}'`
    #subjName=$(basename "$subjName")
    #subjName="${subjName%.*}"
    #subjName="${subjName%.*}"
    #echo $subjName

    #fslmaths FA/${subjName}_pre_FA_to_target.nii.gz \
        #-sub FA/${subjName}_post_FA_to_target.nii.gz \
        #subj_diff/${subjName}_diff

#done


#cd subj_diff
#arr=( $(ls) )
#fslmerge -t pre_minus_post ${arr[@]}

#version II
#mkdir fa_collection/skeleton_images
#cp fa_collection/stats/all_FA_skeletonised.nii.gz \
    #fa_collection/skeleton_images
#cd fa_collection/skeleton_images
##fslsplit all_FA_skeletonised.nii.gz skeleton -t


#arr=( $(ls skeleton*) )
#for i in ${arr[@]}
#do
    #num=`echo ${i} | awk -F 'skeleton' '{print $2}'`
    #num=`echo ${num} | awk -F '.' '{print $1}'`
    #echo ${i}
    #if [ $((num%2)) -eq 0 ]
    #then
        #echo even
    #else
        #echo odd
    #fi
#done
