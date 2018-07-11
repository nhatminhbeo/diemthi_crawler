#!/bin/bash

IP=$1
CODE=$2
SKIP=$3
START=$4
END=$5
STEP=$6

i=$START

ssh -t -t -i ~/.ssh/vietego Vietego@$IP << EOF
cd diemthi_crawler;

while [ $i -lt $END ]
do
	LOW=$i
	HIGH=$(($i + $STEP - 1))
	COM=`printf "nohup python crawler_zing.py $SKIP $CODE %06d %06d T >> log &" $LOW $HIGH`
	echo $COM
	i=$(($i + $STEP))
done

EOF