from bs4 import BeautifulSoup
import requests
import re
from webscraper.models.bestbuy import BestBuy
from webscraper.models.amazon import Amazon
import asyncio
import time


def sendNotification(price):
    data = {"message": f"The price is ${price}"}
    headers = {
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIwM2UwZTkzNzc3YTc0YmVkYjU1NTFjMjUzNTdmODBmNiIsImlhdCI6MTU5OTQxNDQ0OSwiZXhwIjoxOTE0Nzc0NDQ5fQ.4eRpXkia4TsdT39LWc4ryYYN0UTkazXkFw4d_DhuM2c",
        "Content-Type": "application/json",
    }

    r = requests.post(
        "http://docker.anthonyma.ca:8123/api/services/notify/mobile",
        headers=headers,
        json=data,
    )

    assert r.ok


async def main():

    t = time.perf_counter()
    # amazon: Amazon = await Amazon.create("https://www.amazon.ca/Lodge-EC7OD43-Enameled-Dutch-quart/dp/B01839OPSM?pf_rd_r=9KHQKG2K201P3PQCW602&pf_rd_p=91592ffe-8a5e-4891-bf14-8b1db9aedc64&pd_rd_r=0d0274c4-b67d-41d5-8b66-36df900bb3fe&pd_rd_w=qGvfx&pd_rd_wg=YXzxB&ref_=pd_gw_cr_wsim")

    # bestbuy: BestBuy = await BestBuy.create("https://www.bestbuy.ca/en-ca/product/hp-15-6-laptop-silver-intel-core-i3-1005g1-256gb-ssd-8gb-ram-windows-10/13863131")

    # bestbuy2: BestBuy = await BestBuy.create("https://www.bestbuy.ca/en-ca/product/samsung-58-4k-uhd-hdr-qled-tizen-smart-tv-qn58q60tafxzc-titan-grey-only-at-best-buy/14471420")

    # print(bestbuy)

    # amazonTask = asyncio.create_task(Amazon.create(
    #     "https://www.amazon.ca/Lodge-EC7OD43-Enameled-Dutch-quart/dp/B01839OPSM?pf_rd_r=9KHQKG2K201P3PQCW602&pf_rd_p=91592ffe-8a5e-4891-bf14-8b1db9aedc64&pd_rd_r=0d0274c4-b67d-41d5-8b66-36df900bb3fe&pd_rd_w=qGvfx&pd_rd_wg=YXzxB&ref_=pd_gw_cr_wsim"))

    bestbuyTask = asyncio.create_task(
        BestBuy.create(
            "https://www.bestbuy.ca/en-ca/product/hp-15-6-laptop-silver-intel-core-i3-1005g1-256gb-ssd-8gb-ram-windows-10/13863131"
        )
    )
    bbTask = asyncio.create_task(
        BestBuy.create(
            "https://www.bestbuy.ca/en-ca/product/samsung-58-4k-uhd-hdr-qled-tizen-smart-tv-qn58q60tafxzc-titan-grey-only-at-best-buy/14471420"
        )
    )

    # amazon = await amazonTask
    bestbuy = await bestbuyTask
    bestbuy2 = await bbTask

    # print(amazon)
    print(bestbuy)
    print(bestbuy2)

    print(f"Finished. Total time elapsed: {time.perf_counter() - t}")

    # if option == "1":
    #     bestbuy = BestBuy(
    #         "https://www.bestbuy.ca/en-ca/product/hp-15-6-laptop-silver-intel-core-i3-1005g1-256gb-ssd-8gb-ram-windows-10/13863131")
    #     print(bestbuy.getTitle())
    #     print(f"Current price: {bestbuy.getCurrentPrice()}")
    #     print(f"Regular price: {bestbuy.getRegularPrice()}")
    #     # print(f"Product is on sale: {bestbuy.isOnSale()}")
    # else:
    #     amazon = await Amazon.create("https://www.amazon.ca/Lodge-EC7OD43-Enameled-Dutch-quart/dp/B01839OPSM?pf_rd_r=9KHQKG2K201P3PQCW602&pf_rd_p=91592ffe-8a5e-4891-bf14-8b1db9aedc64&pd_rd_r=0d0274c4-b67d-41d5-8b66-36df900bb3fe&pd_rd_w=qGvfx&pd_rd_wg=YXzxB&ref_=pd_gw_cr_wsim")
    #     print(amazon.getTitle())
    #     print(f"Current price: {amazon.getCurrentPrice()}")
    #     print(f"Regular price: {amazon.getRegularPrice()}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    loop.run_until_complete(main())
