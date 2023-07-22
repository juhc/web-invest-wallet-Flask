FROM python:3.10-bullseye

COPY . /app

WORKDIR /app

RUN pip3 install pip==22.0.2
RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]