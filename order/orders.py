import configparser
import random

from utilites.utilities import on_response_error

config = configparser.ConfigParser()
config.read('config.ini')


class Orders:

    def __init__(self, session, account, base_url):
        self.session = session
        self.account = account
        self.base_url = base_url
        pass

    @staticmethod
    def create_close_order(quantity, product):
        order = {
            "client_order_id": random.randint(999999999, 9999999999),
            "symbol": product["symbol"],
            "quantity": quantity,
            "call_put": product["callPut"],
            "expiry_day": product["expiryDay"],
            "expiry_year": product["expiryYear"],
            "expiry_month": product["expiryMonth"],
            "strike_price": product["strikePrice"]
        }

        return order

    @staticmethod
    def create_order_request_params(consumer_key, order, request="PreviewOrderRequest", preview_id=0):
        headers = {"Content-Type": "application/xml", "consumerKey": consumer_key}
        payload = """<{8}>
                       <orderType>OPTN</orderType>
                       <clientOrderId>{0}</clientOrderId>
                       <PreviewIds>
                           <previewId>{9}</previewId>
                       </PreviewIds>
                       <Order>
                           <allOrNone>false</allOrNone>
                           <priceType>MARKET</priceType>
                           <orderTerm>GOOD_FOR_DAY</orderTerm>
                           <marketSession>REGULAR</marketSession>
                           <stopPrice/>
                           <Instrument>
                               <Product>
                                   <callPut>{1}</callPut>
                                   <securityType>OPTN</securityType>
                                   <symbol>{2}</symbol>
                                   <expiryYear>{3}</expiryYear>
                                   <expiryMonth>{4}</expiryMonth>
                                   <expiryDay>{5}</expiryDay>
                                   <strikePrice>{6}</strikePrice>
                               </Product>
                               <orderAction>SELL_CLOSE</orderAction>
                               <quantityType>QUANTITY</quantityType>
                               <quantity>{7}</quantity>
                           </Instrument>
                       </Order>
                   </{8}>"""

        payload = payload.format(order["client_order_id"], order["call_put"], order["symbol"],
                                 order["expiry_year"], order["expiry_month"], order["expiry_day"],
                                 order["strike_price"], order["quantity"], request, preview_id)

        return headers, payload

    def preview_order(self, headers, payload):
        print("\nPreview Order: ")

        url = self.base_url + "/v1/accounts/" + self.account["accountIdKey"] + "/orders/preview.json"

        response = self.session.post(url, header_auth=True, headers=headers, data=payload)

        if response is not None and response.status_code == 200:
            data = response.json()
            print("\nPreview Order:")

            try:
                preview_id = False

                for preview_ids in data["PreviewOrderResponse"]["PreviewIds"]:
                    preview_id = preview_ids["previewId"]
                    print("Preview ID: " + str(preview_id))

                for orders in data["PreviewOrderResponse"]["Order"]:
                    if orders is not None:
                        if "Instrument" in orders:
                            for instrument in orders["Instrument"]:
                                if instrument is not None:
                                    if "orderAction" in instrument:
                                        print("Action: " + instrument["orderAction"])

                                    if "quantity" in instrument:
                                        print("Quantity: " + str(instrument["quantity"]))

                                    if "Product" in instrument and "symbol" in instrument["Product"]:
                                        print("Symbol: " + instrument["Product"]["symbol"])

                                    if "symbolDescription" in instrument:
                                        print("Description: " + str(instrument["symbolDescription"]))

                        if "priceType" in orders and "limitPrice" in orders:
                            print("Price Type: " + orders["priceType"])
                            if orders["priceType"] == "MARKET":
                                print("Price: MKT")
                            else:
                                print("Price: " + str(orders["limitPrice"]))

                        if "orderTerm" in orders:
                            print("Duration: " + orders["orderTerm"])

                        if "estimatedCommission" in orders:
                            print("Estimated Commission: " + str(orders["estimatedCommission"]))

                        if "estimatedTotalAmount" in orders:
                            print("Estimated Total Cost: " + str(orders["estimatedTotalAmount"]))
                return preview_id
            except KeyError:
                on_response_error(response, "Order")
                return False
        else:
            on_response_error(response, "Order")
            return False

    def place_order(self, headers, payload):
        url = self.base_url + "/v1/accounts/" + self.account["accountIdKey"] + "/orders/place.json"

        response = self.session.post(url, header_auth=True, headers=headers, data=payload)

        if response is not None and response.status_code == 200:
            print("Order placed successfully!")
            return True
        else:
            on_response_error(response, "Place Order")
            return False
