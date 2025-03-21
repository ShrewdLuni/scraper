FROM python:3.13.2-alpine

WORKDIR /scraper

RUN apk add --no-cache git curl

RUN git clone --depth=1 https://github.com/ShrewdLuni/scraper.git .

COPY ceneo_scraper/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "ceneo_scraper/run.py"]
