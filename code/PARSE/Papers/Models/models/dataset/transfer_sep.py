import pandas as pd

# 读取tsv文件
def convert_tsv_to_csv(tsv_file_path, csv_file_path):
    df = pd.read_csv(tsv_file_path, sep='\t')

    # 将DataFrame写入csv文件
    df.to_csv(csv_file_path, index=False)

# 使用函数
convert_tsv_to_csv('test_abs.csv', 'test_abs_sc.csv')

