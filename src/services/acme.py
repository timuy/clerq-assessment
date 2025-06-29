

from requests import Session
from fastapi import HTTPException

from datetime import datetime, date
import os
import time
import requests

class AcmeService:

    @staticmethod
    def get_settlement_data(session: Session, merchant: str, closing_date: date) -> float:
        # sum up all of the PURCHASE types and substract the REFUND types from given merchant and closing date
        merchant__uuid =  AcmeService._search_merchants(session, merchant)
        return  AcmeService._calculate_settlement_for_given_date(session, merchant__uuid, closing_date)

    @staticmethod
    def _search_merchants(session: Session, merchant: str) ->dict:
        # call merchant URL to search merchants in the system
        merchant_url = os.getenv("ACME_MERCHANT_URL")

        while True:
            response_json = AcmeService._call_API(session,merchant_url)
            next_url = response_json.get('next')
            results = response_json.get('results')

            for result in results:
                name = result.get("name")
                # remove all whitespace and change to lowercase before comparing
                if name and merchant.lower().strip() == name.lower().strip():
                    return result.get("id")

            merchant_url = next_url
            if not merchant_url:
                raise HTTPException(status_code=404, detail=f"{merchant} not found in system")

    @staticmethod
    def _calculate_settlement_for_given_date(session: Session, merchant_uuid: str, closing_date: date) ->dict:
        # calculate settlement  for merchant uuid and closing date passed in
        transaction_url = os.getenv("ACME_TRANSACTION_URL")

        # add merchant uuid and created_at_lte and create_at_gte to the URL before calling it
        transaction_url += f"?merchant={merchant_uuid}"

        date_format = "%Y-%m-%dT%H:%M:%SZ"

        end_of_date = datetime.combine(closing_date, datetime.max.time())
        transaction_url += f"&created_at__gte={closing_date.strftime(date_format)}&created_at__lte={end_of_date.strftime(date_format)}"

        settlement_amount = 0
        while True:
            response_json = AcmeService._call_API(session,transaction_url)
            next_url = response_json.get('next')
            results = response_json.get('results')

            for result in results:
                # need to filter for PURCHASE and REFUND type
                # add to amount for PURCHASE and subtract from amount for REFUND
                type = result.get("type")
                amount = float(result.get("amount"))
                if type == 'PURCHASE':
                    settlement_amount += amount
                elif type == "REFUND":
                    settlement_amount -= amount

            transaction_url = next_url
            # no more transactions break out of the loop
            if not transaction_url:
                return settlement_amount


    @staticmethod
    def _call_API(session: Session, url: str) -> dict:
        # call the acme endpoint and check the status code
        # returns the response in JSON format

        try:
            max_retries = int(os.getenv("MAX_RETRIES"))
        except ValueError:
            max_retries = 3
        
        try:
            sleep_between_retries = int(os.getenv("SLEEP_SECONDS_BETWEEN_RETRIES"))
        except ValueError:
            sleep_between_retries = 5

        for attempt in range(max_retries):
            try:
                response = session.get(url)
                if response.status_code == 200:
                    return response.json()
                else:
                    if attempt < max_retries -1:
                        time.sleep(sleep_between_retries)

            except requests.exceptions.RequestException:
                if attempt < max_retries - 1:
                    time.sleep(sleep_between_retries)

        # max retries reached so raise HTTPException     
        raise HTTPException(status_code=500, detail="Max retries reached.  Please try again later.")
