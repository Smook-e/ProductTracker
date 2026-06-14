FROM python:3.14.5-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0"]