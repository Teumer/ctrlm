# ctrlm

## Purpose

Automated download and deployment of the following Control-M components:
1. Control-M/Enterprise Manager
2. Control-M/Server
3. Control-M/Agent
4. Control-M/Batch Impact Manager
5. Control-M/Forecast
6. Control-M/Self Service
7. Control-M/Workload Change Manager
8. Control-M/Web Services, Java, and Messaging
9. Control-M/Advanced File Transfer
10. Control-M/Managed File Transfer
11. Control-M/Application Pack


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
# Execute script
python install.py
```

```
CONTROL-M Installation Menu
-----------------------------

Select one of the following versions:

1 - 9.0.20.000
2 - 9.0.19.200
3 - 9.0.19.100
4 - 9.0.19.000

0 - Quit

 Enter option number --->   []:
```


```
usage: install.py [-h] [-s]

optional arguments:
  -h, --help          show this help message and exit
  -s, --skip-install  skip Control-M installation, download packages only
```

## Output
Quickly ready a new test environment for troubleshooting.

Control-M/Enterprise Manager Client login: 
```emuser / empass```

Control-M/Enterprise Manager Unix Account: ```em1 / empass```

Control-M/Server Unix Account: ```s1 / empass```

