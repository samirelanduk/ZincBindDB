FROM ubuntu

RUN mkdir -p /home/app

WORKDIR /home/app

RUN apt update
RUN apt -y install python3-pip
RUN apt-get install -y cron
COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt


COPY ./build ./build
COPY ./core ./core
COPY ./data ./data
COPY ./manage.py ./manage.py
RUN rm ./core/secrets.py
RUN python3 manage.py migrate

RUN sed -i s/'DEBUG = True'/'DEBUG = False'/g ./core/settings.py

RUN echo "0 5 * * * cd /home/app && python3 build/build.py >> /var/log/cron.log 2>&1 && python3 build/cluster.py >> /var/log/cron.log 2>&1" > scheduler.txt
RUN crontab scheduler.txt

CMD python3 build/build.py && python3 build/cluster.py
