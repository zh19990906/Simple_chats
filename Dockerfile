FROM python:3.7

# install google chrome
#RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
#RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
#RUN apt-get -y update
#RUN apt-get install -y google-chrome-stable
#
## install chromedriver
#RUN apt-get install -yqq unzip
#RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
#RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/


WORKDIR /usr/src/app
ADD . /usr/src/app


# install requirements


RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 修改时区
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 运行redis维护文件
#RUN nohup python3 /usr/src/app/Simple_redis_maintain.py >/dev/null 2>&1 &

CMD ["python3", "app.py"]
#CMD ["python3","Simple_redis_maintain.py"]