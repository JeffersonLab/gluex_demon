#!/bin/bash

if [ $# -ne 2 ]; then
  echo
  echo "Usage: run_demon.sh <run-period> <version> [run/copy]"
  echo "eg     run_demon.sh 2023-01 07"
  echo
  echo "run: exit after running scan.py, do not copy output files into halldweb"
  echo "copy: do not run scan.py, copy existing output files into halldweb"
  echo
  exit
fi

run_period=$1
version=$2

run_only=0
copy_only=0

if [ "$3" == "run" ] ; then
  run_only=1
elif [ "$3" == "copy" ] ; then
  copy_only=1
fi

home_dir=$PWD
verbose=1

demon_web_home=/group/halld/www/halldweb/html/gluex_demon    # web files live here

scan_path=/home/njarvis/tests/scan.py   # path to demon code scan.py

histo_dir=/work/halld/data_monitoring/RunPeriod-${run_period}/mon_ver${version}/rootfiles


for x in $demon_web_home $histo_dir ; do
  if [ ! -d $x ]; then
    echo Could not find $x
    exit
  fi
done


if [ ! -f $scan_path ]; then
  echo Could not find $scan_path
  exit
fi



datestring=`date '+%Y-%m-%d_%H:%M:%S'`

temp_dir=demon_$datestring

mkdir $temp_dir
cd $temp_dir

[ $verbose ] && echo Created and moved into $temp_dir



if [ $copy_only -eq 0 ] ; then
  echo Running demon 
  python3.6 ${scan_path} -r ${run_period} -v $version 
  echo Demon run complete
  echo Output files:
  ls monitoring_*
fi

# list of output files

f1=monitoring_graphs_${run_period}_ver${version}.root
f2=monitoring_data_${run_period}_ver${version}.csv
f3=monitoring_pagenames_${run_period}_ver${version}.txt
f4=monitoring_badruns_${run_period}_ver${version}.txt

for x in $f1 $f2 $f3 ; do
  if [ ! -f $x ]; then
    echo Could not find $x
    exit
  fi
done


if [ $run_only -eq 1 ] ; then
  cd $home_dir
  exit
fi



# copy files into demon_web_home

# runperiods.txt contains eg
# RunPeriod-2022-05

rpname=RunPeriod-${run_period}

rplist=${demon_web_home}/runperiods.txt

if ! grep -q $rpname "$rplist"; then
  echo Adding $rpname to $rplist
  echo $rpname >> $rplist
fi 

demon_rp_dir=${demon_web_home}/$rpname
if [ ! -d $demon_rp_dir ] ; then
  echo Making directory $demon_rp_dir
  mkdir $demon_rp_dir
fi

# add version to versions.txt

versionlist=${demon_rp_dir}/versions.txt

if [ ! -f $versionlist ] ; then
  Creating $versionlist and adding version $version to it
  echo $version > $versionlist
else # file exists, maybe version is in there already
  if ! grep -q $version "$versionlist"; then
    echo Adding $version to $versionlist
    echo $version >> $versionlist
  fi 
fi

demon_ver_dir=${demon_rp_dir}/$version

if [ ! -d $demon_ver_dir ] ; then
  echo Making directory $demon_ver_dir
  mkdir $demon_ver_dir
fi

echo Copying files into $demon_ver_dir
for x in $f1 $f2 $f3 $f4 ; do
  cp -v $x $demon_ver_dir
done


cd $home_dir

echo Files are left in $temp_dir
echo You might want to remove them

rm -i ${temp_dir}/*
rmdir $temp_dir
