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
  -h    -> help          show this help message and exit
  -s    -> skip Control-M installation, download packages only
  -ssl  -> setup SSL Zone 1, 2, 3
```

##### SSL Deployment Process

```
# Execute script after installation with ssl argument
python install.py -ssl

# Follow the instructions below
```

```
Zone 1 - Control-M/Enterprise Manager Web Server

1. Copy the following keystore from the VM to your laptop / computer with desktop client installed
    - /auto_ssl/hostname-keystore-zone-1.p12
2. Right click on the .p12
    - Select Install PFX
    - Select Default Options
    - Enter Password 'changeit'
3. Recycle the web server
4. Control-M Web and Desktop Client are ready for use with SSL
```

```
Zone 2 - Control-M/Enterprise Manager and Control-M/Server
Zone 3 - Control-M/Server and Control-M/Agent

1. The script deploys SSL to each component, however, manual steps are required to enable SSL mode
2. Review the document: Enabling SSL in zone 2 and 3
https://documents.bmc.com/supportu/9.0.20/help/Main_help/en-US/index.htm#98211.htm
```

## Output
Quickly ready a new test environment for troubleshooting.

Control-M/Enterprise Manager Client login: 
```emuser / empass```

Control-M/Enterprise Manager Unix Account: ```em1 / empass```

Control-M/Server Unix Account: ```s1 / empass```

