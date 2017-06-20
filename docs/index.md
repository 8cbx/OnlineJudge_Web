# 欢迎来到 OnlineJudge_Web

[![Build Status](https://travis-ci.org/8cbx/OnlineJudge_Web.svg?branch=master)](https://travis-ci.org/8cbx/OnlineJudge_Web)
[![Coverage Status](https://coveralls.io/repos/github/8cbx/OnlineJudge_Web/badge.svg?branch=master)](https://coveralls.io/github/8cbx/OnlineJudge_Web?branch=master)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL--3.0-green.svg)](http://www.gnu.org/licenses/agpl-3.0)

Online Judge用于学校程序设计竞赛的评判工作，本部分为Web端

## 项目说明

- 整个项目分为Web端和Judge端，基于flask框架
- Web端可使用docker进行快速部署
- 部署方式可以选择为单机部署(单Web单Judge), 多机部署(单Web多Judge和单负载均衡+多Web多Judge)三种方案
- 依赖celery和rabbitmq进行部分任务的分发和处理
- Under AGPL v3 License

## Web端说明

- Web端主要分为7大模块，功能上还存在不完善的地方，主要在一些细节方面
- 比赛模块的排行榜功能尚存在效率低下的问题，最好改成celery中的异步计算
- Web端的数据库中预留了一些设想所需要的字段，如rating等，这些内容可以在后续的开发中加上对应的功能

## Judge端说明

- Judge端当前可以评判ACM类型题目、NOI类型题目
- Judge端当前采用的是[ljudge项目](https://github.com/quark-zju/ljudge)开源的评测机，外面套了一层评判结果的解析和API的调用以及评测任务的调度，如有需要可以调整评测机的使用
- Judge端当前还未实现Special Judge的工作，不过ljudge支持Spical Judge，当前缺少这方面的封装调用工作

## 参考书籍和文档

- 