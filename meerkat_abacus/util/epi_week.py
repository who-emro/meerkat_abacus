from datetime import datetime, timedelta

from meerkat_abacus.config import country_config


def epi_week_for_date(date):
    """
    calculate epi week

    Args:
        date
    Returns tuple epi_year, epi_week
    """
    _epi_year_start_date = epi_year_start_date(date)
    _epi_year = epi_year_by_date(date)
    # If the date is before the epi year start date, include it in week 1.
    if date < _epi_year_start_date:
        return _epi_year, 1
    _epi_week_number = (date - _epi_year_start_date).days // 7 + 1
    return _epi_year, _epi_week_number


def epi_year_start_date(date, epi_config=country_config["epi_week"]):
    """
    Get the first day of epi week 1 for year including given date.

    if epi_config==international epi_week 1 starts on the 1st of January

    if epi_config== day:<weekday> then the first epi_week start on the first weekday
    First weekday after 1st of January
    <weekday> is an integer where <weekday>=0 is Monday, 2 is Tuesday, etc.

    if epi_config is a dict one can specify custom start dates for epi years
    e.g.
    "epi_week": {
        2011: datetime.datetime(2011, 1, 2),
        2012: datetime.datetime(2011, 12, 31)
    }

    Args:
        date: date for which to return the start of epi year
        epi_config: how epi-weeks are calculated
    Returns:
        start_date: date of start of epi week 1 which includes provided date
    """
    if epi_config == "international":
        return datetime(date.year, 1, 1)
    elif "day" in epi_config:
        day_of_week = int(epi_config.split(":")[1])
        first_of_year = datetime(date.year, 1, 1)
        f_day_of_week = first_of_year.weekday()
        adjustment = day_of_week - f_day_of_week
        if adjustment < 0:
            adjustment = 7 + adjustment
        return first_of_year + timedelta(days=adjustment)
    elif isinstance(epi_config, dict):
        for start_datetime in reversed(sorted(epi_config.values())):
            if date > start_datetime:
                return start_datetime
    else:
        return datetime(date.year, 1, 1)


def epi_year_start_date_by_year(year, epi_config=country_config["epi_week"]):
    """
    Get the first day of epi week 1 for given year

    if epi_config==international epi_week 1 starts on the 1st of January

    if epi_config== day:<weekday> then the first epi_week start on the first weekday
    First weekday after 1st of January
    <weekday> is an integer where <weekday>=0 is Monday, 2 is Tuesday, etc.

    if epi_config is a dict one can specify custom start dates for epi years
    e.g.
    "epi_week": {
        2011: datetime.datetime(2011, 1, 2),
        2012: datetime.datetime(2011, 12, 31)
    }

    Args:
        year: year for which to return the start of epi year
        epi_config: how epi-weeks are calculated
    Returns:
        start_date: date of start of epi week 1 in provided year
    """
    if epi_config == "international":
        return datetime(year, 1, 1)
    elif "day" in epi_config:
        return __epi_year_start_date_for_weekday_config(year, epi_config)
    elif isinstance(epi_config, dict):
        return epi_config[year]
    else:
        return datetime(year, 1, 1)


def epi_year_by_date(date, epi_config=country_config["epi_week"]):
    """
    Calculates the epi year for provided date
    :param date: date to caluclate the epi year for
    :param epi_config: epi year computation logic, "international", "day:X" or custom dict
        if epi_config==international epi_week 1 starts on the 1st of January

        if epi_config== day:<weekday> then the first epi_week start on the first weekday
        First weekday after 1st of January
        <weekday> is an integer where <weekday>=0 is Monday, 2 is Tuesday, etc.

        if epi_config is a dict one can specify custom start dates for epi years
        e.g.
        "epi_week": {
            2011: datetime.datetime(2011, 1, 2),
            2012: datetime.datetime(2011, 12, 31)
        }
    :return: epi year
    """
    if isinstance(epi_config, dict):
        for epi_year, epi_year_start_datetime in reversed(sorted(epi_config.items())):
            if date > epi_year_start_datetime:
                return epi_year
        raise ValueError("Could not compute epi year for date {!r}".format(date))
    elif isinstance(epi_config, str) and "day:" in epi_config:
        year = date.year
        _epi_year_start_date = __epi_year_start_date_for_weekday_config(year, epi_config)
        if date < _epi_year_start_date:
            return year - 1
        else:
            return year
    else:
        return date.year


def epi_week_start_date(year, epi_week):
    """
    Calculates the start of an epi week in given year:

    Args:
        epi-week: epi week
        year: year
    Returns:
        start-date: datetime
    """
    _epi_year_start_date = epi_year_start_date_by_year(int(year))
    start_date = _epi_year_start_date + timedelta(weeks=int(epi_week) - 1)
    return start_date


def __epi_year_start_date_for_weekday_config(year, epi_config):
    config_weekday = int(epi_config.split(":")[1])
    first_of_year = datetime(year, 1, 1)
    first_day_of_year_weekday = first_of_year.weekday()
    adjustment = config_weekday - first_day_of_year_weekday
    if adjustment < 0:
        adjustment = 7 + adjustment
    return first_of_year + timedelta(days=adjustment)
