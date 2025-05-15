import os
import json
from config.config import args

import pandas as pd
import sodas
import algorithm

env = 'development' if not 'APP_ENV' in os.environ else os.environ['APP_ENV']
args = args[env]

if __name__ == '__main__' :
    print('Merge!')
    
    algorithm.solution('./tmp/products.csv', './tmp/customers.csv', './tmp/transactions.csv', 
                    'customer_id', 'customer_id', 'inner')
