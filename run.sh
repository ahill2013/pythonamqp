#!/bin/bash

echo 'neuromancer: run.sh: Entered run.sh'

echo 'neuromancer: run.sh: sudo pigpiod'
sudo pigpiod

echo 'neuromancer: run.sh: sleep 5'
sleep 5

echo 'neuromancer: run.sh: for i in `seq 1 3`;'
for i in `seq 1 3`; do
    echo 'neuromancer: run.sh: do python ~/pythonamqp/src/main.py'
    python ~/pythonamqp/src/main.py
    echo 'neuromancer: run.sh: *** python crashed?? Restarting.'
done

echo 'neuromancer: run.sh: Something bad probably happened.'
echo 'neuromancer: run.sh: Exiting'
