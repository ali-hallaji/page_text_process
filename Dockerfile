FROM python:2

EXPOSE 8888

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY initialize.py /usr/src/app/
RUN python initialize.py

COPY . .

ENTRYPOINT ["python", "main.py"]