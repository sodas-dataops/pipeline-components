import os
import json
from config.config import args

import pandas as pd
import sodas
import algorithm

from io import StringIO

env = 'development' if not 'APP_ENV' in os.environ else os.environ['APP_ENV']
args = args[env]

if __name__ == '__main__' :
    print('Merge!')
    
    with open('./tmp/products.csv', 'r', encoding='utf-8') as f:
        left_table = StringIO(f.read())
    with open('./tmp/customers.csv', 'r', encoding='utf-8') as f:
        right_table = StringIO(f.read())
        
    algorithm.solution(
        left_table=left_table, 
        right_table=right_table, 
        output_filename='./tmp/transactions.csv', 
        left_on='customer_id', 
        right_on='customer_id', 
        how='inner'
    )
