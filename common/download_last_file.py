import os
import re
from datetime import datetime, date
from django.conf import settings
from weather_data.utils.load_config import load_config
# 気象情報ダウンロードの最終ダウンロード日付を保存するファイルの操作を行う共通ロジック

# プロジェクトの共有ディレクトリから、daily のディレクトリ
daily_download_dir = 'daily'
download_last_date_file = 'download_last.txt'

root_path = settings.WEATHER_DATA_ROOT
download_last_file_path = os.path.join(root_path, daily_download_dir, download_last_date_file)

# 最終ダウンロード日を確認
def get_download_last_date():
    # 返却の初期値
    last_download_date = '1800-01-01'

    if os.path.exists(download_last_file_path):
        f = open(download_last_file_path, 'r')
        s = f.read()

        result = re.match(r'(\d{4})\-(\d{2})\-(\d{2})$', s)

        if result:
            # マッチした場合
            date_string = date(int(result.group(1)), int(result.group(2)), int(result.group(3)))
            f.close()

            if date_string:
                last_download_date = date_string.strftime('%Y-%m-%d')
        
    return last_download_date

# 最終ダウンロード日を保存
def set_download_last_date():
    if os.path.exists(download_last_file_path):
        today_str = date.today().strftime('%Y-%m-%d')
        print('== today ==', today_str)
        f = open(download_last_file_path, 'w')
        f.write(today_str)
        f.close()

    # 完了
