import zipfile
zip_ref = zipfile.ZipFile('az-medicine-dataset-of-india.zip') 
zip_ref.extractall() # extract file to directory
zip_ref.close() # close file

import pandas as pd
df=pd.read_csv('az-medicine-dataset-of-india.zip')

df

# Define the lambda function to map medicine category into values
def map_medicine_type(medicine):
    if 'tablets' in medicine:
        return 'Tablets'
    elif 'Suspension' in medicine:
        return 'Suspension'
    elif 'Injection' in medicine:
        return 'Injection'
    elif 'Capsule' in medicine:
        return 'Capsule'
    elif 'Syrup' in medicine:
        return 'Syrup'
    elif 'Oral' in medicine:
        return 'Oral'
    elif 'Ear' in medicine:
        return 'Ear Drop'
    elif 'Nasal' in medicine:
        return 'Nasal'
    elif 'gel' in medicine:
        return 'gel'
    elif 'Cream' in medicine:
        return 'Cream'
    else:
        return 'other'

# Apply the lambda function to the 'Medicine' column
df['Category'] = df['pack_size_label'].apply(lambda x: map_medicine_type(x))  # re-orgainsing the pack_size_label with mapped categorized label

df['short_composition1'].fillna('') #Preparing the df with filling/indundating with NAN

df['process_type'] = df['short_composition2'].apply(lambda x: 'Filling' if pd.notna(x) else 'Manufacturing') #Preparing the df with keyword "Filing" if NAN is identified and with "Manufacturing" if Not-Empty

df

# Apply the lambda function to the 'Medicine' column for getting strength
df['Strength']=df['short_composition1'].str.extract(r'(.*?)')

# Rename column for better understanding
df = df.rename(columns={'name': 'Product_Name','price(₹)':'Price','manufacturer_name':'Company','pack_size_label':'Size','Is_discontinued':'Active','short_composition1':'Composition1','short_composition2':'Composition2'})
df['Active']=df['Active'].apply(lambda x:1 if x==False else 0)
df = df.fillna('')


import sqlalchemy as sal
from sqlalchemy import text  # Import text for raw SQL execution

# Connect to MySQL without specifying a database
engine = sal.create_engine('mysql+pymysql://root:Mysql!2025@127.0.0.1:3306')

# Create a connection
with engine.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS Pharma_Project;"))  # Use text() for raw MySQL - DB creation
    conn.commit()  


engine = sal.create_engine('mysql+pymysql://root:Mysql!2025@127.0.0.1:3306/Pharma_Project')# Now connect to the Pharma_Project database
conn=engine.connect()

if df.empty:
    print("DataFrame is empty. No data to load.")
else:
    print(f"Loading {len(df)} records into MySQL...")
    df.to_sql(name='medicine', con=engine, index=False, if_exists='append', method='multi')#At first instance , use this DB loading entries from .csv format 
    #df.to_sql(name='medicine', con=engine, index=False, if_exists='append', method='multi') #Initializing the DATABASE with all the pharmaceutical details - 2.5L entries( Not necesasry to instatntiate at every executions
    

    print("Data successfully inserted into 'medicine' table.")

engine.dispose()

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Function to fetch alternatives for a given medicine
def find_alternative_medicines(medicine_name, engine):
    query = f"""
    SELECT
        m.Product_Name,
        m.Company,
        m.Price,
        m.Composition1,
        m.Composition2
    FROM medicine m
    WHERE m.Composition1 = (SELECT Composition1 FROM medicine WHERE Product_Name = '{medicine_name}' LIMIT 1)
    AND m.Active = 'Yes'
    ORDER BY m.Price ASC;
    """
    df_alternatives = pd.read_sql(query, con=engine)
    return df_alternatives

# User input: Medicine name
medicine_name = input("Enter Medicine Name: ")  # Example: "Alex Syrup"

# Fetch alternatives based on composition feeded
df_alternatives = find_alternative_medicines(medicine_name, engine)

# Check if any alternatives found
if df_alternatives.empty:
    print(f"No alternatives found for {medicine_name}.")
else:
    print(f"Found {len(df_alternatives)} alternatives for {medicine_name}.")
    
    # Visualization
    plt.figure(figsize=(12, 6))
    sns.barplot(y="Product_Name", x="Price", data=df_alternatives, palette="coolwarm")

    for index, row in df_alternatives.iterrows():
        plt.text(row.Price, index, f"₹{row.Price:.2f}", ha='left', va='center', fontsize=10)

    plt.xlabel("Price (₹)")
    plt.ylabel("Alternative Medicines")
    plt.title(f"Price Comparison for {medicine_name} Alternatives")
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.show()

