FROM python:3.13.2-alpine

WORKDIR /scraper

RUN apk add --no-cache git curl

RUN curl -O https://raw.githubusercontent.com/shrewdluni/scraper/main/ceneo_scraper/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN rm requirements.txt

RUN git clone --depth=1 https://github.com/ShrewdLuni/scraper.git .

EXPOSE 5000

CMD ["python", "ceneo_scraper/run.py"]
