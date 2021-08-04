
if [ "$YUM_INSTALL_SERVICE" ]; then
  yum install mysql-devel -y
  yum install redis -y
  systemctl restart redis
fi


if [ "$CREATE_PYTHON_VENV" ]; then
  # 创建虚拟环境
  pip install virtualenv
  VENV_DIR="${APP_CODE}_venv"
  virtualenv "$VENV_DIR"
  virtualenv -p /usr/local/bin/python3.6 "$VENV_DIR"
  # 激活Python虚拟环境
  source "${VENV_DIR}/bin/activate"
fi

# 更新pip
pip install --upgrade pip

# 检查Python版本
python -V

# 检查
pip list
