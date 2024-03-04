# grafana-iot-workshop
An IoT workshop using Grafana Cloud and the m5stack Atom S3 microcontroller

![iot_dashboard](https://github.com/scarolan/grafana-iot-workshop/assets/403332/53ab9ede-87b2-4151-bd61-6d634d7e6bff)

# Prerequisites
You'll need an M5Stack Atom S3 microcontroller, an M5Stack Env III temp/humi sensor, and a free Grafana cloud account.

# Instructions
In your Grafana Cloud account navigate down to the Graphite section and click on "Send Metrics".  
![image](https://github.com/scarolan/grafana-iot-workshop/assets/403332/9e7dbb18-c546-4e72-81af-a425c3f3bae5)

Generate a new API key with default settings:  
![image](https://github.com/scarolan/grafana-iot-workshop/assets/403332/ee95683c-2c97-44de-bac4-f2fae0d77bd0)
  
![image](https://github.com/scarolan/grafana-iot-workshop/assets/403332/22389497-0561-43d5-ab5b-acd1f632c941)

Save the API key in a file, you'll need it in a moment. Also make note of your Graphite URL and username:  
![image](https://github.com/scarolan/grafana-iot-workshop/assets/403332/3b5cd90f-d542-4210-bfb1-260e153e07fd)

Clone this repo or download the zip file using the 'Code' button.

Edit the 'settings.toml' file and add your settings for WiFi and Grafana.  

Your file should look similar to this when you are done:

```
CIRCUITPY_WIFI_SSID = "WIFINET"
CIRCUITPY_WIFI_PASSWORD = "supersecretpassword"
GRAFANA_GRAPHITE_URL = "https://graphite-prod-13-prod-us-east-0.grafana.net/graphite/metrics"
GRAFANA_API_KEY = "glc_eyJvIjoiMTA1NDkyMyIsIm4iOiJzdGFjay04NjA1asdjfkljsdfkljklasjdfkljaskldfjkljkdfjklW4wNkw1NhhweruioyqweoriuiousdojoicHJvZC11cy1lYXN0LTAifX0="
GRAFANA_USER = "1432854"
CIRCUITPY_WEB_API_PASSWORD = "grafana"
CIRCUITPY_WEB_API_PORT = 80
DEVICE_NAME = "atoms3"
DEVICE_LOCATION = "office"
```

Save the 'settings.toml' file.  

If you haven't already done so you'll need to install CircuitPython on the Atom S3.  Instructions for that are here:
https://circuitpython.org/board/m5stack_atoms3/

Once you have the device flashed with CircuitPython firmware, plug it into your laptop with a USB cable.  It should show up as a new disk drive called CIRCUITPY.

Drag and drop *all* of the files from the git repo onto the CIRCUITPY drive.  Remember you are copying the *contents* of the git repo / zip file, not the folder itself.  If you did it right the drive will look like this:
![image](https://github.com/scarolan/grafana-iot-workshop/assets/403332/e2d38284-87f4-4157-a789-910a73ebc00b)

Create a new dashboard by importing the JSON at this link:
https://gist.github.com/scarolan/d95e24486fc5c6757930f1ce942470ec

You're done!  Play with the device to see how you can affect the temperature, humidity, and accelerometer settings.
