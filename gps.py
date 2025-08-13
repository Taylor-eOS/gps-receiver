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

def read_gps(port='/dev/serial0', baud=9600):
    try:
        ser = serial.Serial(port, baud, timeout=1)
    except Exception as e:
        err = str(e)
        print('Failed to open serial port:', err)
        return
    with ser:
        while True:
            line = ser.readline().decode(errors='ignore').strip()
            if not line.startswith('$'):
                continue
            try:
                msg = pynmea2.parse(line)
            except pynmea2.ParseError:
                continue
            if isinstance(msg, pynmea2.GGA):
                lat = nmea_to_decimal(msg.lat, msg.lat_dir)
                lon = nmea_to_decimal(msg.lon, msg.lon_dir)
                if lat is not None and lon is not None and int(msg.gps_qual) > 0:
                    print(f'GGA Fix: Lat {lat:.6f}, Lon {lon:.6f}')
            elif isinstance(msg, pynmea2.RMC):
                if msg.status == 'A':
                    lat = nmea_to_decimal(msg.lat, msg.lat_dir)
                    lon = nmea_to_decimal(msg.lon, msg.lon_dir)
                    if lat is not None and lon is not None:
                        print(f'RMC Fix: Lat {lat:.6f}, Lon {lon:.6f}')

if __name__ == '__main__':
    read_gps()

