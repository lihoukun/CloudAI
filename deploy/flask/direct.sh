cd ../../webapp
git pull
export FLASK_APP=main.py
export FLASK_DEBUG=1
python3 -m flask run --host=0.0.0.0 --port=30050
