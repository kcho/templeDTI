import os
import re
import shutil

skeletonDirectory = 'fa_collection/skeleton_images'

def main():
    prepare_images()



def prepare_images():
    skeletonList = [x for x in os.listdir(skeletonDirectory) \
            if x.startswith('diff') \
            or x.startswith('new_diff')]

    numberOfControls = 17
    controlCheck = 0
    meditationCheck = 0


    B_minus_A_controls=[]
    A_minus_B_controls=[]
    B_minus_A_meditation=[]
    A_minus_B_meditation=[]

    for skeleton in skeletonList:
        num = re.search('\d{4}',skeleton).group()

        if int(num) < numberOfControls * 2:
            group = "controls"
            if skeleton.startswith('diff'):
                B_minus_A_controls.append(skeleton)
                calc = "post_minus_pre"
            else:
                A_minus_B_controls.append(skeleton)
                calc = "pre_minus_post"
        else:
            group = "meditation"
            if skeleton.startswith('diff'):
                B_minus_A_meditation.append(skeleton)
                calc = "post_minus_pre"
            else:
                A_minus_B_meditation.append(skeleton)
                calc = "pre_minus_post"


    command_B_minus_A_controls = 'fslmerge -t {location}/{output} {inputs}'.format(
            location = skeletonDirectory,
            output = 'controls_post_minus_pre',
            inputs = ' '.join(
                [skeletonDirectory+'/'+x for x \
                        in B_minus_A_controls]))

    command_A_minus_B_controls = 'fslmerge -t {location}/{output} {inputs}'.format(
            location = skeletonDirectory,
            output = 'controls_pre_minus_post',
            inputs = ' '.join(
                [skeletonDirectory+'/'+x for x \
                        in A_minus_B_controls]))


    command_B_minus_A_meditation = 'fslmerge -t {location}/{output} {inputs}'.format(
            location = skeletonDirectory,
            output = 'meditation_post_minus_pre',
            inputs = ' '.join(
                [skeletonDirectory+'/'+x for x \
                        in B_minus_A_meditation]))

    command_A_minus_B_meditation = 'fslmerge -t {location}/{output} {inputs}'.format(
            location = skeletonDirectory,
            output = 'meditation_pre_minus_post',
            inputs = ' '.join(
                [skeletonDirectory+'/'+x for x \
                        in A_minus_B_meditation]))

    commands = ([command_B_minus_A_controls,
        command_A_minus_B_controls,
        command_B_minus_A_meditation,
        command_A_minus_B_meditation])

    for command in commands:
        print command
        os.popen(command).read()




if __name__=='__main__':
    main()

