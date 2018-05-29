#22-May-2018
#Andy said the errors of eff_data are too low, should be double checked



#Produce the results with the same version input as the eff_data in aux material of paper

PROJECT="Dec.01.AddStopNlo"
INPUT="./input/CalJetDec.01.AddStopNlo.root"
OUTPUT="./output"
CONFIG="./data/Run_CalJet_test.json"
CDI="2016-20_7-13TeV-MC15-CDI-2017-01-31_v1.root"
VERSION="r20.7"


RUNTAG=vtest

python scripts/Run.py -e   --project_name ${PROJECT} --input_file ${INPUT} --output_path ${OUTPUT} --config_file ${CONFIG} --cdi_file ${CDI}  #  1>logs/${PROJECT}_${RUNTAG}.output 2>logs/${PROJECT}_${RUNTAG}.error 0>logs/${PROJECT}_${RUNTAG}.warning
#python scripts/Run.py -t  --project_name ${PROJECT} --input_file ${INPUT} --output_path ${OUTPUT} --config_file ${CONFIG} --cdi_file ${CDI} --version ${VERSION}
