import data_manipulation
import database
import numpy as np
import Knn
import pandas as pd
from sklearn.cluster import AgglomerativeClustering

_NUMBER_OF_NEIGHBORS = 1


def apply_algorithm(db, record) -> tuple:
    """
    Fetches all the records from the 'Active_data' database collection and performs the 1-Nearest-Neighbors algorithm
    to classify the given record to the closest cluster.
    After that, calculates the expected energy consumption by finding the mean consumption from the records within
    the cluster.

    :param db: (pymongo.database)The MongoDB database connection.
    :param record: (dict)The record to be classified.
    :return: (tuple)The mean consumption from the cluster and a pandas data frame with all the data.
    """
    dataFrame = database.retrieve_data(db, "Active_data", {})
    labels = dataFrame["label"]

    data_manipulation.preprocess_pipeline(db, record)

    dataFrame_processed = pd.concat([dataFrame, pd.DataFrame(record, index=[0])], ignore_index=True)
    dataFrame_processed.fillna(value=0, inplace=True)
    dataFrame_processed.drop(["_id", "Kwh/day/m2", "Heating Source", "label"], axis=1, inplace=True)
    dataFrame_processed = dataFrame_processed.to_numpy()

    label = Knn.Knn(record=dataFrame_processed[-1], k=_NUMBER_OF_NEIGHBORS, data=dataFrame_processed[:-1],
                    labels=labels)
    prediction = np.mean(dataFrame[dataFrame.loc[:, "label"] == label]["Kwh/day/m2"])

    return prediction, dataFrame


def train_clustering_algorithm(db, heating_source) -> None:
    """
    Fetches records from the 'Active_data' database collection based on the 'heating_source' argument and performs an
    agglomerative clustering algorithm on them.
    It updates each record back to the database with the calculated label.

    :param db: (pymongo.database)The MongoDB database connection.
    :param heating_source: (str)The heating source to filter the records.
    :return: (None)
    """
    dataFrame = database.retrieve_data(db, "Active_data", {"Heating Source": f"{heating_source}"})
    IDs = dataFrame["_id"]

    dataFrame_processed = np.array(dataFrame.drop(["_id", "Kwh/day/m2", "Heating Source"], axis=1))
    if heating_source == "Yes":
        labels = AgglomerativeClustering(linkage="average", metric="l1", n_clusters=3).fit_predict(
            dataFrame_processed)
    elif heating_source == "No":
        labels = AgglomerativeClustering(linkage="average", metric="euclidean", n_clusters=4).fit_predict(
            dataFrame_processed)
    else:
        raise ValueError("Heating source should be: {Yes/No}")

    for Id, label in zip(IDs, labels):
        db["Active_data"].update_one({"_id": Id}, {"$set": {"label": int(label)}})


"""
Run main to re-calculate the clusters with records from the 'Active_data' database collection.
"""
if __name__ == "__main__":
    database = database.get_database()
    train_clustering_algorithm(db=database, heating_source="Yes")
    train_clustering_algorithm(db=database, heating_source="No")
