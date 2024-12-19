#!/bin/bash
export DEPENDS=$(< etc/shDEPENDENCIES.txt)
for name in ${DEPENDS}
do
        [[ $(command -v $name 2>/dev/null) ]] || { echo -en "\n$name needs to be installed.";deps=1; }
done
[[ $deps -ne 1 ]] && echo "OK" || { echo -en "\nInstall the above and rerun this script\n"; }