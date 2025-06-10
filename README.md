
# Django

Djangoの勉強

## pythonのバージョン

```sh
pyenv local 3.12.9
pyenv --version
python --version
```

## install pip

```sh
wget https://bootstrap.pypa.io/get-pip.py -O get-pip.py
python get-pip.py
```

## virtualenv

```sh
pip install virtualenv
virtualenv weather_data
```

バージョン確認

```sh
python -m django --version
```

<!-- ```sh
cd weather_data
``` -->

<!-- Windowsの場合は下記で行けるはず。(アクティベートか) -->

<!-- ```sh
./Script/activate.bat
``` -->

<!-- MacOSでは`source ./Script/activate` で良さそう。 -->

## Djangoのインストール

project1の中で実行する。

```sh
pip install Django==5.2.2
```

プロジェクト作成

```sh
django-admin startproject weather_data .
```

気象情報のアプリの作成

```sh
python manage.py startapp weather_data
```

サーバー起動

```sh
python manage.py runserver
```

## メモ

### マイグレーション

モデルファイル(models.py)からマイグレーションファイルを作成。

```sh
python manage.py makemigrations weather_data
```

マイグレーション実行

```sh
python manage.py migrate weather_data
```

```sh
python manage.py showmigrations
```

### キャッシュ削除

対話モードでキャッシュ削除を行う。

```sh
python manage.py shell
from django.core.cache import cache
cache.clear()
```

## そのほかのpip

```sh
php install python-decouple
```

python -m pip install chardet

- chardet
- Django==5.2.2
- mysqlclient
- python-decouple
- virtualenv

### コマンド

