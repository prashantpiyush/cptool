# export PATH=$PWD/dist:$PATH
# pyinstaller --onefile cf.py
# pyinstaller --onefile atc.py
python3 -m PyInstaller --onefile cf.py
python3 -m PyInstaller --onefile atc.py
sudo cp dist/cf /usr/local/bin/cf
sudo cp dist/atc /usr/local/bin/atc