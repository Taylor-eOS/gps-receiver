import serial
import pynmea2

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

def get_coordinates(port='/dev/serial0', baud=9600):
    try:
        ser = serial.Serial(port, baud, timeout=1)
    except Exception as e:
        print('Failed to open serial port:', str(e))
        return None, None
    gga_coords = None
    rmc_coords = None
    with ser:
        while gga_coords is None or rmc_coords is None:
            line = ser.readline().decode(errors='ignore').strip()
            if not line.startswith('$'):
                continue
            try:
                msg = pynmea2.parse(line)
            except pynmea2.ParseError:
                continue
            if isinstance(msg, pynmea2.GGA) and gga_coords is None and int(msg.gps_qual) > 0:
                lat = nmea_to_decimal(msg.lat, msg.lat_dir)
                lon = nmea_to_decimal(msg.lon, msg.lon_dir)
                if lat is not None and lon is not None:
                    gga_coords = (lat, lon)
            elif isinstance(msg, pynmea2.RMC) and rmc_coords is None and msg.status == 'A':
                lat = nmea_to_decimal(msg.lat, msg.lat_dir)
                lon = nmea_to_decimal(msg.lon, msg.lon_dir)
                if lat is not None and lon is not None:
                    rmc_coords = (lat, lon)
    if gga_coords is None or rmc_coords is None:
        return None, None
    avg_lat = (gga_coords[0] + rmc_coords[0]) / 2
    avg_lon = (gga_coords[1] + rmc_coords[1]) / 2
    return avg_lat, avg_lon

def print_coordinates():
    avg_lat, avg_lon = get_coordinates()
    if avg_lat is not None and avg_lon is not None:
        print(f'Coordinates: {avg_lat:.3f}, {avg_lon:.3f}')
    else:
        print('No valid GPS coordinates received')

if __name__ == '__main__':
    print('Running at 9600 baud')
    print_coordinates()

