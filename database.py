import pandas as pd
from pymongo import MongoClient
from pymongo.database import Database
import data_manipulation

_DBUSERNAME = "dvrakas"
_DBPASSWORD = "AuthThesis"


def get_database() -> Database:
    """
    Establishes a connection with the MongoDB database.

    :return: (Database)The 'ThesisDB' database from the online cluster.
    """
    CONNECTION_STRING = f"mongodb+srv://{_DBUSERNAME}:{_DBPASSWORD}@cluster73885.u7exk8j.mongodb.net/?retryWrites" \
                        f"=true"
    client = MongoClient(CONNECTION_STRING)
    return client['ThesisDB']


def save_data(db, form1, form2) -> dict:
    """
    Organizes the data from the HTML forms into a dictionary and saves it to the "New_entries" database collection.

    :param db: (pymongo.database) The MongoDB database connection.
    :param form1: (json file) The data from the first HTML form.
    :param form2: (json file) The data from the second HTML form.
    :return: (dict) A dictionary with all the data.
    """
    record = data_manipulation.transform_data(form1, form2)
    db["New_entries"].insert_one(record)
    return record


def retrieve_data(db, collection, condition=None) -> pd.DataFrame:
    """
    Returns a subset of the database collection based on the given condition.

    :param db: (pymongo.database) The MongoDB database connection.
    :param collection: (str) The name of the collection stored in the database.
    :param condition: (dict) A database query.
    :return: (pd.DataFrame) The matched records in the form of a pandas data frame.
    """
    if condition is None:
        condition = {}

    collection = db[collection]
    cursor = collection.find(condition)
    dataFrame = pd.DataFrame(list(cursor))
    dataFrame.reset_index(inplace=True, drop=True)

    return dataFrame
