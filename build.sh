#!/bin/bash
# $0 is the script name, $1 id the first ARG
if [ -z "$1" ]
  then
    echo "No OS Type argument supplied -- ./build.sh <OS Type>"
    exit
fi

#pytest || { echo '!!!Test finish with ERROR' ; exit 1; }

osType="$1"

pip3 install wheel

rm -rf ./dist/$osType
mkdir -p ./dist/$osType
rm -rf ./_build
mkdir ./_build
mkdir ./_build/simpleservice
mkdir ./_build/simpleservice/lib
mkdir ./_build/simpleservice/src
mkdir ./_build/simpleservice/docs
rm -rf ./src/python/log
rm -rf ./src/python/__pycache__
cp -rf ./src/python/* ./_build/simpleservice/
cp -rf ./src/scripts/* ./_build/simpleservice/
cp -rf ./docs/* ./_build/simpleservice/docs
cp ./README.md ./_build/simpleservice/
pip3 install -r requirements.txt --target ./_build/simpleservice/lib


cp ./_build/simpleservice/lib/cx_Oracle.*.so ./_build/simpleservice/lib/cx_Oracle.so
rm ./_build/simpleservice/lib/cx_Oracle.*.so
cp ./_build/simpleservice/lib/_yaml.*.so ./_build/simpleservice/lib/_yaml.so
rm ./_build/simpleservice/lib/_yaml.*.so
cp ./_build/simpleservice/lib/_cffi_backend.*.so ./_build/simpleservice/lib/_cffi_backend.so
rm ./_build/simpleservice/lib/_cffi_backend.*.so
cp ./_build/simpleservice/lib/ujson.*.so ./_build/simpleservice/lib/ujson.so
rm ./_build/simpleservice/lib/ujson.*.so

rm -rf ./_build/*.pyc
cd ./_build
tar -czf ../dist/$osType/simpleservice-$osType.tar.gz ./simpleservice/
cd ..
rm -rf ./_build

# build src only
osType="src_only"
rm -rf ./dist/$osType
mkdir -p ./dist/$osType
rm -rf ./_build
mkdir ./_build
mkdir ./_build/simpleservice
mkdir ./_build/simpleservice/src
mkdir ./_build/simpleservice/docs
rm -rf ./src/python/log
rm -rf ./src/python/__pycache__
cp -rf ./src/python/* ./_build/simpleservice/
cp -rf ./src/scripts/* ./_build/simpleservice/
cp -rf ./docs/* ./_build/simpleservice/docs
cp ./README.md ./_build/simpleservice/
rm -rf ./_build/*.pyc
cd ./_build
tar -czf ../dist/$osType/simpleservice_$osType.tar.gz ./simpleservice/
cd ..
rm -rf ./_build