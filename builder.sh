#! /bin/bash

SCRIPT_PATH=`realpath $0`
CLUSTERGEN_DIR=`dirname $SCRIPT_PATH`

if [ -z "$BUILD_RPM"  ] ; then
  echo " 
************************************************************
** IMPORTANT NOTICE **
************************************************************

If your current OS version matches the OS versions on the cluster nodes.
You can save time by reusing pre-built Slurm binaries.

- If you choose to build Slurm now, the pre-built binaries will be used for each node
- Otherwise, each node will compile it separately.

Would you like to build Slurm now?

Please enter 'y' to build it.
"
  read BUILD_RPM
fi

python3 cgen.py -i $CLUSTERGEN_DIR/cluster.json -d $CLUSTERGEN_DIR/build -f 

if [ "$BUILD_RPM" == "y" ] ; then
  $CLUSTERGEN_DIR/build/scripts/buildslurm.sh
fi
