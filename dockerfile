from ubuntu:20.04

run apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git

run pip3 install flask && pip3 install requests
run pip3 install pydexcom

copy . /app.py 
copy ./requirements.txt ./requirements.txt
copy ./suger_readings.py ./suger_readings.py

cmd app.py