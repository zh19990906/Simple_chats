# Simple_chat

#### 介绍
Redis+ Python3 + flask实现简易聊天室
#### 源码
https://github.com/zh19990906/Simple_chats

# Redis

#### 说明

这里面一共用到了3个redis的库，0库目前左右存储用户名的，后面有可能放弃使用，11和10是来校验token的，并且修复了一个用户可以产生多个token的情况，12库用来存储聊天记录，这个库一定要空，原因是后面会写一个维护的脚本，每天12点清空聊天室的内容，这样可以减少内存消耗，

# 配置

dockerfile已将写好，修改完config.py中的配置后可以直接使用。

# 演示网址

[这里](http://49.232.30.93:7799/)


# docker命令

## 打包命令
在项目目录下：docker build -t simole:v2 .

simole：名字
v2：版本
## 查看
docker images
## 启动命令
docker run -itd --name 新名字 -p 宿主机端口:docker环境内的端口 -d 打包好的id

例： docker run -itd --name simolev2 -p 7799:7788 -d 4e41911249c6

# v2.0测试版说明
修改了部分表结构
增加了聊天室的验证
增加了聊天室选择
修改了部分bug

# 鸣谢

此处鸣谢git上多个项目的前段借鉴，以及ajax的处理逻辑，十分感谢。
