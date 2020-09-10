#!/bin/bash

python3 dump_logs.py 2020-01-01 2022-01-01
tar -cvf ~/dump_images.tar -C ~ biohack_downloads
tar -cvf ~/dump_results.tar -C ~ dump_2020-01-01_2022-01-01.txt dump_images.tar