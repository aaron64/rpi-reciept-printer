set -e

sudo usermod -a -G dialout pi
sudo usermod -a -G lp pi

python3 -m venv --without-pip .
./bin/python -m ensurepip --upgrade
./bin/pip install -r requirements.txt
