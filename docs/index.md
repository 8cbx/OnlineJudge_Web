# 欢迎来到 OnlineJudge_Web

[![Build Status](https://travis-ci.org/8cbx/OnlineJudge_Web.svg?branch=master)](https://travis-ci.org/8cbx/OnlineJudge_Web)
[![Coverage Status](https://coveralls.io/repos/github/8cbx/OnlineJudge_Web/badge.svg?branch=master)](https://coveralls.io/github/8cbx/OnlineJudge_Web?branch=master)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL--3.0-green.svg)](http://www.gnu.org/licenses/agpl-3.0)

Online Judge用于学校程序设计竞赛的评判工作，本部分为Web端

## 项目说明

- 整个项目分为Web端和Judge端
- Web端可使用docker进行快速部署
- 部署方式可以选择为单机部署(单Web单Judge), 多机部署(单Web多Judge和单负载均衡+多Web多Judge)三种方案
- 依赖celery和rabbitmq进行部分任务的分发和处理
- Under AGPL v3 License
