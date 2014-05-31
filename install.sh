pip install -r requirements.txt
mkdir temp
cd temp
git clone https://github.com/wagnerrp/pytmdb3.git
cd pytmdb3
./setup.py install
rm -fR ../../temp