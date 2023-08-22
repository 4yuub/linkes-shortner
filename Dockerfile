FROM python:3.10.0a7-alpine3.13

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 5001

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5001"]