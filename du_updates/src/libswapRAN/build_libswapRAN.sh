#! /bin/bash

docker build -t swapran-builder .
docker run --rm -it -v $PWD:/build swapran-builder make