FROM ubuntu:latest

MAINTAINER 8cbx<chu849238686@aliyun.com>

# update ubuntu && install pip

RUN apt-get update && apt-get -y install python-pip python-mysqldb python-dev vim

# install requirement package

COPY requirements.txt /opt/judge_contest/requirements.txt
RUN pip install -r /opt/judge_contest/requirements.txt

ADD ./ /opt/judge_contest

WORKDIR /opt/judge_contest
VOLUME ["/root/data"]
ENTRYPOINT ["./start.sh"]

EXPOSE 8000