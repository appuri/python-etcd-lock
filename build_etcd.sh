#!/bin/sh

git clone -b ${1:master} https://github.com/coreos/etcd.git --depth=1
cd etcd
./build
./bin/etcd &