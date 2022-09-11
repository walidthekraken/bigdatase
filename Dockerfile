FROM python:3.9-slim

COPY prod_requirements.txt .

RUN apt-get update
RUN yes | apt-get install build-essential python-dev libffi-dev
RUN yes | apt install libcurl4-openssl-dev libssl-dev

RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -Ur prod_requirements.txt

EXPOSE 8080

COPY . .
ENTRYPOINT ["python", "-m", "gunicorn", "--access-logfile", "-", "--bind", "0.0.0.0:8080", "--workers=12", "--threads=5", "--preload", "Backend:create_app()"]
