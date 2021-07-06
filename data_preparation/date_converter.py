from datetime import date

def get_count_of_day(year,month,day):
    
    """
    Function that returns the count of day (since the beginning of the year) 
    for a given year, month and day
    
    Positional argument:
        year -- type = integer
        month -- type = integer 
        day -- type = integer
    
    Example:
        get_count_of_day(2015,7,18)
        returns: 199
    """
    
    d0 = date(year, 1, 1)
    d1 = date(year, month, day)
    delta = d1 - d0

    count_of_day = delta.days + 1

    return count_of_day
