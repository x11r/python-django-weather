import os
from common.download_last_file import get_download_last_date, set_download_last_date
from datetime import date
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.management import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from weather_data.utils.load_config import load_config

# from database import db

class Command(BaseCommand):
    help = 'CSVダウンロードコマンド'
    def add_arguments(self, parser):
        parser.add_argument('--daily', default=0, type=int, help="毎日実行する前提のコマンド")
        self.root_path = settings.WEATHER_DATA_ROOT
        return super().add_arguments(parser)
    
    def handle(self, *args, **options):
        self.notice('処理を開始します。')
        self.config = load_config()

        # 日々実行フラグ
        daily = options['daily']

        if daily > 0:
            self.daily()
        else:
            self.downloadAll()

    def daily(self):
        # 毎日実行バッチ
        # 最新数日の情報を取得

        target_year = date.today().year

        last_download_date = get_download_last_date()

        is_old_current_download = True

        # 最後のダウンロード日が今日だったら、ダウンロードは古いものと判定する
        if last_download_date == date.today().strftime('%Y-%m-%d'):
            is_old_current_download = False
        
        areas = self.config['areas']
        n = 0
        while True:
            download_all = True
            n += 1
            for area in areas:
                area_id = area['id']
                csv_path = os.path.join(self.root_path, 'daily', 'csv', str(area_id), 'data.csv')

                # 直近のダウンロードが古かったらCSVファイルを削除
                if os.path.exists(csv_path) and is_old_current_download:
                    print('== 古いCSVを削除 ==')
                    os.remove(csv_path)

                self.download(area_id=area_id, target_year=target_year, daily=True, force=is_old_current_download)

                print('== csv_path ==', csv_path)
                if not os.path.exists(csv_path):
                    print(f'ダウンロード 待ち {n}回目 Area:{area_id}')
                    download_all = False
                else:
                    print(f'ダウンロード 済み {n}回目 Area:{area_id}')

                # 最終取得日を保存
                set_download_last_date()
                
                is_old_current_download = False

            if download_all:
                print('もう一回')
                break

    def downloadAll(self):
        # 全期間をダウンロードする

        # 開始年と作業年
        start_year = self.config['default_year']['start']
        current_year = start_year

        # start_year = 2020
        print('## 開始年 ## ', start_year)

        # 都道府県一覧
        areas = self.config['areas']

        # 最終年
        end_year = date.today().year

        # 設定値の最初から今年までループ
        while current_year <= end_year:
            # 都道府県でループ
            for area in areas:
                # 都道府県ID
                area_id = area['id']

                # 開発用
                if not (area_id == 45 or area_id == 82):
                    continue
                
                print(f'#### YEAR : {str(current_year)}  AREA : {str(area_id)} ')
                        # str(area_id) + ' / ' + str(current_year))

                self.download(area_id=area_id, target_year=current_year)

            current_year += 1

    def download(self, area_id=44, target_year=0, force=False, daily=False):

        try:
            # 指定年の有無で分岐
            if target_year == 0:
                year_start = date.today().year
            else:
                year_start = target_year

            today = date.today()
            if year_start >= today.year:
                end_year = today.year

                # 2日前であれば気象情報がダウンロードできる可能性が高い
                end_date = today - relativedelta(days=2)
                end_month = end_date.month
                end_day = end_date.day
            else:
                end_year = target_year
                end_month = 12
                end_day = 31

            options = webdriver.ChromeOptions()

            # ダウンロードディレクトリ
            if daily:
                # 日々など頻繁に行う場合
                
                download_directory_base = os.path.join(self.root_path, 'daily', 'csv')

                # 情報取得の対象
                date_start = date.today() - relativedelta(days=300)
                date_end = date.today() - relativedelta(days=2)

                # CSV保存ディレクトリ
                download_directory = os.path.join(
                    download_directory_base, str(area_id))
            else:
                # 
                download_directory_base = os.path.join(self.root_path, 'csv')

                # CSV保存ディレクトリ
                download_directory = os.path.join(
                    download_directory_base, str(area_id), str(end_year))

            # CSVのパス
            download_file_path = os.path.join(download_directory,'data.csv')

            # 強制ダウンロードで、CSVファイルがある場合はCSVを削除
            if os.path.exists(download_file_path) and force:
                os.remove(download_file_path)

            if not os.path.exists(download_file_path):
                print("file_path", download_file_path)

                # ディレクトリ作成
                os.makedirs(download_directory, exist_ok=True)

                # ダウンロード先を設定するために、ブラウザ起動オプションを設定する
                prefs = {}
                prefs['download.default_directory'] = os.path.realpath(
                    download_directory)
                prefs['download.directory_upgrade'] = True
                prefs['download.extensions_to_open'] = ''
                prefs['download.prompt_for_download'] = False
                prefs['safebrowsing.enabled'] = True

                options.add_experimental_option('prefs', prefs)

                driver = webdriver.Chrome(options=options)

                # ブラウザのヘッドレス動作のフラグ
                headless_browser = False
            
                options.add_argument('--no-sandbox')
                options.add_argument('--lang=ja')
                if headless_browser:
                    options.add_argument('--headless')
                    options.add_argument('--disable-gpu')
                else:
                    driver.set_window_size(1440, 1100)

                # 設定値を取得
                url = self.config['url']
                areas = self.config['areas']

                # area_idからareaを取得
                area = next((area for area in areas if area['id'] == area_id), None)
            
                # 測定地点一覧
                stations = area['stations']

                # 都道府県のDomのID
                prefectureId = 'pr' + str(area_id)

                # 最初のURLを開く
                driver.get(url)

                # 東京都が表示されるまで待つ
                element = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, prefectureId)))
                # print('#### 東京都が表示されたはず ####')
                element.click()
                # print('東京都をクリック')

                # 表示された全ての地点の丸印でループする
                elements = WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'stmark')))

                for element in elements:
                    stationName = element.find_element(
                        By.NAME, 'stname').get_attribute('value')
                    if stationName in stations:
                        # 地点をクリックする
                        element.click()

                # 「項目を選ぶ」タブをクリック
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, 'elementButton'))).click()

                # 「項目を選ぶ」ボタン elementButton

                # 「日最高気温」のラジオボタンが表示されるのを待つ
                WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                    (By.XPATH, '//input[@name=\'element\' and @value=\'202\']')))

                # 最高気温
                driver.find_element(
                    By.XPATH, '//input[@name=\'element\' and @value=\'202\']').click()

                # 最低気温
                driver.find_element(
                    By.XPATH, '//input[@name=\'element\' and @value=\'203\']').click()

                # 「期間を選ぶ」タブをクリック  //*[@id="periodButton"]
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'periodButton'))).click()

                # print('#### 「期間を選ぶ」をクリック完了 ####')
                if daily:
                    Select(driver.find_element(By.NAME, 'iniy')).select_by_value(str(date_start.year))
                    Select(driver.find_element(By.NAME, 'inim')).select_by_value(str(date_start.month))
                    Select(driver.find_element(By.NAME, 'inid')).select_by_value(str(date_start.day))
                    Select(driver.find_element(By.NAME, 'endy')).select_by_value(str(date_end.year))
                    Select(driver.find_element(By.NAME, 'endm')).select_by_value(str(date_end.month))
                    Select(driver.find_element(By.NAME, 'endd')).select_by_value(str(date_end.day))
                    
                else:
                    Select(driver.find_element(By.NAME, 'iniy')
                        ).select_by_value(str(year_start))
                    Select(driver.find_element(By.NAME, 'inim')
                        ).select_by_value('1')
                    Select(driver.find_element(By.NAME, 'inid')
                        ).select_by_value('1')
                    Select(driver.find_element(By.NAME, 'endy')
                        ).select_by_value(str(end_year))
                    Select(driver.find_element(By.NAME, 'endm')
                        ).select_by_value(str(end_month))
                    Select(driver.find_element(By.NAME, 'endd')
                        ).select_by_value(str(end_day))

                time.sleep(1)

                # CSVファイルをダウンロード //*[@id="csvdl"]/img
                WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="csvdl"]/img'))).click()
                # print('#### ダウンロードをクリック ####')
                time.sleep(1)

                # アクセス集中のメッセージはすぐ表示される
                busy_message = self.config['busy_message']

                main_content_wait = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.ID, 'main')))
                
                if os.path.exists(download_file_path):
                    print(f'download ok. {download_file_path}')

                if busy_message in main_content_wait.text:
                    message = '#### ビジー状態 リトライを検討すべき ####'
                    print(message)
                    driver.quit()
                    raise RuntimeError(message)

                else:
                    print('#### ダウンロード完了かビジー状態 ####')
                # print('#### MAIN ####', main_content_wait.text)

                # ダウンロード完了まで待ちたい
                time.sleep(1)
                driver.quit()

        except TimeoutException as e:
            print('exception エラータイムアウト')
        except NoSuchElementException as e:
            print('exception エレメントが見つからない')
        # finally:
            # print('#### finally ####')

    # ログ出力的なもの
    def notice(self, str):
        self.stdout.write(self.style.NOTICE(str))