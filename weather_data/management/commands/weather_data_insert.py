import csv
from common.download_last_file import get_download_last_date
from datetime import datetime, date
from decimal import Decimal
from django.core.management.base import BaseCommand
from weather_data.models import Daily
from django.conf import settings
import os
import re
import sys
import time
from weather_data.utils.load_config import load_config

class Command(BaseCommand):
    help = 'CSV取り込みコマンド'

    def add_arguments(self, parser):
        self.stdout.write(self.style.NOTICE('start command'))
        parser.add_argument('--daily', default=0, type=int, help="日々実行用")
        # parser.add_argument('--count', type=int, help='処理する件数')

    def handle(self, *args, **options):

        self.stdout.write(self.style.NOTICE('処理を開始します'))
        self.root_path = settings.WEATHER_DATA_ROOT
        sys.config = load_config()

        # 日々実行用
        daily = options['daily']

        if daily > 0:
            self.daily()
        else:
            self.list_csv_files_in_directory()

    def daily(self):
        print('== daily ==')

        # ダウンロードディレクトリ
        download_dir = os.path.join(self.root_path, 'daily')

        for root, dirs, files in os.walk(download_dir):
            for file in files:
                if file.lower().endswith('.csv'):
                    # CSVファイルのパス
                    file_path = os.path.join(root, file)

                    print('== file_path ==', file_path)

                    # 都道府県IDをパスの正規表現で取得
                    # match = re.search(r'csv/(\d+)/[a-zA-Z0-9]+.csv/', file_path.replace('\\', '/'))
                    match = re.search(r'daily/csv/(\d+)/', file_path.replace('\\', '/'))
                    if match:
                        prefecture_id = int(match.group(1))

                        try:
                            with open(file_path, newline=''):
                                print('file_path', file_path)

                                self.csv_file_import(file_path, prefecture_id=prefecture_id)

                        except Exception as e:
                            print(f'error reading {file_path}: {e}')

        sys.exit()


    def list_csv_files_in_directory(self):
        # まとめてインポートする

        # CSVのディレクトリ
        base_dir = settings.WEATHER_DATA_ROOT

        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith('.csv'):
                    file_path = os.path.join(root, file)

                    # この辺りから未確認
                    try:
                        with open(file_path, newline=''):
                            self.csv_file_import(file_path, prefecture_id = 0)
                    except Exception as e:
                        print(f"error reading {file_path}: {e}")

    def import_daily(self):
        # 日々ダウンロードしたCSVを登録実行

        base_dir = settings.WEATHER_DATA_ROOT
        for root, dirs, files in os.walk(base_dir):
            print('==')


    # ログ出力的なもの
    def notice(self, str):
        self.stdout.write(self.style.NOTICE(str))

    # パスから都道府県返す
    def get_prefecture_id_from_path(self, file_path):
        match = re.search(r'csv/(\d+)/(\d{4})/', file_path.replace('\\', '/'))
        if match:
            return int(match.group(1)), int(match.group(2))
        
        return None, None
    
    # CSVファイルパスでインポートする
    def csv_file_import(self, file_path, prefecture_id=0):
        # encoding = self.detect_encoding(file_path)
        encoding = 'Shift_JIS'
        try:
            with open(file_path, newline='', encoding=encoding) as csv_file:
                if prefecture_id == 0:
                    prefecture_id, year = self.get_prefecture_id_from_path(file_path=file_path)
                else:
                    year = '0000'
        
                # todo ==== develop ====
                # if prefecture_id == 44:
                #     return
                # if not ((prefecture_id == 44 or prefecture_id == 45 or prefecture_id == 82)):
                #     return
                # if prefecture_id == 85:
                #     return
                # if prefecture_id == 12:
                #     return
                # if not (prefecture_id == 87 or prefecture_id == 91):
                #     return
        
                reader = csv.reader(csv_file)
                arr = [row for row in reader]

                # CSVファイルの中の行数
                line = 0
                for row in arr:
                    line += 1
                    if line >= 7:
                        # 日付形式変換
                        dt = datetime.strptime(row[0], '%Y/%m/%d')
                        formatted_date = dt.strftime('%Y-%m-%d')

                        # 品質情報
                        quality1 = int(row[2])
                        quality2 = int(row[5])

                        # 品質情報
                        # quality = int(row[8]) , row[11]
                        print('station_name', arr[2][2])

                        # 1か所目
                        if quality1 >=8 or quality2 >= 8:
                            try:
                                print('station_name', arr[2][2])
                                daily = {
                                    'prefecture_id': prefecture_id,
                                    'station_name': arr[2][2],
                                    'date': formatted_date,
                                    'temperature_highest': None if quality1 < 8 else row[1],
                                    'temperature_lowest': None if quality2 < 8 else row[4],
                                }

                                print('== daily object ==', daily)
                                self.register_weather_data(daily)
                            except Exception as e:
                                print(f'error {e}')


                        # 2か所目
                        if 13 <= len(row):
                            quality1 = int(row[8])
                            quality2 = int(row[11])

                            # 品質情報が8以上の時だけ登録
                            if quality1 >= 8 or quality2 >= 8:
                                daily = {
                                    'prefecture_id': prefecture_id,
                                    'station_name': arr[2][7],
                                    'date': formatted_date,
                                    'temperature_highest': None if quality1 < 8 else row[7],
                                    'temperature_lowest': None if quality2 < 8 else row[10],
                                }

                                self.register_weather_data(daily)

                now = datetime.now().strftime('%Y-%m-%D %H:%m:%S')
                self.notice(f"登録完了  {prefecture_id} {year} {now}")
                # self.notice(dailies)
                time.sleep(1 / 4)

        except Exception as e:
            print(f'error reading {file_path}: {e}')
            time.sleep(2)
            
    def register_weather_data(self, daily):
        try:
            # Upsert実行
            temperature_highest = None if not daily['temperature_highest'] else Decimal(daily['temperature_highest'])
            temperature_lowest = None if not daily['temperature_lowest'] else Decimal(daily['temperature_lowest'])

            obj, create = Daily.objects.update_or_create(
                prefecture_id = daily['prefecture_id'],
                station_name = daily['station_name'],
                date = daily['date'],
                defaults={
                    'temperature_highest': temperature_highest,
                    'temperature_lowest': temperature_lowest,
                }
            )

        except Exception as e:
            print(f"{daily} エラー {e}")
