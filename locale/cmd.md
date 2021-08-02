# 安装软件：
	pip install babel
	安装gettext(参阅ppt)

# 创建语言目录和配置

>>> mkdir locale
>>> cd locale && touch babel.cfg
>>> cat babel.cfg

```
# Extraction from Python source files
[python: home_application/**.py]

# Extraction from Mako templates
[mako: **/templates/**.*]

# [mako: myproj/templates/**.html]
input_encoding = utf-8
```

# 生成语言文件
python manage.py makemessages  -d djangojs -v 3 --keep-pot -i '*webpack*' --no-location -l en
python manage.py makemessages  -d djangojs -v 3 --keep-pot -i '*webpack*' --no-location -l zh_CN

# 标记翻译内容：python/mako/js，vue不支持扫描
pybabel extract -F locale/babel.cfg --copyright-holder=blueking . -o django.pot
pybabel init -i django.pot -D django -d locale -l en
pybabel init -i django.pot -D django -d locale -l zh_CN

# 人工整理vue需要翻译的内容，并按照po文件的格式分别追加到各语言目录下的djangojs.po(t)文件中
# 将locale目录下的翻译文件交给翻译人员翻译（或者自行翻译），拿到翻译好的文件后继续下面的步骤

# 编译语言文件
django-admin compilemessages

# 更新
pybabel extract -F locale/babel.cfg --copyright-holder=blueking . -o django.pot
pybabel update -i django.pot -d locale -D django
django-admin makemessages -d djangojs

# 或者仅更新某种语言（如en）
pybabel update -i django.pot -d locale -D django -l en
django-admin  makemessages -d djangojs –l en

