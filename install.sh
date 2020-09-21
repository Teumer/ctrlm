#!/bin/sh

DIRECTORY='ctrlm'

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# Check if python3 is installed
if not python3 -V; then
  yum install python3 -y
fi

# Remove directory if exists
if [ -d "$DIRECTORY" ]; then
  rm -rf "$DIRECTORY"
fi

# Clone repository
#git -c http.sslVerify=false clone https://github.com/Teumer/ctrlm.git
git clone https://github.com/Teumer/ctrlm.git

cd "$DIRECTORY"

# Start install
python3 install.py