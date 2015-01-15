arr=( $(find /Volumes/promise/CCNC_SNU_temple_2014/2_data -iname 'dti_FA.nii.gz') )

for i in ${arr[@]}
do
    subjName=( $(echo ${i} |awk -F '/' '{print $7}') )
    timeline=( $(echo ${i} |awk -F '/' '{print $8}') )
    echo $subjName $timeline

    cp ${i} fa_collection/${subjName}_${timeline}.nii.gz

done

