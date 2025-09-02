import serial
import pynmea2
from utils import nmea_to_decimal

def read_gps_messages(port='/dev/serial0', baud=9600):
    try:
        ser = serial.Serial(port, baud, timeout=1)
    except Exception as e:
        print('Failed to open serial port:', str(e))
        return None, None
    gga_msg = None
    rmc_msg = None
    with ser:
        while gga_msg is None or rmc_msg is None:
            line = ser.readline().decode(errors='ignore').strip()
            if not line.startswith('$'):
                continue
            try:
                msg = pynmea2.parse(line)
            except pynmea2.ParseError:
                continue
            if isinstance(msg, pynmea2.GGA) and gga_msg is None and int(msg.gps_qual) > 0:
                gga_msg = msg
            elif isinstance(msg, pynmea2.RMC) and rmc_msg is None and msg.status == 'A':
                rmc_msg = msg
    return gga_msg, rmc_msg

def extract_coordinates(gga_msg, rmc_msg):
    if gga_msg is None or rmc_msg is None:
        return None, None
    coords = []
    for msg in (gga_msg, rmc_msg):
        lat = nmea_to_decimal(msg.lat, msg.lat_dir)
        lon = nmea_to_decimal(msg.lon, msg.lon_dir)
        if lat is not None and lon is not None:
            coords.append((lat, lon))
    if not coords:
        return None, None
    avg_lat = sum(lat for lat, _ in coords) / len(coords)
    avg_lon = sum(lon for _, lon in coords) / len(coords)
    return avg_lat, avg_lon

def extract_gps_info(gga_msg, rmc_msg):
    gga_data = {
        'fix_quality': gga_msg.gps_qual,
        'satellites': gga_msg.num_sats,
        'hdop': gga_msg.horizontal_dil,
        'altitude': gga_msg.altitude,
        'altitude_units': gga_msg.altitude_units
    } if gga_msg else None
    rmc_data = {
        'status': rmc_msg.status,
        'speed': rmc_msg.spd_over_grnd,
        'course': rmc_msg.true_course,
        'timestamp': rmc_msg.timestamp
    } if rmc_msg else None
    return gga_data, rmc_data

def print_coordinates(avg_lat, avg_lon):
    if avg_lat is not None and avg_lon is not None:
        print(f'Coordinates: {avg_lat:.6f}, {avg_lon:.6f}')
    else:
        print('No valid GPS coordinates received')

def print_gps_info(gga_data, rmc_data):
    if gga_data:
        print(f"GGA - Fix quality: {gga_data['fix_quality']}")
        print(f"GGA - Satellites: {gga_data['satellites']}")
        print(f"GGA - HDOP: {gga_data['hdop']}")
        print(f"GGA - Altitude: {gga_data['altitude']} {gga_data['altitude_units']}")
    if rmc_data:
        print(f"RMC - Status: {rmc_data['status']}")
        print(f"RMC - Speed: {rmc_data['speed']} knots")
        print(f"RMC - Course: {rmc_data['course']}")
        print(f"RMC - UTC time: {rmc_data['timestamp']}")

if __name__ == '__main__':
    gga_msg, rmc_msg = read_gps_messages()
    avg_lat, avg_lon = extract_coordinates(gga_msg, rmc_msg)
    gga_data, rmc_data = extract_gps_info(gga_msg, rmc_msg)
    print_coordinates(avg_lat, avg_lon)
    print_gps_info(gga_data, rmc_data)

