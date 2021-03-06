#!/bin/sh

# sh -c "$(curl -fsSL https://raw.githubusercontent.com/Teumer/ctrlm/master/install.sh)
# sh -c "$(wget https://raw.githubusercontent.com/Teumer/ctrlm/master/install.sh -O -)"

DIRECTORY='ctrlm'

if [ "$(id -u)" -ne 0 ]; then
  echo "Please run as root"
  exit
fi

# Check if python3 is installed
if ! python3 -V; then
  yum install python3 -y
fi

# Remove directory if exists
if [ -d "$DIRECTORY" ]; then
  rm -rf "$DIRECTORY"
fi

# Clone repository
git clone https://github.com/Teumer/ctrlm.git

cd "$DIRECTORY"

# Start install
python3 install.py