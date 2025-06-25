import os
import csv
from django.core.management.base import BaseCommand
from weather_data.models import Daily
from django.conf import settings

import time
import re
from datetime import datetime
from decimal import Decimal

class Command(BaseCommand):
    help = 'CSV取り込みコマンド'

    def add_arguments(self, parser):
        self.stdout.write(self.style.NOTICE('start command'))
        # parser.add_argument('--count', type=int, help='処理する件数')

    def handle(self, *args, **options):

        self.stdout.write(self.style.NOTICE('処理を開始します'))

        self.list_csv_files_in_directory()

    def list_csv_files_in_directory(self):

        # csv_dir = settings.WEATHER_DATA_ROOT
        base_dir = os.path.join(settings.WEATHER_DATA_ROOT)
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith('.csv'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, newline=''):
                            self.csv_file_import(file_path)
                    except Exception as e:
                        print(f"error reading {file_path}: {e}")

    # ログ出力的なもの
    def notice(self, str):
        self.stdout.write(self.style.NOTICE(str))

    # パスから都道府県返す
    def get_prefecture_id_from_path(self, file_path):
        match = re.search(r'weather_data_csv/(\d+)/(\d{4})/', file_path.replace('\\', '/'))
        if match:
            return int(match.group(1)), int(match.group(2))
        
        return None, None
    
    # CSVファイルパスでインポートする
    def csv_file_import(self, file_path):
        # encoding = self.detect_encoding(file_path)
        encoding = 'Shift_JIS'
        try:
            with open(file_path, newline='', encoding=encoding) as csv_file:
                prefecture_id, year = self.get_prefecture_id_from_path(file_path=file_path)

                # todo ==== develop ====
                # if prefecture_id == 44:
                #     return
                # if prefecture_id == 45:
                #     return
                # if prefecture_id == 85:
                #     return
                # if prefecture_id == 12:
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

                        if quality1 >= 8 or quality2 >= 8:
                            daily = {
                                'prefecture_id': prefecture_id,
                                'date': formatted_date,
                                'station_name': arr[2][2],
                                'temperature_highest': None if quality1 < 8 else row[1],
                                'temperature_lowest': None if quality2 < 8 else row[4],
                            }

                            self.register_weather_data(daily)

                        # 品質情報
                        # quality = int(row[8]) , row[11]
                        # 2か所目
                        if 7 in row:
                            quality1 = int(row[8])
                            quality2 = int(row[11])
                            # 品質情報が8
                            if quality1 >= 8 or quality2 >= 8:
                                daily = {
                                    'prefecture_id': prefecture_id,
                                    'station_name': arr[2][7],
                                    'date': formatted_date,
                                    'temperature_highest': None if quality1 < 8 else row[7],
                                    'temperature_lowest': None if quality2 < 8 else row[10],
                                }

                                self.register_weather_data(daily)

                self.notice(f"登録完了  {prefecture_id} {year}")
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

            if create:
                print(f"新規登録: {obj}")
            else:
                print(f"更新: {obj}")

        except Exception as e:
            print(f"{daily} エラー {e}")
