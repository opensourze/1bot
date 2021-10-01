FROM python:3

WORKDIR /app

COPY . .

RUN python3 -m pip install -Ur ./requirements.txt

CMD python -u ./main.py