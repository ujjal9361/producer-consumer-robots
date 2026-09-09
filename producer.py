from robocorp.tasks import task
from robocorp import workitems
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.JSON import JSON

http = HTTP()
table = Tables()
json = JSON()


TRAFFIC_JSON_FILE_PATH = "output/traffic.json"


# JSON data keys 
YEAR_KEY =  "TimeDim"
FATALITY_RATE_KEY = "NumericValue"
COUNTRY_KEY= "SpatialDim"
GENDER_KEY = "Dim1"





@task
def produce_traffic_data():
    """
    Inhuman Insurance, Inc. Artificial Intelligence System automation.
    Produces traffic data work items.
    """
    # Downloads the raw data of the traffic from the traffic API
    http.download(url="https://github.com/robocorp/inhuman-insurance-inc/raw/main/RS_198.json",
                      target_file=TRAFFIC_JSON_FILE_PATH,
                      overwrite= True)
    traffic_data = load_traffic_data_as_table()
    # table.write_table_to_csv(traffic_data, "output/test.csv")
    
    # Filter based on fatality rate, gender and sort such that data of latest date comes first
    filtered_traffic_data = filter_and_sort_traffic_data(traffic_data)
    # table.write_table_to_csv(filtered_traffic_data, "output/test.csv")

    #Provides the latest data for each country
    filtered_traffic_data = get_latest_data_by_country(filtered_traffic_data)

    payloads = create_work_item_payloads(filtered_traffic_data)

    save_work_item_payloads(payloads)


def load_traffic_data_as_table():
    #Fetches the json data from traffic.json file, convert it into RPA table, and return it.
    json_data = json.load_json_from_file(TRAFFIC_JSON_FILE_PATH)
    return table.create_table(json_data["value"])
    
def filter_and_sort_traffic_data(traffic_data):
    """ Filter based on fatality rate, gender and sort such that data of latest date comes first"""
    max_fatality_rate = 5.0
    both_sexes = "BTSX"
    # The fatality rate needs to be less than 5 (since insurance is targetting places where claim for insurance will be least )
    table.filter_table_by_column(traffic_data,FATALITY_RATE_KEY, "<", max_fatality_rate)
    #Company is considering fatality rate that is of both of the sexes only(Male and Female) 
    table.filter_table_by_column(traffic_data, GENDER_KEY,"==", both_sexes)
    #Sorting the data in descending order of Time such that latest data comes first
    table.sort_table_by_column(traffic_data,YEAR_KEY, False)
    return traffic_data

def get_latest_data_by_country(data):
    """Group the latest data by country, and return the first row of each group. Since the data we received is already sorted such that latest data comes first, the first row is the latest data for each country """
    data = table.group_table_by_column(data, COUNTRY_KEY)
    latest_data_by_country = []
    for group in data:
        first_row = table.pop_table_row(group)
        latest_data_by_country.append(first_row)
    return latest_data_by_country

    

def create_work_item_payloads(data):
    payloads= []
    for row in data:
        payload = dict(
            country =row[COUNTRY_KEY] ,
            year=row[YEAR_KEY] ,
            rate =row[FATALITY_RATE_KEY] ,
        )
        payloads.append(payload)
    return payloads

def save_work_item_payloads(payloads):
    for payload in payloads:
        variables = dict(traffic_data=payload)
        workitems.outputs.create(variables)







    




 


