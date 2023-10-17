FROM python:3.9
WORKDIR /opt/app

COPY . .
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python3", "main.py"]
