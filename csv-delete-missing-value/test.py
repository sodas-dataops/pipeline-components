import os
import json
from config.config import args

import pandas as pd
import sodas
import algorithm

env = 'development' if not 'APP_ENV' in os.environ else os.environ['APP_ENV']
args = args[env]

if __name__ == '__main__' :
    print('CSV Delete Missing Value')
    
    algorithm.solution('./tmp/customers.csv', './tmp/dropna_customers.csv', 
                    ['education_level'])
