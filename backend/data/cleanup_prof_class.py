import pandas as pd

df = pd.read_csv('prof_class_aggregates.csv')

#combining first and last name into one column
df['Instructor_Name'] = df['firstName'] + ' ' + df['lastName']
df = df.drop(columns=['firstName', 'lastName'])

"seperating the class to match the sections_spring.csv file format for future matching"
df[['Subject', 'Catalog Number']] = df['class'].str.extract(r'(\D+)(\d+)', expand=True)
df = df.drop(columns=['class'])

"reordering columns so it's easier to read"
cols = df.columns.tolist()
cols.insert(1, cols.pop(cols.index('Instructor_Name')))
cols.insert(2, cols.pop(cols.index('Subject')))
cols.insert(3, cols.pop(cols.index('Catalog Number')))
df = df[cols]


df.to_csv('prof_class_aggregates_cleaned.csv', index=False)
