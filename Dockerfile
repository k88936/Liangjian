FROM centos:centos7

# COPY ./CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo
# COPY ./RPM-GPG-KEY-7 /etc/pki/rpm-gpg/RPM-GPG-KEY-7

# 使用yum-builddep为Python3构建环境
RUN yum update -y && yum install yum-utils -y && yum-builddep python -y \
    && yum install -y wget make

# 控制版本
ENV PYTHON_NAME Python-3.7.7
ENV JAVA_NAME jre-8u251-linux-x64


COPY ./docker/jre-8u251-linux-x64.tar.gz /home
COPY ./docker/Python-3.7.7.tgz /home
COPY ./docker/requirements.txt /home

#编译Java8
RUN mkdir /usr/local/java && tar -zxvf /home/${JAVA_NAME}.tar.gz -C /usr/local/java/

# 编译Python3
RUN tar -zxvf /home/${PYTHON_NAME}.tgz -C /home/ \
    && cd /home/${PYTHON_NAME} \
    && ./configure \
    && make \
    && make install

RUN ln -s /usr/local/bin/pip3 /usr/local/bin/pip

# 删除文件
RUN rm -rf /home/${PYTHON_NAME} \
    && rm -rf /home/${PYTHON_NAME}.tgz \
    && rm -rf /home/${JAVA_NAME}.tar.gz

# 环境变量
ENV JRE_HOME /usr/local/java/jre1.8.0_251
ENV PATH=$PATH:$JAVA_HOME/bin:$JRE_HOME/bin

COPY ./bundle /root/resource/bundle
RUN pip install -r /home/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY ./hephaestus /root/resource/hephaestus
COPY ./shell /root/resource/shell

CMD echo "Docker Success!"