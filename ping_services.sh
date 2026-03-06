#!/bin/bash

if ping -c 1 google.com &> /dev/null
then
  echo "Google.com is reachable."
else
  echo "Google.com is not reachable."
fi
