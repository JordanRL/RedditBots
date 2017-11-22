#!/usr/bin/env bash
python3 run.py mentionMonitor > bot_log.txt 2> bot_errors.txt &
python3 run.py submissionMontir > bot_log.txt 2> bot_errors.txt &
python3 run.py highReports > bot_log.txt 2> bot_errors.txt &
python3 run.py risingPost > bot_log.txt 2> bot_errors.txt &
python3 run.py trollUnreported > bot_log.txt 2> bot_errors.txt &
python3 run.py violence > bot_log.txt 2> bot_errors.txt &