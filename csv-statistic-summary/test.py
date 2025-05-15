import algorithm

if __name__ == '__main__' :
    algorithm.solution(
                        './tmp/customers_and_transactions.csv', 
                        './tmp/grouped_by_customer_purchase.csv', 
                        ['customer_id'],
                        ['price'],
                        ['sum']
                        )