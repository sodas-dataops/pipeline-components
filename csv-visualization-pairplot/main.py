import os
import requests
import re
import json
from minio import Minio
from config.config import args

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

env = 'development' if not 'APP_ENV' in os.environ else os.environ['APP_ENV']
args = args[env]

# Get access token via refresh_token.
def get_access_token (base_url, user_name, refresh_token):
    url='http://' + base_url + '/api/v1/gateway/authentication/user/refreshUser'
    res = requests.post(url,
        data={'id': user_name, 'refreshToken': refresh_token})
    return json.loads(res.content.decode('ascii'))['accessToken']

# Download data file.
def download_data_file (base_url, access_token, storage_id, bucket_name, object_name, file_name):
    url = 'http://' + base_url + '/api/v1/devops/development/environment/minio/object/download'
    params = {
        'storageId': storage_id,
        'bucketName': bucket_name,
        'objectName': object_name
    }
    headers = {
        'Accept' : 'text/csv; charset=utf-8',
        'Content-Type': 'text/csv; charset=utf-8',
        'Authorization': 'Bearer ' + access_token
    }
    with open('.tmp/' + file_name, "wb") as file:
        res = requests.get(url, headers=headers, params=params)
        file.write(res.content)
        print('The file downloads successfully.')

# Upload to MinIO.
def get_connection (base_url, access_token, storage_id):
    url = 'http://' + base_url + '/api/v1/devops/development/environment/get'
    params = {
        'id': storage_id
    }
    headers = {
        'accept': 'application/json', 
        'Authorization': 'Bearer ' + access_token
    }
    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        raise Exception('Unauthorized. Cannot access API.')
    storage = json.loads(res.content.decode('ascii'))
    connection = { # to be corrected
        'end_point': [o['host'] for o in storage['sandbox']['ingress'] if o['servicePort'] == 9000][0],
        'port': [o['clusterAccessPort'] for o in storage['sandbox']['ingress'] if o['servicePort'] == 9000][0],
        'use_ssl': False,
        'access_key': [o['value'] for o in storage['config']['environments'] if o['name'] == 'MINIO_ACCESS_KEY'][0],
        'secret_key': [o['value'] for o in storage['config']['environments'] if o['name'] == 'MINIO_SECRET_KEY'][0]    }
    return connection

def upload_data_file (minio_client, bucket_name, object_name, file_name):
    minio_client.fput_object(bucket_name, object_name, '.tmp/' + file_name)
    print('The file uploads successfully.')

data_file_name = 'data.csv'
image_file_name = 'fig.png'

download_data_file(
    base_url=args['input1']['base_url'], 
    access_token=get_access_token(args['input1']['base_url'], args['input1']['user_name'], args['input1']['refresh_token']), 
    storage_id=args['input1']['storage_id'], 
    bucket_name=args['input1']['bucket_name'], 
    object_name=args['input1']['object_name'], 
    file_name=data_file_name)

dataFile = pd.read_csv('.tmp/' + data_file_name)

feature_names = args['feature_names']
target_name = args['target_name']
df = pd.DataFrame(data=dataFile[feature_names], columns=feature_names)
df['target'] = dataFile[[target_name]]

x_data = df.iloc[:, :-1]
y_data = df.iloc[:, [-1]]

sns.pairplot(df, hue="target", height=3)
plt.savefig('.tmp/' + image_file_name, dpi=300)

connection_info = get_connection(
    base_url=args['output1']['base_url'],
    access_token=get_access_token(args['output1']['base_url'], args['output1']['user_name'], args['output1']['refresh_token']),
    storage_id=args['output1']['storage_id']
)
minio_client = Minio(endpoint=connection_info['end_point']+':'+str(connection_info['port']), secure=connection_info['use_ssl'], access_key=connection_info['access_key'], secret_key=connection_info['secret_key'])
upload_data_file(minio_client, args['output1']['bucket_name'], args['output1']['object_name'], image_file_name)