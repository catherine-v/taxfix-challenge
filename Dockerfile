FROM python:3.6

RUN apt-get update && apt-get -y upgrade && apt-get -y install cron

# Install scripts dependencies
COPY . /taxfix-challenge
ENV PYTHONPATH="${PYTHONPATH}:/taxfix-challenge"
WORKDIR /taxfix-challenge
RUN pip install -r /taxfix-challenge/requirements.txt

# Setup periodical jobs via crontab
ADD crontab /etc/cron.d/jobs
RUN chmod 0644 /etc/cron.d/jobs
RUN crontab /etc/cron.d/jobs

# Start processes
CMD ["./script_wrapper.sh"]
