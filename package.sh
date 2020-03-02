#Edit the version and the download_url from setup.py prior to executing this
python setup.py sdist
twine upload dist/*
