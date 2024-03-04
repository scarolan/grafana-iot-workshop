import board
import busio
import displayio
import terminalio
import time
import rtc
import os
import wifi
import socketpool
import ssl
import adafruit_imageload
import adafruit_sht31d
import adafruit_requests
import adafruit_ntp
from mpu6886 import MPU6886
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from digitalio import DigitalInOut, Direction, Pull

# Initialize button
btn = DigitalInOut(board.BTN)
btn.direction = Direction.INPUT
btn.pull = Pull.UP

# Variable to track temperature unit, False for Celsius, True for Fahrenheit
display_fahrenheit = False

# Function to convert temperature
def convert_temp(celsius, to_fahrenheit):
    if to_fahrenheit:
        return celsius * 9 / 5 + 32
    else:
        return celsius

# Initialize I2C
imu_i2c = busio.I2C(board.IMU_SCL, board.IMU_SDA)

# Wait for the I2C device to be ready
while not imu_i2c.try_lock():
    pass

# Scan for devices on the I2C bus
print("I2C addresses found:", [hex(device_address) for device_address in imu_i2c.scan()])
imu_i2c.unlock()

# Initialize the MPU6886
mpu = MPU6886(imu_i2c)

# Display setup
display = board.DISPLAY
display_group = displayio.Group()
display.root_group = display_group

# Load the Grafana logo
logo_bitmap, logo_palette = adafruit_imageload.load("/grafana_logo.bmp", 
                                                      bitmap=displayio.Bitmap, 
                                                      palette=displayio.Palette)

# Create a TileGrid to hold the bitmap
logo_tile_grid = displayio.TileGrid(logo_bitmap, pixel_shader=logo_palette)

# Position the image in the upper middle of the display
logo_tile_grid.x = 90
logo_tile_grid.y = 5  # Adjust this value based on your image size and desired position

# Add the image to the display group
display_group.append(logo_tile_grid)

# Add a thermometer image next to the temperature
thermometer_bitmap, thermometer_palette = adafruit_imageload.load("/thermometer.bmp", 
                                                      bitmap=displayio.Bitmap, 
                                                      palette=displayio.Palette)

# Create a TileGrid to hold the bitmap
thermometer_tile_grid = displayio.TileGrid(thermometer_bitmap, pixel_shader=thermometer_palette)

# Position the thermometer image
thermometer_tile_grid.x = 5
thermometer_tile_grid.y = 50  # Adjust this value based on your image size and desired position

# Add the image to the display group
display_group.append(thermometer_tile_grid)

# Add a water droplet image next to the humidity
humidity_bitmap, humidity_palette = adafruit_imageload.load("/droplet.bmp", 
                                                      bitmap=displayio.Bitmap, 
                                                      palette=displayio.Palette)

# Create a TileGrid to hold the bitmap
humidity_tile_grid = displayio.TileGrid(humidity_bitmap, pixel_shader=humidity_palette)

# Position the humidity image
humidity_tile_grid.x = 5
humidity_tile_grid.y = 90  # Adjust this value based on your image size and desired position

# Add the image to the display group
display_group.append(humidity_tile_grid)

# Import fonts
mono_font = bitmap_font.load_font("Roboto-Regular.bdf")

# Create some text labels
text_area = label.Label(terminalio.FONT, text="Connecting to WiFi...", color=0xFFFFFF, x=5, y=15)
temp_area = label.Label(mono_font, text="???", color=0xFFFFFF, x=40, y=63)
humi_area = label.Label(mono_font, text="???", color=0xFFFFFF, x=40, y=105)
display_group.append(text_area)
display_group.append(temp_area)
display_group.append(humi_area)

# WiFi connection information from environment variables
WIFI_SSID = os.getenv("CIRCUITPY_WIFI_SSID")
WIFI_PASSWORD = os.getenv("CIRCUITPY_WIFI_PASSWORD")

# Connect to WiFi
try:
    print(f"Connecting to {WIFI_SSID}")
    text_area.text = f"Connecting to {WIFI_SSID}"
    wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Connected!")
    text_area.text = "WiFi\nConnected!"
except Exception as e:
    text_area.text = "WiFi Connect\nFailed."
    print(f"WiFi Connect Failed: {e}")
    while True:
        pass  # Halt execution to troubleshoot

pool = socketpool.SocketPool(wifi.radio)
ntp = adafruit_ntp.NTP(pool, tz_offset=0)
# Set the rtc clock to NTP time
rtc.RTC().datetime = ntp.datetime
current_time = rtc.RTC().datetime
formatted_time = "{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}".format(
    year=current_time.tm_year,
    month=current_time.tm_mon,
    day=current_time.tm_mday,
    hour=current_time.tm_hour,
    minute=current_time.tm_min,
    second=current_time.tm_sec
)
print("Current time:", formatted_time)
ssl_context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, ssl_context)

# I2C setup for the SHT31D sensor
i2c = busio.I2C(board.PORTA_SCL, board.PORTA_SDA)
sht30 = adafruit_sht31d.SHT31D(i2c)

# Function to send data to Grafana cloud
def send_to_grafana(temperature, humidity):
    # Grafana Cloud Graphite endpoint details
    grafana_url = os.getenv("GRAFANA_GRAPHITE_URL")
    grafana_user = os.getenv("GRAFANA_USER")  # Assuming os.getenv is a placeholder for actual retrieval
    grafana_api_key = os.getenv("GRAFANA_API_KEY")  # Assuming os.getenv is a placeholder for actual retrieval

    # Correctly format the Authorization header
    auth_token = f"{grafana_user}:{grafana_api_key}"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

    # Retrieve DEVICE_NAME and DEVICE_LOCATION from environment variables
    DEVICE_NAME = os.getenv("DEVICE_NAME", "iotdevice")
    DEVICE_LOCATION = os.getenv("DEVICE_LOCATION", "home")

    # Prepare the data payload as a list of dictionaries
    data = [
        {"name": f"iot.{DEVICE_NAME}.temperature", "interval": 30, "value": float(temperature), "tags": [f"source={DEVICE_NAME}", f"location={DEVICE_LOCATION}"], "time": int(time.time())},
        {"name": f"iot.{DEVICE_NAME}.humidity", "interval": 30, "value": float(humidity), "tags": [f"source={DEVICE_NAME}", f"location={DEVICE_LOCATION}"], "time": int(time.time())},
        {"name": f"iot.{DEVICE_NAME}.accel_x", "interval": 30, "value": float(accel_data[0]), "tags": [f"source={DEVICE_NAME}", f"location={DEVICE_LOCATION}"], "time": int(time.time())},
        {"name": f"iot.{DEVICE_NAME}.accel_y", "interval": 30, "value": float(accel_data[1]), "tags": [f"source={DEVICE_NAME}", f"location={DEVICE_LOCATION}"], "time": int(time.time())},
        {"name": f"iot.{DEVICE_NAME}.accel_z", "interval": 30, "value": float(accel_data[2]), "tags": [f"source={DEVICE_NAME}", f"location={DEVICE_LOCATION}"], "time": int(time.time())},
        {"name": f"iot.{DEVICE_NAME}.gyro_x", "interval": 30, "value": float(gyro_data[0]), "tags": [f"source={DEVICE_NAME}", f"location={DEVICE_LOCATION}"], "time": int(time.time())},
        {"name": f"iot.{DEVICE_NAME}.gyro_y", "interval": 30, "value": float(gyro_data[1]), "tags": [f"source={DEVICE_NAME}", f"location={DEVICE_LOCATION}"], "time": int(time.time())},
        {"name": f"iot.{DEVICE_NAME}.gyro_z", "interval": 30, "value": float(gyro_data[2]), "tags": [f"source={DEVICE_NAME}", f"location={DEVICE_LOCATION}"], "time": int(time.time())},
    ]

    try:
        # Use the json parameter to automatically serialize the data
        print(data)
        response = requests.post(grafana_url, json=data, headers=headers)
        print("Response Status Code:", response.status_code)
        print("Data sent to Grafana Cloud:", response.text)
    except Exception as e:
        print("Failed to send data to Grafana Cloud:", e)

def update_sensors_and_display():
    global temperature, humidity, accel_data, gyro_data  # Declare globals for sensor data
    accel_data = mpu.acceleration()
    gyro_data = mpu.gyro()
    print("Acceleration Data:", accel_data)
    print("Gyro Data:", gyro_data)
    text_area.text = "Grafana Cloud\nIOT Workshop"
    temperature = sht30.temperature
    humidity = sht30.relative_humidity

    # Update temperature display based on current unit
    if display_fahrenheit:
        temp_display = f"{convert_temp(temperature, True):.1f}°F"
    else:
        temp_display = f"{temperature:.1f}°C"
    
    temp_area.text = temp_display
    humi_area.text = f"{humidity:.1f}%"
    
    # Send data to Grafana Cloud
    send_to_grafana(temperature, humidity)

# Initialize sensor data variables
temperature = 0
humidity = 0
accel_data = (0, 0, 0)
gyro_data = (0, 0, 0)

# Initialize the last update time to ensure the first update happens immediately
last_update_time = time.monotonic() - 5

# Perform an immediate update before the loop
update_sensors_and_display()

# Main loop
while True:
    current_time = time.monotonic()
    if current_time - last_update_time >= 5:  # Check if 10 seconds have passed
        update_sensors_and_display()
        last_update_time = current_time  # Reset the timer

    # Check if the button is pressed without blocking
    if not btn.value:
        print("Button pressed!")
        display_fahrenheit = not display_fahrenheit  # Toggle the temperature unit
        # Immediate update of temperature display after unit change
        update_sensors_and_display()
        time.sleep(0.2)  # Debounce delay to avoid multiple detections