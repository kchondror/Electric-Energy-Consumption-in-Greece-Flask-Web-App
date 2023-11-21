import datetime as dt
from datetime import datetime

"""
Dictionaries used to map categorical attributes to numeric values.
"""
_MAP_DWELLING = {"Family House": 1.0, "Semidetached": 0.7, "Townhome": 0.4, "Apartment": 0.0}
_MAP_AGE = {"0 - 5": 0, "6 - 15": 0.33, "16 - 30": 0.66, "30+": 1.0}

"""
Lists that contains the attribute labels based on their type.
"""
_NUMERICAL_LABELS = ['Dwelling Grade', 'Bedrooms', 'Old', 'Occupants',
                     'Children', 'Teenagers', 'Adults', 'Elders', 'Ainc', 'Adec', 'Agauge', 'Fulltimers', 'Parttimers',
                     'Grads', 'PostGrads', 'Education Index']
_ONEHOT_LABELS = ['Income', 'Recycling', 'Energy Class', 'Thermostats', 'Smart Plugs', 'Awareness']
_ORDINAL_LABELS = ['Water Heater']
_COLUMNS = _NUMERICAL_LABELS + _ONEHOT_LABELS + _ORDINAL_LABELS


def min_max_scaler(value, min_max_tuple, min_max_range=(0, 1)) -> float:
    """
    Performs scaling to the given value within the range [0,1].

    :param value: (float) The value to be scaled.
    :param min_max_tuple: (tuple) The min and max values of the attribute that the value is part of.
    :param min_max_range: (tuple) The scale range.
    :return: (float) The processed value.
    """
    x_std = (value - min_max_tuple[0]) / (min_max_tuple[1] - min_max_tuple[0])
    x_scaled = x_std * (min_max_range[1] - min_max_range[0]) + min_max_range[0]
    return x_scaled


def preprocess_pipeline(db, record) -> None:
    """
    Preprocesses the given record by applying a pipeline of transformations for the numerical and categorical data.
    Transformations:
    -> min_max_scaler : for the _NUMERICAL_LABELS
    -> ordinal_encoding : for the _ORDINAL_LABELS and
    -> One_hot_encoding : for the _ONEHOT_LABELS.

    :param db: (pymongo.database)The MongoDB database connection.
    :param record: (dict)A dictionary with the data from the filled HTML forms.
    :return: (None)
    """
    min_max_info = db["attributes_info"].find_one()

    for attribute in [element for element in _NUMERICAL_LABELS if element not in ['Dwelling Grade', 'Old']]:
        record[attribute] = min_max_scaler(record[attribute], min_max_tuple=(
            min_max_info[attribute]['min'], min_max_info[attribute]['max']))

    for ordinal in _ORDINAL_LABELS:
        record[ordinal] = 1 if record[ordinal] == "No" else 0

    for onehot in _ONEHOT_LABELS:
        record[f"{onehot}_{record[onehot]}"] = 1
        del record[onehot]


def _map_size(size) -> float:
    """
    Maps the size of a dwelling to a value between 0 and 1.
    (The values and mapping are described in the initial dataset documentation.)

    :param size: (int)The dwelling size.
    :return: (float)The mapped ordinal value.
    """
    size = float(size)
    thresholds = [60, 81, 100, 140, 200]
    values = [0, 0.2, 0.4, 0.6, 0.8]

    for i, threshold in enumerate(thresholds):
        if size < threshold:
            return values[i]

    return 1


def _map_age_api(age) -> float:
    """
    Calculates the age of a dwelling and maps it to a value between 0 and 1.
    (The values and mapping are described in the initial dataset documentation.)

    :param age: (int)The dwelling age.
    :return: (float)The mapped ordinal value.
    """
    today = dt.date.today()
    age = today.year - age

    thresholds = [5, 15, 30]
    values = [0, 0.33, 0.66]

    for i, threshold in enumerate(thresholds):
        if age <= threshold:
            return values[i]
    return 1


def _map_income(income) -> str:
    """
    Maps the income information to a distinct value.
    (The values and mapping are described in the initial dataset documentation.)

    :param income: (float)The total income of the occupants.
    :return: (str)The mapped ordinal value.
    """
    thresholds = [10000, 20000, 40000, 60000]
    values = ["0€ - 10.000€", "10.001€ - 20.000€", "20.001€ - 40.000€", "40.001€ - 60.000€"]

    for counter, threshold in enumerate(thresholds):
        if income <= threshold:
            return values[counter]

    return "60.000€"


def _calculate_Ainc(*argv) -> float:
    """
    Calculates the Ainc value, which quantifies the ages of the people living in the house, based on the assumption
    that an individual consumes more energy as they grow.

    :param argv: (*argv)Non-keyword arguments for the number of Children, Teenagers, Adults, and Elders living in
    the house.
    :return: (float)The Ainc value.
    """
    return 0.5 * argv[0] + 0.75 * argv[1] + 0.9 * argv[2] + 1.0 * argv[3]


def _calculate_Adec(*argv) -> float:
    """
    Calculates the Adec value, which quantifies the ages of the people living in the house, based on the assumption
    that an individual consumes less energy as it grows.

    :param argv: (*argv)Non-keyword arguments for the number of Children, Teenagers, Adults, and Elders living in
    the house.
    :return: (float)The Adec value.
    """
    return 1.0 * argv[0] + 0.9 * argv[1] + 0.75 * argv[2] + 0.5 * argv[3]


def _calculate_Agauge(*argv) -> float:
    """
    Calculates the Agauge value, which quantifies the ages of the people living in the house, based on the assumption
    that adults and teenagers consume more energy than children and elders.

    :param argv: (*argv)Non-keyword arguments for the number of Children, Teenagers, Adults, and Elders living in
    the house.
    :return: (float) TheAgauge value.
    """
    return 0.5 * argv[0] + 0.75 * argv[1] + 1.0 * argv[2] + 0.5 * argv[3]


def _calculate_Education_Index(grads, post_grads) -> float:
    """
    Calculates the education index that aims at measuring the educational attainment of a group of people.

    :param grads: (int)The number of occupants that have graduated from a university.
    :param post_grads: (int)The number of occupants that received a post-graduate degree.
    :return: (float)The education index value.
    """
    MYS = (4 * grads) + (2 * post_grads)
    EYS = 17.91  # Expected years of schooling in Greece for 2019

    EI = ((EYS / 18) + (MYS / 18)) / 2
    return EI


def transform_data(form1, form2) -> dict:
    """
    Gathers all the data from the filled HTML forms, executes the necessary transformations, and constructs a new
    record.

    :param form1: (json file)The form that contains the household and occupants data.
    :param form2: (json file)The form that contains the energy data.
    :return: (dict)The new record.
    """
    record = {}
    house_data = {"Dwelling Grade": _MAP_DWELLING[form1["dtype"]], "Bedrooms": int(form1["bedrooms"]),
                  "Old": _MAP_AGE[form1["age"]],
                  "Heating Source": form1["heating"]}

    Occupants = int(form1["occupants"])
    Children = int(form1["children"])
    Teenagers = int(form1["teens"])
    Adults = int(form1["adults"])
    Elders = int(form1["elders"])

    occupants_data = {"Occupants": Occupants,
                      "Children": Children,
                      "Teenagers": Teenagers,
                      "Adults": Adults,
                      "Elders": Elders,
                      "Ainc": _calculate_Ainc(Children, Teenagers, Adults, Elders),
                      "Adec": _calculate_Adec(Children, Teenagers, Adults, Elders),
                      "Agauge": _calculate_Agauge(Children, Teenagers, Adults, Elders),
                      "Fulltimers": int(form1["full"]),
                      "Parttimers": int(form1["part"]),
                      "Grads": int(form1["graduated"]),
                      "PostGrads": int(form1["post"]),
                      "Education Index": _calculate_Education_Index(int(form1["graduated"]), int(form1["post"])),
                      "Income": form1["income"]}

    start = datetime.strptime(form2['start'], '%Y-%m-%d')
    end = datetime.strptime(form2['end'], '%Y-%m-%d')
    days = (end - start).days

    energy_data = {"Recycling": form2["recycling"], "Energy Class": form2["energy"],
                   "Thermostats": form2["thermo"], "Water Heater": form2["water"],
                   "Smart Plugs": form2["plugs"], "Awareness": form2["awareness"],
                   "Kwh/day/m2": float(form2["kwhs"]) / int(days) / float(form1["meters"])}

    record.update(house_data)
    record.update(occupants_data)
    record.update(energy_data)
    return record


def transform_data_API(api_reply, consumption) -> dict:
    """
    Gathers all the data from the lavoro API reply, executes the necessary transformations, and constructs a new
    record.

    :param api_reply: (json file)The API response that contains the all the data.
    :param consumption: (json file)The API response that contains the energy consumption.
    :return: (dict)The new record.
    """
    record = {}
    house_data = {"Dwelling Grade": _MAP_DWELLING[api_reply["Dwelling"]],
                  "Bedrooms": int(api_reply["Bedrooms"]),
                  "Old": _map_age_api(int(api_reply["built"])),
                  "Heating Source": "Yes" if api_reply[
                      "Heating Source"] else "No"}

    Occupants = int(api_reply["Occupants"])
    Children = int(api_reply["Children"])
    Teenagers = int(api_reply["Teenagers"])
    Adults = int(api_reply["Adults"])
    Elders = int(api_reply["Elders"])

    occupants_data = {"Occupants": Occupants, "Children": Children,
                      "Teenagers": Teenagers, "Adults": Adults,
                      "Elders": Elders,
                      "Ainc": _calculate_Ainc(Children, Teenagers, Adults, Elders),
                      "Adec": _calculate_Adec(Children, Teenagers, Adults, Elders),
                      "Agauge": _calculate_Agauge(Children, Teenagers, Adults, Elders),
                      "Fulltimers": int(api_reply["Fulltimers"]),
                      "Parttimers": int(api_reply["Parttimers"]),
                      "Grads": int(api_reply["Grads"]),
                      "PostGrads": int(api_reply["PostGrads"]),
                      "Education Index": _calculate_Education_Index(int(api_reply["Grads"]),
                                                                    int(api_reply["PostGrads"])),
                      "Income": _map_income(int(api_reply["Income"]))}

    energy_data = {"Recycling": api_reply["Recycling"], "Energy Class": api_reply["Energy Class"],
                   "Thermostats": api_reply["Thermostats"],
                   "Water Heater": "Yes" if api_reply["Water Heater"] else "No",
                   "Smart Plugs": api_reply["Smart Plugs"], "Awareness": api_reply["Awareness"],
                   "Kwh/day/m2": consumption}

    record.update(house_data)
    record.update(occupants_data)
    record.update(energy_data)

    return record
