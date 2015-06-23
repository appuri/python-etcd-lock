#!/bin/sh

if [  $# -gt 0 ]; then
    ETCD_VERSION="$1"
else
    ETCD_VERSION="master"
fi

echo "Using ETCD version $ETCD_VERSION"

git clone -b $ETCD_VERSION --depth=1 https://github.com/coreos/etcd.git
cd etcd
./build