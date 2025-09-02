def nmea_to_decimal(degree_min, direction):
    if not degree_min or not direction:
        return None
    try:
        deg_len = 2 if direction in ['N', 'S'] else 3
        degrees = float(degree_min[:deg_len])
        minutes = float(degree_min[deg_len:])
        dec = degrees + minutes / 60
        if direction in ['S', 'W']:
            dec = -dec
        return dec
    except ValueError:
        return None
