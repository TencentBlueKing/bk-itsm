#!/bin/bash

# 单元测试
# coverage 需要统计覆盖率的文件（夹）
COVERAGE_INCLUDE_MODULES="itsm/*"

# coverage 忽略文件
COVERAGE_OMIT_PATH="*/test/*,*/virtualenv/*,*/venv/*,*/migrations/*,*/tests/*,*/helper/*,*/blueking/*,*/business_rules/*,*/common/*,*/iam/*,*/pipeline/*"

# 删除coverage历史归档文件
coverage erase

TEST_LOGS=$(coverage run --include "$COVERAGE_INCLUDE_PATH" --omit "$COVERAGE_OMIT_PATH" ./manage.py test itsm.tests  2>&1)
echo "${TEST_LOGS}"
TEST_RESULT=$(echo "${TEST_LOGS}" | grep -Ev "'errors'|Consumer" | grep -E "Ran|OK\n|failures|errors")
TEST_TIME=''
TEST_COUNT=0
TEST_SUCCESS=0
TEST_FAILURE=0
TEST_ERROR=0

echo $TEST_RESULT
TEST_TIME=$(echo $TEST_RESULT | awk '{print $5}')
TEST_COUNT=$(echo $TEST_RESULT | awk '{print $2}')
if [[ $TEST_RESULT =~ "OK" ]];
then
  TEST_SUCCESS=$(echo $TEST_RESULT | awk '{print $2}')
else
  if [[ $TEST_RESULT =~ "failures" ]];
  then
    echo $TEST_RESULT | awk '{print $7}'
    echo $TEST_RESULT | awk '{print $7}' | grep -Po '\d+'
    TEST_FAILURE=$(echo $TEST_RESULT | awk '{print $7}' | grep -Po '\d+')
    if [[ $TEST_RESULT =~ "errors" ]]
    then
      TEST_ERROR=$(echo $TEST_RESULT | awk '{print $8}' | grep -Po '\d+')
    fi
  else
    TEST_ERROR=$(echo $TEST_RESULT | awk '{print $7}' | grep -Po '\d+')
  fi
  TEST_SUCCESS=$(printf "%d" $((TEST_COUNT-TEST_FAILURE-TEST_ERROR)))
fi

echo "测试时长: $TEST_TIME"
echo "单元测试数: $TEST_COUNT"
echo "成功数: $TEST_SUCCESS"
echo "失败数: $TEST_FAILURE"
echo "报错数: $TEST_ERROR"

TEST_NOT_SUCCESS_COUNT=$[TEST_NOT_SUCCESS_COUNT+TEST_FAILURE]
TEST_NOT_SUCCESS_COUNT=$[TEST_NOT_SUCCESS_COUNT+TEST_ERROR]

echo "未通过数: $TEST_NOT_SUCCESS_COUNT"


if [[ $TEST_NOT_SUCCESS_COUNT -ne 0 ]];
then
  exit 1
fi

# 打印报告
coverage report --include "$COVERAGE_INCLUDE_PATH" --omit "$COVERAGE_OMIT_PATH"

exit 0
