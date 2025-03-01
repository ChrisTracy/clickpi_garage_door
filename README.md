# ClickPi Garage Door HACS Integraton

## ClickPi Setup
See the [ClickPi Repo](https://github.com/ChrisTracy/clickpi) to get started.

You will need a contact sensor of some sort to use this integration properly (show the garage door as closed/open in Home Assistant). I am using the [Yolink Door Sensor](https://shop.yosmart.com/collections/door-sensors/products/ys7704) and hub.

## Installation

1. Install [HACS](https://www.hacs.xyz/docs/use/) if you haven't already
2. Add custom repository `https://github.com/christracy/clickpi_garage_door` as "Integration" by clicking the three dots at the top right of HACS
3. Find and install "ClickPi Garage Door" integration in HACS's store
4. Restart your Home Assistant
5. Navigate to Settings > Devices & services > Add Integration > ClickPi Garage Door
6. Enter the parameters for your ClickPi instance and click submit

| Parmeter     | Example Value                      | Description                                            |
| ------------ | ---------------------------------- | ------------------------------------------------------ |
| `host`       | `http://192.168.1.5:5151`          | The endpoint of your ClickPi device                    |   
| `api_key`    | `abcdefghijklmnop123456789`        | The api key obtained from the ClickPi admin console    |
| `pin_number` | `21`                               | The Rasp Pi GPIO pin # connected to your Garage Opener |
| `sensor`     | `binary_sensor.garage_door_sensor` | The contact sensor on your garage door                 |
| `name`       | `Garage Door`                      | The name that will be shown in Home Assistant          |