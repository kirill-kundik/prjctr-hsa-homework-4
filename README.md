# UAH/USD rates project

*This project completes homework #4: Monitoring systems for user metrics.*

A simple `Python` script fetches NBU (National Bank of Ukraine) 
official UAH/USD rates from [public API](https://bank.gov.ua/ua/open-data/api-dev).
Also, it uses Privat24 [public API](https://api.privatbank.ua/#p24/exchange) to obtain real 
rates from Cash and No-Cash markets. 
After gathering the info it pushes the event with rates
to pre-configured [Google Analytics v4 property](https://developers.google.com/analytics/devguides/collection/ga4).

## Prerequisites

* Installed [Python 3.7](https://www.python.org/downloads/) or newer
* Available [virtual environment](https://docs.python.org/3/library/venv.html) for Python
* Configured Google Analytics v4 [property](https://developers.google.com/analytics/devguides/collection/ga4) and [Web Stream](https://support.google.com/analytics/answer/9304153#stream&zippy=%2Cweb).
* Fill the following variables `<YOUR_GA_API_SECRET>`, 
`<YOUR_GA_MEASUREMENT_ID>`, `<YOUR_GA_CLIENT_ID>` 
with actual values in the `main.py` and `index.html` files.
* To obtain `<GA_CLIENT_ID>` please open `index.html` in your preferred browser. 
Then your Google client id will appear on the screen. Fill `main.py`.

## Install

Following command will install `main.py` script:

```bash
$ bash install.sh
```

*By default,* it creates a separate python virtual environment in 
`/usr/local/etc/ga-uah-events-sender` dir on your local machine. 
Installs all the required packages and places the script 
in `crontab` to run every hour. So you don't need to run it manually.

## Executing script manually

As was mentioned in [Install](#install) section, 
you don't need to run the script manually after successful installation.
But if you want to, you can do this with following steps:

### Step 1

Change working directory to the location where script was installed. 
*By default,* it is `/usr/local/etc/ga-uah-events-sender` 

```bash
$ cd /usr/local/etc/ga-uah-events-sender
```

### Step 2

Activate python virtual environment.

```bash
$ source venv/bin/activate
```

### Step 3

Run the script.

```bash
$ python main.py
```

### Debugging

To run the script in `debug` mode you just need to replace the line 6:

```python
DEBUG = True
```

---

Feel free to make any changes in `install.sh` or `main.py` scripts.