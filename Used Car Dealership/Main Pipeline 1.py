# import modules required for etl
import glob
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime

# name files for easy access
tmpfile    = "dealership_temp.tmp"
logfile    = "dealership_logfile.txt"
targetfile = "dealership_transformed_data.csv"

# extract csv file function
def extract_from_csv(file_to_process):
    dataframe = pd.read_csv(file_to_process)
    return dataframe

# extract json file function
def extract_from_json(file_to_process):
    dataframe = pd.read_json(file_to_process, lines=True)
    return dataframe

# extract xml file function
def extract_from_xml(file_to_process):
    dataframe = pd.DataFrame(columns=['car_model','year_of_manufacture','price', 'fuel'])
    tree = ET.parse(file_to_process)
    root = tree.getroot()
    for person in root:
        car_model = person.find("car_model").text
        year_of_manufacture = int(person.find("year_of_manufacture").text)
        price = float(person.find("price").text)
        fuel = person.find("fuel").text
        dataframe = dataframe.append({"car_model":car_model, "year_of_manufacture":year_of_manufacture, "price":price, "fuel":fuel}, ignore_index=True)
    return dataframe

#  extract function
def extract():
    extracted_data = pd.DataFrame(columns=['car_model','year_of_manufacture','price', 'fuel'])
    
    for csvfile in glob.glob("dealership_data/*.csv"):
        extracted_data = extracted_data.append(extract_from_csv(csvfile), ignore_index=True)

    for jsonfile in glob.glob("dealership_data/*.json"):
        extracted_data = extracted_data.append(extract_from_json(jsonfile), ignore_index=True)

    for xmlfile in glob.glob("dealership_data/*.xml"):
        extracted_data = extracted_data.append(extract_from_xml(xmlfile), ignore_index=True)
        
    return extracted_data

# round to 2 decimal points (transform)
def transform(data):
        data['price'] = round(data.price, 2)
        return data

# load file
def load(targetfile,data_to_load):
    data_to_load.to_csv(targetfile)  

# log analytics
def log(message):
    timestamp_format = '%H:%M:%S-%h-%d-%Y'
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open("dealership_logfile.txt","a") as f:
        f.write(timestamp + ',' + message + '\n') 

# log job started
log("ETL Job Started")

# log extract started, call extract function, and extract ended
log("Extract phase Started")
extracted_data = extract()
log("Extract phase Ended")

# log transform started, call transform function, and transform ended
log("Transform phase Started")
transformed_data = transform(extracted_data)
log("Transform phase Ended")

# log load started, call load function, and load ended
log("Load phase Started")
load(targetfile,transformed_data)
log("Load phase Ended")

# log etl job ended
log("ETL Job Ended")