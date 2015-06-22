#!/bin/sh

if [  $# -gt 0 ]
    then
    ETCD_VERSION="$1";
    else
    ETCD_VERSION="master";
fi

echo "Using ETCD version $ETCD_VERSION"

git clone https://github.com/coreos/etcd.git --depth=1
cd etcd
git checkout $ETCD_VERSION
./build
./bin/etcd &