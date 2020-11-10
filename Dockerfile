FROM python:3.8 as builder

COPY requirements.txt .

RUN groupadd -g 999 flask && useradd -r -u 999 -g flask flask

RUN mkdir /home/flask

RUN chown -R flask:flask /home/flask
RUN chmod -R 770 /home/flask

USER flask

RUN pip install --user -r requirements.txt
# RUN pip install --user gunicorn

FROM python:3.8-slim

# Set ENV
ENV TZ=America/Toronto
ENV FLASK_ENV=production
ENV FLASK_APP=main.py
ENV SECRET_KEY=swertjgisoetrsaerhbnsegfhjkrtg32qw594p4t67234908hsdfkbgn
ENV DATA_URI=/data

WORKDIR /data
VOLUME /data

WORKDIR /app

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

RUN groupadd -g 999 flask && useradd -r -u 999 -g flask flask
RUN mkdir /home/flask

COPY --from=builder /home/flask/.local/ /home/flask/.local
ENV PATH=/home/flask/.local/bin:$PATH

RUN chown -R flask:flask /home/flask
RUN chmod -R 770 /home/flask
RUN chown -R flask:flask /data
RUN chmod -R 770 /data
USER flask

COPY main.py ./
COPY webscraper/ ./webscraper

CMD ["python", "main.py"]

# CMD ["gunicorn", "-b", ":5000", "--access-logfile", "-", "--error-logfile", "-", "--workers", "5", "-t", "90", "main:app"]