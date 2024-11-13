# setup_feast.py 수정
from airflow.hooks.base import BaseHook
import json
import os

conn = BaseHook.get_connection('google_cloud_default')
print("Connection Extra:", conn.extra_dejson)  # 디버깅을 위해 추가

# extra에서 keyfile_dict 가져오기 전에 체크
if 'extra__google_cloud_platform__keyfile_dict' in conn.extra_dejson:
    credentials_dict = json.loads(conn.extra_dejson['extra__google_cloud_platform__keyfile_dict'])
elif 'keyfile_dict' in conn.extra_dejson:
    credentials_dict = json.loads(conn.extra_dejson['keyfile_dict'])
else:
    raise ValueError("GCP credentials not found in connection")

with open('/tmp/gcp-credentials.json', 'w') as f:
    json.dump(credentials_dict, f)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/tmp/gcp-credentials.json'
