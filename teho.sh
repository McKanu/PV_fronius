#/usr/bin/bash
xmlstarlet el -v http://192.168.10.59/measurements.xml |sed '/AC_Power.]/!d' | awk -F "'" '{print $2}'

