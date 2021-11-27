# Simple_chat

#### 介绍
Redis+ Python3 + flask实现简易聊天室

# Redis

#### 说明

这里面一共用到了3个redis的库，0库目前左右存储用户名的，后面有可能放弃使用，11和10是来校验token的，并且修复了一个用户可以产生多个token的情况，12库用来存储聊天记录，这个库一定要空，原因是后面会写一个维护的脚本，每天12点清空聊天室的内容，这样可以减少内存消耗，

# 配置

dockerfile已将写好，修改完config.py中的配置后可以直接使用。

# 演示网址

[这里](http://49.232.30.93:7799/)

# 鸣谢

此处鸣谢git上多个项目的前段借鉴，以及ajax的处理逻辑，十分感谢。