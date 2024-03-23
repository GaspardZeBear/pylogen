# PYLOGEN

PYthon LOad GENerator



## Function

A quick experimental load injector

Based on python multiprocessing module to avoid GIL effect.

A run launches a main, that launches subprocess (runners, workers) for  CUT processing

A CUT is a subclass of ClassUnderTest.

A run may run as 

- closed model processing : driver : predefined workers count
A runner runs loops of calls to the CUT (see parameters loop, duration ...).
The --proc parameter controls the count of runners.

- opened model processing : driver : events arrivals rate dynamically creates wand adjusts workers count

A CUT executes requests that may be embedded in transactions.

Stats are displayed on STDIN.

The stats are processed thru a single queue. 
One line per event (request or transaction), with local data (ex : CUT process throughput, request time) and global datas (global throughput).

A summary with high water marks is displayed at end of run
If queue length highwatermark is high (hint : > 4 * cores as a rule of thumb), records could not be poped as quickly as required .. : throughput  biased

Important : 
- It's python : may be sufficient for Kms testing. Beware of cpu 
- Global stat may be biased if queure reader process is too low. Local not !
- Have a look at the sum of local throughputs vs global one : they should be consistent : global ~ process * local
- global count and throughput count only requests, not transactions
- a transaction and its requests have the same transaction id (None if no transaction)

## Installation

Python venv
- python3 -m venv venv
- . venv/bin/activate
- pip3 install --upgrade pip
- pip3 install -r requrements.txt

Then 

- . venv/bin/activate

## Usage 

### General  Pylogen

Please see Pylogen.py section for new (but not fully tested) functionnalities

usage: Pylogen.py {action} [-v] [--process PROCESS] [--postpone POSTPONE] [--rampup RAMPUP] [--duration DURATION] [--loops LOOPS] [--lengths LENGTHS] [--extra EXTRA] [--pauseloop PAUSELOOP] [--pauselen PAUSELEN] [--summary SUMMARY] [--outformat OUTFORMAT]

action : either 
- name of a CUT
- keyword "scenario"

Note : if "scenario", none of the following are usable, except --file 

<br>
-v : verbosity -vv _vvv ....  <br>
--postpone POSTPONE : postpones the start of the run (permits to shape a load)<br>
--rampup RAMPUP : time between each process start <br>
--lengths LENGTHS : array of lengths (for exemple). Loop on length in a loop execution<br>
--extra EXTRA : parameters for plugins <br>
--pauselen PAUSELEN :  pause between lengths<br>
--summary SUMMARY : time between 2 summary computations <br>
--outformat OUTFORMAT : csv (short) of anything (long) <br>
--id ID : an arbitrary ID

--file FILE : name of scenario file

### Closed model

By default, closed model : a predefined number of worker process running cuts is given 

--process PROCESS : number of process (to set in accordance with the expected load and the capacities of the server<br>
--duration DURATION : duration of the process (vs loops). Prioritary <br>
--loops LOOPS : how many loops per process<br>
--pauseloop PAUSELOOP : pause between loops  <br>

### Opened model 

Opened model : a generator generates events at a given frequency.
These events are processed by workers
A controller adjusts the number of worker to process as quick as possible

--openedmodel : use openedmodel
--controllerDelay : frequency for the controller to adjust number of process 
--generatorDelay : ?
--sechedule : schedule : example 30@10,20@15 : during 30 seconds generate 10 runs/second then during 20 seconds 15 runs/second
--trigger : if more than trigger events in the jobqueue, start a new worker
--prefork : number of workers to start before generation begins
--decrease : number of consecutive times the controller found no job in queue : then kills a worker to spare resources

### Scenario 

A file with 1 line per CUT. Useful to mix operations at the same time.
May be used to shape a load profile with postpone starts and durations

Sample : python3 Pylogen.py scenario --file Scenario.txt

### Samples Pylogen 

Hereunder Dummy and KmsEncrytSymmetric are class names (in <class>.py files)

- python3 Pylogen.py cuts.Dummy  --le 384 --pauselen 0 --pauselo 0.001  --duration 10 --ram 0 --proc 2
- python3 Pylogen.py cuts.KmsEncrytSymmetric --defaults myprofile.json  --le 384,512,1024 --pauselen 0 --pauseloop 0 --duration 10 --proc 1 --extra '{"file":"KmsDefault.json","key":"symmetric1"}'


- python3 Pylogen.py cuts.Dummy  -vvv  --open  --pre 2 --sche "5@1,10@0.1,5@1,30@0.1" --len 0  --out x --contr 0.5 --extra '{"sleep":1}'
- python3 Pylogen.py cuts.Sbgc01 -vvv  --open  --pre 2 --sche "5@1" --len 0  --out x --contr 0.5 --extra '{"sleep":1}'
- python3 Pylogen.py cuts.Sbgc01 -vvv  --open  --pre 2 --sche "5@1" --len 0  --out x --contr 0.5 --extra '{"sleep":1}'


Beware : use --defaults or --def , not -d nor --defa nor --defau ...


## CUTS

### Integrate

Cuts are imported dynamically (importlib).
Put them in cuts directory !!!

### Design 

- A CUT inherits ClassUnderTest
- A CUT contains requests
- A CUT may contain a transaction (requestsManager) that groups the requests
- be careful, give relevant names (id, requestsManager and requests names) to interpret output
- CUT should be written with @Executor.exec decorator


### cuts options : extra

Options are a json string in --extra with 2 keys :
- file : name of a json file containing keys definition. Optionnal : default KmsDefault.json
- key : the name of the key in file
Sample : 
- --extra '{"key":"symmetric1"}'
- --extra '{"file":"MyKmsDefault.json","key":"symmetric1"}'




