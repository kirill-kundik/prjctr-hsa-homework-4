import logging
import time

import requests

NBU_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
LIQPAY_CASH_URL = "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5"
LIQPAY_NON_CASH_URL = "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11"
GOOGLE_GA_URL = "https://www.google-analytics.com/mp/collect"
GOOGLE_GA_API_SECRET = "<YOUR_GA_API_SECRET>"
GOOGLE_GA_MEASUREMENT_ID = "<YOUR_GA_MEASUREMENT_ID>"
GOOGLE_GA_CLIENT_ID = "<YOUR_GA_CLIENT_ID>"


def fetch_nbu():  # Using NBU Public API
    logging.debug(f"Fetching HTTP GET {NBU_URL}")
    res = requests.get(NBU_URL)
    logging.debug(f"Responded {res.status_code} {res.reason}")
    res = res.json()
    logging.debug(f"Received data: {res}")
    usd_rate = list(filter(lambda x: x["cc"] == "USD", res))[0]
    return usd_rate["rate"], usd_rate["exchangedate"]


def fetch_liqpay():  # Using Privat24 Public API
    logging.debug(f"Fetching (cash) HTTP GET {LIQPAY_CASH_URL}")
    res_cash = requests.get(LIQPAY_CASH_URL)
    logging.debug(f"Responded (cash) {res_cash.status_code} {res_cash.reason}")
    logging.debug(f"Fetching (non-cash) HTTP GET {LIQPAY_NON_CASH_URL}")
    res_non_cash = requests.get(LIQPAY_NON_CASH_URL)
    logging.debug(f"Responded (non-cash) {res_non_cash.status_code} {res_non_cash.reason}")
    res_cash = res_cash.json()
    logging.debug(f"Received (cash) data: {res_cash}")
    res_non_cash = res_non_cash.json()
    logging.debug(f"Received (non-cash) data: {res_non_cash}")
    usd_cash_rate = list(filter(lambda x: x["ccy"] == "USD", res_cash))[0]
    usd_non_cash_rate = list(filter(lambda x: x["ccy"] == "USD", res_non_cash))[0]
    result = tuple(map(
        float, (usd_cash_rate["buy"], usd_cash_rate["sale"], usd_non_cash_rate["buy"], usd_non_cash_rate["sale"])
    ))
    return result


def push_to_ga(event_name, data):
    url = GOOGLE_GA_URL + f"?api_secret={GOOGLE_GA_API_SECRET}&measurement_id={GOOGLE_GA_MEASUREMENT_ID}"
    payload = {
        "client_id": GOOGLE_GA_CLIENT_ID,
        "non_personalized_ads": True,
        "timestamp_micros": str(time.monotonic_ns() // 1000),
        "events": [{
            "name": event_name,
            "params": data,
        }],
    }
    logging.debug(f"Pushing over HTTP POST {GOOGLE_GA_URL} \"{payload}\"")
    res = requests.post(url, json=payload)
    logging.debug(f"Pushing respond {res.status_code} {res.reason}")
    logging.debug(f"Pushing respond text: {res.text}")


def main():
    logging.info("UAH currency rates fetching started.")
    nbu_rate, date = fetch_nbu()
    p24_cash_buy, p24_cash_sale, p24_non_cash_buy, p24_non_cash_sale = fetch_liqpay()
    logging.info("UAH currency rates fetching finished.")
    data = {
        "exchange_date": date,
        "nbu_rate": nbu_rate,
        "p24_cash_buy": p24_cash_buy,
        "p24_cash_sale": p24_cash_sale,
        "p24_non_cash_buy": p24_non_cash_buy,
        "p24_non_cash_sale": p24_non_cash_sale,
    }
    logging.info(f"Pushing to GA: {data}")
    push_to_ga("uah_rates", data)
    logging.info("Successfully pushed to GA.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
