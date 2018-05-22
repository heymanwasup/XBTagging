#22-May-2018
#Andy said the errors of eff_data are too low, should be double checked



#Produce the results with the same version input as the breakdown table in paper 
#then compare it to the corrected version which used for eff_data

PROJECT="Nov.24.Fixed"
INPUT="./input/CalJetNov.24.Fixed.root"
OUTPUT="./output"
CONFIG="./data/Run_CalJet_r207_noStopME_full.json"
CDI="./data/2016-20_7-13TeV-MC15-CDI-2017-01-31_v1.root"

RUNTAG=v1

Run.py -e  --project_name ${PROJECT} --input_file ${INPUT} --output_path ${OUTPUT} --config_file ${CONFIG} --cdi_file ${CDI}   1>logs/${PROJECT}_${RUNTAG}.output 2>logs/${PROJECT}_${RUNTAG}.error 0>logs/${PROJECT}_${RUNTAG}.warning

Run.py -b -t -cdi --project_name ${PROJECT} --input_file ${INPUT} --output_path ${OUTPUT} --config_file ${CONFIG} --cdi_file ${CDI}
