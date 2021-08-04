#!/bin/sh

# 单元测试
# coverage 需要统计覆盖率的文件（夹）
COVERAGE_INCLUDE_MODULES="itsm/*,config/*,urls.py,settings.py"

# coverage 忽略文件
COVERAGE_OMIT_PATH="*/test/*,*/virtualenv/*,*/venv/*,*/migrations/*,*/tests/*"

# 删除coverage历史归档文件
coverage erase

# -p: 表示覆盖率统计文件追加机器名称，进程pid和随机数，用于区分不同模块之间生成的.coverage文件
coverage run -p --include "$COVERAGE_INCLUDE_PATH" --omit "$COVERAGE_OMIT_PATH" ./manage.py test itsm.tests

# 将多个模块的覆盖率报告进行整合
coverage combine

# 打印报告
coverage report --include "$COVERAGE_INCLUDE_PATH" --omit "$COVERAGE_OMIT_PATH"
