import sys
import pandas as pd
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    '''
    Loads and merges the input datasets
    '''
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    df = pd.merge(messages, categories, on='id')
    return df


def clean_data(df):
    '''
    Clean the datasets, split categories columns into separate, clearly named columns, convert values to binary, drop duplicates
    '''
    categories = df['categories'].str.split(';', expand=True)
    row = categories.iloc[0]
    category_colnames = row.apply(lambda x: x[:-2])
    categories.columns = category_colnames
    for column in categories.columns:
        # set each value to be the last character of the string
        categories[column] =  categories[column].str[-1]
        # convert column from string to numeric
        categories[column] = categories[column].astype(int)
        
    df.drop(['categories'], axis=1, inplace=True)
    df = pd.concat([df, categories], axis=1, sort=False)
    df['related'] = df['related'].map({0:0, 1:1, 2:1})
    df.drop_duplicates(inplace=True)
    df.fillna(value=0, inplace=True)
    return df

def save_data(df, database_filename):
    '''
    Store the clean data into a SQLite database in the specified database file path
    '''
    engine = create_engine('sqlite:///' + database_filename)
    df.to_sql('df', engine, index=False)

def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]
        
        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')

if __name__ == '__main__':
    main()