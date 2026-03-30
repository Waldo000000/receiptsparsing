#!/bin/bash
set -e -x

dateStr=`date +%s`
bkpdir=./bkp/${dateStr}
mkdir -p bkp
mv out ${bkpdir}
mkdir -p out

##cmd="./parse_csv.py --month $1 --outFileName ./out/$(date +"%Y%m%d").out.csv ./in/*.csv"
#cmd="./parse_csv.sh in/in.offset.csv out/out.offset.csv"
#$cmd Offset

cmd="./parse_csv.sh in/in.ubank.csv out/out.ubank.csv"
echo "cmd: $cmd"
$cmd Ubank

if [ -f in/in.bendigo.csv ]; then
    cmd="./parse_csv.sh in/in.bendigo.csv out/out.bendigo.csv"
    echo "cmd: $cmd"
    $cmd Bendigo
fi

#sort -t, -k2 out/out.offset.csv out/out.ubank.csv | tee out/out.csv
sort -t, -k2 out/out.ubank.csv out/out.bendigo.csv 2>/dev/null | tee out/out.csv
