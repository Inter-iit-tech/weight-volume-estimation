FROM python:3.8-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update --fix-missing -y
RUN apt-get install libgl1 libglib2.0-0 -y

EXPOSE 5000

CMD [ "python", "./volume.py" ]