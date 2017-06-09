FROM amazonlinux:latest

# Install system packages
RUN yum -y update
RUN yum -y install which unzip aws-cli python35 python35-pip
RUN pip-3.5 install --upgrade pip
RUN pip install numpy pandas pymysql tensorflow

ADD . /nonlinear_capm_beta
WORKDIR /nonlinear_capm_beta/estimation

ENV PYTHONPATH "/:$PYTHONPATH"

