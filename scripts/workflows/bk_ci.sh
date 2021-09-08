#!/bin/bash
# 当前脚本目录
SCRIPT_DIR=$(dirname $(readlink -f "$0"))

cat << EOF
SCRIPT_DIR -> "$SCRIPT_DIR"
EOF

${SCRIPT_DIR}/prepare_services.sh

${SCRIPT_DIR}/install.sh

${SCRIPT_DIR}/code_quality.sh

if [[ $? -ne 0 ]];
then
  echo "单元测试未通过!"
  exit 1
else
  echo "单元测试已通过"
fi
