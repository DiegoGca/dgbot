#!/bin/bash
# Simple script to update pip and install requirements
# Requires: pip
#
echo -e "\033[0;33m"
echo Upgrade pip
echo -e "\033[0m"
pip install --upgrade pip

echo -e "\033[0;33m"
echo Install requirements
echo -e "\033[0m"
pip install -r requirements.txt

if [[ $? -eq 0 ]]; then
    echo -e "\033[0;33m"
    echo Success!
    echo -e "\033[0m"
fi