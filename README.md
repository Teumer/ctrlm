# ctrlm

## Purpose

Automated deployment of the following Control-M components:
1. Control-M/Enterprise Manager
2. Control-M/Server
3. Control-M/Agent
4. Control-M/Batch Impact Manager
5. Control-M/Forecast


## Input / Requirements
1. Red Hat 7 virtual machine
   - hosted on BMC Cloud Lifecycle Management
   - clean state - no Control-M software previously installed
2. Login as root user


## Process
```
# Clone the repository
git clone https://github.com/Teumer/ctrlm.git
```

```
# Navigate to the directory
cd ctrlm
```

```
# Allow user to execute
chmod u+x install.py
```

```
# Execute script
./install.py
```

```
CONTROL-M Installation Menu
-----------------------------

Select one of the following versions:

1 - 9.0.19.200
2 - 9.0.19.100
3 - 9.0.19.000

0 - Quit

 Enter option number --->   []:
```

## Output
Quickly ready a new test environment for troubleshooting.
