#!/bin/bash
#cmd="./parse_csv.py --month $1 --outFileName ./out/$(date +"%Y%m%d").out.csv ./in/*.csv"
cmd="./parse_csv.py --readAll --outFileName $2 --source $3 $1"
echo "cmd: $cmd"
python $cmd
