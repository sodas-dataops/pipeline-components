from core import algorithm_csv_date_time_formatter as algorithm

if __name__ == '__main__' :
    algorithm.solution(
        './tmp/customers_and_transactions.csv', 
        './tmp/formatted.csv',
        ['transaction_date'], 
        'append',
        '_new',
        '%Y-%m-%d',
        '%Y-%m'
    )