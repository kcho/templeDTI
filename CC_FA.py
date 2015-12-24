import pandas as pd
import numpy
import os
import seaborn as sns
import nibabel as nib
import matplotlib
from nilearn import plotting, image
import nipype.interfaces.freesurfer as fs
import nipype.interfaces.fsl as fsl
from nipype import Node, MapNode, Workflow
import nipype.interfaces.utility as util     # utility
import nipype.interfaces.io as nio           # Data i/o



def main():

    freesurferLoc = '/Volumes/CCNC_3T_2/kcho/temple/freesurfer'
    dtiLoc = '/Volumes/CCNC_3T_2/kcho/temple/preprocessed/preprocessedData/'
    subjectDirs = [x for x in os.listdir(freesurferLoc) if x.endswith('pre') or \
                                                           x.endswith('post')]

    roiDict = {'CC_Posterior':251,
                'CC_Mid_Posterior':252,
                'CC_Central':253,
                'CC_Mid_Anterior':254,
                'CC_Anterior':255}

    for subject in subjectDirs:
        print subject

        subjectLoc = os.path.join(freesurferLoc, subject)
        nodifBrain = os.path.join(dtiLoc,subject,'hifi_nodif_brain.nii.gz')
        fsBrainLoc = os.path.join(subjectLoc, 'mri', 'brain.mgz')
        fsBrainLocNii = fsBrainLoc[:-4]+'.nii.gz'
        asegLoc = os.path.join(subjectLoc,
                               'mri','aseg.mgz')
        fs2dtiMat = os.path.join(subjectLoc, 'fs2dti.mat')
        
        
        

        convert = fs.MRIConvert(in_file=fsBrainLoc,
                                out_type='niigz',
                                out_file=fsBrainLocNii)
        if not os.path.isfile(fsBrainLocNii):
            convert.run()

        flirt = fsl.FLIRT(in_file = fsBrainLocNii,
                reference = nodifBrain,
                interp = 'nearestneighbour',
                out_matrix_file = fs2dtiMat)

        if not os.path.isfile(fs2dtiMat):
            flirt.run()


        for roi, roiNum in roiDict.iteritems():
            roiLoc = os.path.join(subjectLoc,roi+'.nii.gz')
            roiLocReg = os.path.join(subjectLoc,roi+'_reg.nii.gz')
            fa_mean = os.path.join(subjectLoc, roi+'_FA.txt')

            binarize = fs.Binarize(in_file = asegLoc,
                    match = [roiNum],
                    binary_file = roiLoc)
            if not os.path.isfile(roiLoc):
                binarize.run()

            applyReg = fsl.ApplyXfm(in_file = roiLoc,
                    reference = nodifBrain,
                    in_matrix_file = fs2dtiMat,
                    interp = 'nearestneighbour',
                    out_file = roiLocReg)

            if not os.path.isfile(roiLocReg):
                applyReg.run()
            else:
                applyReg.run()



            faFile = os.path.join(dtiLoc,subject, 'dti_FA.nii.gz')
            faStamp = fsl.ImageStats(op_string = '-k {mask} -M'.format(mask = roiLocReg),
                    #mask_file = roiLocReg,
                    in_file = faFile,)
            print faStamp.cmdline
        

            stats = faStamp.run()
            print stats.outputs




    #roiList = ['CC_Posterior.nii.gz':, 
                #'CC_Mid_Posterior.nii.gz', 
                #'CC_Central.nii.gz', 
                #'CC_Mid_Anterior.nii.gz',
                #'CC_Anterior.nii.gz']


    #info = dict(nodif_brain=[['subject_id', 'hifi_nodif_brain.nii.gz']],
                #reference_T1=[['subject_id', 'brain.mgz']],
                #aseg=[['subject_id', 'aseg.mgz']]
               #)



    #preproc = Workflow(name='preproc')




    #inputnode = Node(interface = util.IdentityInterface(fields=['subject_id']),
                    #name='infosource')
    #inputnode.iterables = ('subject_id', subjectDirs[:2])
    

    #maskNode = Node(interface = util.IdentityInterface(fields=['mask']),
                    #name='infosource')
    #maskNode.iterables = ('mask', roiDict.values())

    #datasink = Node(nio.DataSink(), name='sinker')
    #datasink.inputs.base_directory = '/Volumes/CCNC_3T_2/kcho/temple/final'


    #datasource = Node(interface=nio.DataGrabber(infields = [('subject_id')],
                                                #outfields= list(info.keys())),
                      #name='datasource')
    #datasource.inputs.template="%s/%s"


    #datasource.inputs.base_directory = os.path.abspath('/Volumes/CCNC_3T_2/kcho/temple/preprocessed/preprocessedData/')

    #datasource.inputs.field_template = dict(nodif_brain='%s/%s',
                                            #reference_T1="/Volumes/CCNC_3T_2/kcho/temple/freesurfer/%s/mri/%s",
                                            #aseg="/Volumes/CCNC_3T_2/kcho/temple/freesurfer/%s/mri/%s")

    #datasource.inputs.template_args = info
    #datasource.inputs.sort_filelist = True





    #binarize = Node(interface = fs.Binarize(), name='roiExtraction')


    #print roiDict.values()
    #preproc.connect(inputnode, 'subject_id', datasource, 'subject_id')
    #preproc.connect(maskNode, 'mask', binarize, 'match')
    #preproc.connect(datasource, 'aseg', binarize, 'in_file')

    #preproc.run()



    ##reg = Workflow(name='reg')

    ##mc = Node(fs.MRIConvert(out_type='niigz'), name='convert')
    ##flt = Node(fsl.FLIRT(),'registration')

    ##reg.connect(mc, 'out_file', flt, 'in_file')


    ##applyReg = Workflow(name='applyReg')
    ##applyflt = Node(fsl.ApplyXfm(), name='apply_reg')

    ##applyReg.connect(reg, 'flt.out_file', applyflt, 'reference')
    ##applyReg.connect(preproc, 'binarize.out_file', applyflt, 'in_file')



    




    ##wf.connect([
            ##(infosource, datasource, [('subject_id', 'subject_id')]),
            ##(infosource, datasink, [('subject_id', 'container')]),
            ##(datasource, mc, [('reference_T1', 'in_file')]),
            ##(mc, flt, [("out_file", "reference")]),
            ##(datasource, flt, [("nodif_brain", "in_file")]),
            ##(flt, applyflt, [("out_matrix_file", "in_matrix_file")]),
            ##(datasource, applyflt, [("masks", "in_file")]),
            ##(mc, applyflt, [("out_file", "reference")]),
            ##(applyflt, datasink, [("out_file", "regCC")])
            ###(datasource, applyflt, [("masks", "in_file")])
        ##])




    ##infosource = Node(interface=util.IdentityInterface(fields=['subject_id']),
                         ##name="infosource")


    ##infosource.iterables = ('subject_id', subjectDirs[:2])

    ##datasink = Node(nio.DataSink(), name='sinker')
    ##datasink.inputs.base_directory = '/Volumes/CCNC_3T_2/kcho/temple/final'


    ##datasource = Node(interface=nio.DataGrabber(infields = [('subject_id')],
                                                ##outfields= list(info.keys())),
                      ##name='datasource')

    ##datasource.inputs.template="%s/%s"


    ##datasource.inputs.base_directory = os.path.abspath('/Volumes/CCNC_3T_2/kcho/temple/preprocessed/preprocessedData/')
    ##datasource.inputs.field_template = dict(nodif_brain='%s/%s',
                                            ##reference_T1="/Volumes/CCNC_3T_2/kcho/temple/freesurfer/%s/mri/%s",
                                            ##masks="/Volumes/CCNC_3T_2/kcho/temple/freesurfer/%s/%s")
    ##datasource.inputs.template_args = info
    ##datasource.inputs.sort_filelist = True


    ###---------------------------------------------------------------------------------

    ##mc = Node(fs.MRIConvert(out_type='niigz'), name='convert')
    ##flt = Node(fsl.FLIRT(),'registration')

    ###applyflt = MapNode(fsl.ApplyXfm(), name='apply_reg', iterfield = ['in_file', 'n'])
    ###applyflt.inputs.in_file = [os.path.join(freesurferLoc,x) for x in roiList]
    ###applyflt.n = [1,2,3,4,5]

    ##applyflt = Node(fsl.ApplyXfm(), name='apply_reg')
    ###applyflt.iterables = ("in_file", roiList)

    ### make work flow
    ##wf = Workflow(name="freesurfer_ROI_to_diffusion")

    ##wf.connect([
            ##(infosource, datasource, [('subject_id', 'subject_id')]),
            ##(infosource, datasink, [('subject_id', 'container')]),
            ##(datasource, mc, [('reference_T1', 'in_file')]),
            ##(mc, flt, [("out_file", "reference")]),
            ##(datasource, flt, [("nodif_brain", "in_file")]),
            ##(flt, applyflt, [("out_matrix_file", "in_matrix_file")]),
            ##(datasource, applyflt, [("masks", "in_file")]),
            ##(mc, applyflt, [("out_file", "reference")]),
            ##(applyflt, datasink, [("out_file", "regCC")])
            ###(datasource, applyflt, [("masks", "in_file")])
        ##])

    ###reg = Workflow(name="registration")

    ###reg.connect([
            ###(infosource, datasource, [(('subject_id','masks'), ('subject_id','masks'))]),
            ###(datasource, applyflt, [("masks", "in_file")])
        ###])

    ##wf.run()



if __name__ == "__main__":
    main()
