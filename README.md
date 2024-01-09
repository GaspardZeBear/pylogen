# PYLOGEN

PYthon LOad GENerator



## Function

A quick load injector for kms.i

Based on python multiprocessing module to avoid GIL effect.

A run launches a main, that launches subprocess (runners) for the requred CUT (encrypt, sign)

A CUT is a subclass of ClassUnderTest.

A runner runs loops of calls to the CUT (see parameters loop, duration ...).
The --proc parameter controls the count of runners.
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
--process PROCESS : number of process (to set in accordance with the expected load and the capacities of the server<br>
--postpone POSTPONE : postpones the start of the run (permits to shape a load)<br>
--rampup RAMPUP : time between each process start <br>
--duration DURATION : duration of the process (vs loops). Prioritary <br>
--loops LOOPS : how many loops per process<br>
--lengths LENGTHS : array of lengths (for exemple). Loop on length in a loop execution<br>
--extra EXTRA : parameters for plugins <br>
--pauseloop PAUSELOOP : pause between loops  <br>
--pauselen PAUSELEN :  pause between lengths<br>
--summary SUMMARY : time between 2 summary computations <br>
--outformat OUTFORMAT : csv (short) of anything (long) <br>
--id ID : an arbitrary ID

--file FILE : name of scenario file

### Scenario 

A file with 1 line per CUT. Useful to mix operations at the same time.
May be used to shape a load profile with postpone starts and durations

Sample : python3 Pylogen.py scenario --file Scenario.txt

### Samples Pylogen 

Hereunder Dummy and KmsEncrytSymmetric are class names (in <class>.py files)

- python3 Pylogen.py cuts.Dummy  --le 384 --pauselen 0 --pauselo 0.001  --duration 10 --ram 0 --proc 2
- python3 Pylogen.py cuts.KmsEncrytSymmetric --defaults myprofile.json  --le 384,512,1024 --pauselen 0 --pauseloop 0 --duration 10 --proc 1 --extra '{"file":"KmsDefault.json","key":"symmetric1"}'

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


### Kms cuts options : extra

Options are a json string in --extra with 2 keys :
- file : name of a json file containing keys definition. Optionnal : default KmsDefault.json
- key : the name of the key in file
Sample : 
- --extra '{"key":"symmetric1"}'
- --extra '{"file":"MyKmsDefault.json","key":"symmetric1"}'




