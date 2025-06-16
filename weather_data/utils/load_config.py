import yaml
import os
from django.conf import settings

def load_config():
    
    file_name = 'config.yml'
    file_path = os.path.join(settings.BASE_DIR, file_name)

    # 日本語を含む場合はエンコードが必要
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)
    
