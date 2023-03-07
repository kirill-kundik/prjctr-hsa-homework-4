import logging
import time

from aiohttp import web, ClientSession

DEBUG = False
NBU_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
LIQPAY_CASH_URL = "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5"
LIQPAY_NON_CASH_URL = "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11"
GOOGLE_GA_DEBUG_URL = "https://www.google-analytics.com/debug/mp/collect"
GOOGLE_GA_URL = GOOGLE_GA_DEBUG_URL if DEBUG else "https://www.google-analytics.com/mp/collect"
GOOGLE_GA_API_SECRET = "<YOUR_GA_API_SECRET>"
GOOGLE_GA_MEASUREMENT_ID = "<YOUR_GA_MEASUREMENT_ID>"


async def fetch_nbu(sess: ClientSession):  # Using NBU Public API
    logging.debug(f"Fetching HTTP GET {NBU_URL}")
    async with sess.get(NBU_URL) as resp:
        logging.debug(f"Responded {resp.status} {resp.reason}")
        res = await resp.json()
    logging.debug(f"Received data: {res}")

    usd_rate = list(filter(lambda x: x["cc"] == "USD", res))[0]
    return usd_rate["rate"], usd_rate["exchangedate"]


async def fetch_liqpay(sess: ClientSession):  # Using Privat24 Public API
    logging.debug(f"Fetching (cash) HTTP GET {LIQPAY_CASH_URL}")
    async with sess.get(LIQPAY_CASH_URL) as resp_cash:
        logging.debug(f"Responded (cash) {resp_cash.status} {resp_cash.reason}")
        res_cash = await resp_cash.json()
    logging.debug(f"Received (cash) data: {res_cash}")

    logging.debug(f"Fetching (non-cash) HTTP GET {LIQPAY_NON_CASH_URL}")
    async with sess.get(LIQPAY_NON_CASH_URL) as resp_non_cash:
        logging.debug(f"Responded (non-cash) {resp_non_cash.status} {resp_non_cash.reason}")
        res_non_cash = await resp_non_cash.json()
    logging.debug(f"Received (non-cash) data: {res_non_cash}")

    usd_cash_rate = list(filter(lambda x: x["ccy"] == "USD", res_cash))[0]
    usd_non_cash_rate = list(filter(lambda x: x["ccy"] == "USD", res_non_cash))[0]
    result = tuple(map(
        float, (usd_cash_rate["buy"], usd_cash_rate["sale"], usd_non_cash_rate["buy"], usd_non_cash_rate["sale"])
    ))
    return result


async def push_to_ga(event_name, data, client_id, sess: ClientSession):
    url = GOOGLE_GA_URL + f"?api_secret={GOOGLE_GA_API_SECRET}&measurement_id={GOOGLE_GA_MEASUREMENT_ID}"
    payload = {
        "client_id": client_id,
        "non_personalized_ads": True,
        "timestamp_micros": str(time.monotonic_ns() // 1000),
        "events": [{
            "name": event_name,
            "params": data,
        }],
    }

    logging.debug(f"Pushing over HTTP POST {GOOGLE_GA_URL} \"{payload}\"")
    async with sess.post(url, json=payload) as resp:
        resp_text = await resp.text()
        logging.debug(f"Pushing respond {resp.status} {resp.reason}")
        logging.debug(f"Pushing respond text: {resp_text}")

    return True


async def index(_request):
    with open("index.html") as f:
        return web.Response(text=f.read(), status=200, content_type="text/html")


async def form(request):
    body = await request.post()
    client_id = body["client_id"]

    async with ClientSession() as sess:
        logging.info("UAH currency rates fetching started.")
        nbu_rate, date = await fetch_nbu(sess)
        p24_cash_buy, p24_cash_sale, p24_non_cash_buy, p24_non_cash_sale = await fetch_liqpay(sess)
        logging.info("UAH currency rates fetching finished.")
        data = {
            "exchange_date": date,
            "nbu_rate": nbu_rate,
            "p24_cash_buy": p24_cash_buy,
            "p24_cash_sale": p24_cash_sale,
            "p24_non_cash_buy": p24_non_cash_buy,
            "p24_non_cash_sale": p24_non_cash_sale,
        }
        logging.info(f"Pushing to GA (client_id='{client_id}'): {data}")
        await push_to_ga("uah_rates", data, client_id, sess)
        logging.info("Successfully pushed to GA.")

    values = [f'{key}={value}' for key, value in data.items()]
    return web.HTTPFound(f"/?{'&'.join(values)}")


def main():
    app = web.Application()

    app.add_routes([web.get('/', index), web.post('/', form)])

    web.run_app(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)

    main()
