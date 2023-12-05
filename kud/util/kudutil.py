

def get_separators(year, month): 
    """
    Returns the right decimal and thousands separators based on the specified year and month. 
    That is needed because DanskeBank has changed the dec and thousands separators around September 2020 in the Kontoudskrift files.
    """
    dec_separator = '.'
    thousands_separator = ','

    if int(year) > 2020: 
        dec_separator = ','
        thousands_separator = '.'
    elif int(year) == 2020 and int(month) >= 9: 
        dec_separator = ','
        thousands_separator = '.'

    return dec_separator, thousands_separator