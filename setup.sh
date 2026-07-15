set -e

sudo usermod -a -G dialout pi
sudo usermod -a -G lp pi

python3 -m venv .
./bin/pip install -r requirements.txt
