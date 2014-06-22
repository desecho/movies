pip install -r requirements.txt
bower install
mkdir temp
cd temp
git clone https://github.com/wagnerrp/pytmdb3.git
cd pytmdb3
./setup.py install
cd ../../
rm -fR temp
mkdir movies_project/cache
cd movies_project/cache
touch tmdb3.cache
chmod 777 tmdb3.cache
