#!/bin/sh
# 当前脚本目录
SCRIPT_DIR=$(dirname $(readlink -f "$0"))

cat << EOF
SCRIPT_DIR -> "$SCRIPT_DIR"
EOF

${SCRIPT_DIR}/prepare_services.sh

${SCRIPT_DIR}/install.sh

cat ${SCRIPT_DIR}/code_quality.sh
${SCRIPT_DIR}/code_quality.sh
