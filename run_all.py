import subprocess as s

processes = {}
processes["mentionMonitor"] = s.Popen(['python3', 'run.py', 'mentionMonitor'])
processes["submissionMonitor"] = s.Popen(['python3', 'run.py', 'submissionMonitor'])
processes["highReports"] = s.Popen(['python3', 'run.py', 'highReports'])
processes["risingPost"] = s.Popen(['python3', 'run.py', 'risingPost'])
processes["trollUnreported"] = s.Popen(['python3', 'run.py', 'trollUnreported'])
processes["violence"] = s.Popen(['python3', 'run.py', 'violence'])

try:
    while True:
        currentProcs = '\n'.join(processes.keys())
        action = input("What action do you want to take?\n\n1: Start a new bot\n2: Kill a bot\n3: List currently active bots")
        if int(action) == 1:
            startCommand = input("Currently running bots:\n\n"+currentProcs+"\n\nType the name of the bot you want to start")
            processes[startCommand] = s.Popen(['python3', 'run.py', startCommand])
        elif int(action) == 2:
            killCommand = input("Currently running bots:\n\n"+currentProcs+"\n\nType the name of which bot you want to kill"
                                " (use 'all' to kill everything):")
            if killCommand in processes:
                if s.Popen.poll(processes[killCommand]) is None:
                    s.Popen.terminate(processes[killCommand])
                    del(processes[killCommand])
            elif killCommand == "all":
                for bot in processes:
                    s.Popen.terminate(bot)
                processes = {}
            else:
                print("Sorry, your command couldn't be recognized")
        elif int(action) == 3:
            print('\n'.join(currentProcs))
        else:
            print("Sorry, your command couldn't be recognized")
except:
    for bot in processes:
        print("Problem encountered, terminating all active bots")
        s.Popen.terminate(bot)

