import algorithm

if __name__ == '__main__' :
    algorithm.solution(
                        input1=[
                            {
                                "field1": "value1",
                                "field2": {
                                    "nested1": "value2",
                                    "nested2": ["item1", "item2"]
                                }
                            },
                            {
                                "field1": "value3",
                                "field2": {
                                    "nested1": "value4"
                                }
                            }
                        ],
                        output_path='./tmp/test_output1.csv', 
                        )