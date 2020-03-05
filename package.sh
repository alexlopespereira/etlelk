#!/bin/bash
#Edit the version and the download_url from setup_template.py prior to executing this
tag=$1
message=$2
rm ./dist/*.gz
sed "s/TAG/$tag/g" ./setup_template.py > ./setup.py

git commit . -m "$message"
git tag $tag
git push origin $tag
python setup.py sdist
twine upload dist/*
