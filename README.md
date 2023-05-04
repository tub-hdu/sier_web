# 基于flask+requests个人博客系统

## 1.基本环境搭建

```python
    1.本人使用的系统是 Centos7
    2.python环境
        2.1 安装python3.6
        2.2 安装pip工具
    3.安装mysql数据库 使用的是mysql 5.7 charset=utf8
    4.建立相关数据库及表
```

## 2.安装教程(推荐安装环境：Centos7,python版本要超过3.4)

    1.首先你应该创建了一个blog数据库（utf-8格式）,然后修改config.py里面的user、passwd、db
    2.初始化数据库：python manage.py db init
    3.生成数据库语句：python manage.py db migrate
    4.创建数据库：python manage.py upgrade

运行：`./start.sh`
