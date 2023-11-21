import requests


def get_element(ID) -> tuple[any, any]:
    """
    This function calls the lavoro API and based on the returned status code, returns either None or two JSON files
    containing the energy information and energy consumption of the dwelling with the specific ID.

    :param ID: (ID) The dwelling ID.
    :return: (tuple) A tuple of Nones or a tuple of JSON files.
    """
    record = requests.get(f"http://lavoro.csd.auth.gr:8000/dev_id/{ID}/meta/")
    if record.status_code in [400, 404, 405]:
        return None, None

    consumption = requests.get(
        f"http://lavoro.csd.auth.gr:8000/dev_id/{ID}/json/30days/average_consumption_div_home_size?from_cache=false")

    return record.json(), consumption.json()
