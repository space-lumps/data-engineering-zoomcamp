import sys
import pandas as pd

# sys.argv passes command line arguments to the script, eg. when running 'python pipeline.py arg1 arg2', then argv will be ['pipeline.py', 'arg1', 'arg2']
print('arguments', sys.argv)

# first argument after the script name is set to month
month = int(sys.argv[1])

# build a dataframe with sample data
df = pd.DataFrame({"day": [1, 2], "num_passengers": [12, 32]})
df['month'] = month
print(df.head())

#save output to parquet file
# index=False to avoid saving the index as a separate column
# parquet is a binary columnar storage file format often used in data processing
df.to_parquet(f'output_{month}.parquet', index=False)

print(f'hello pipeline, month is {month}')