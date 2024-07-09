from hmac import new
from time import time
from hashlib import sha256
import requests
from urllib.parse import urlencode
from typing import Optional
import sqlite3

###############################
# IMPORTANT -  Use https://nordvpn.com/ip-lookup/ to get your IP address
###############################


BASE_URL = "https://api.binance.com"  # production base url
# BASE_URL = 'https://testnet.binance.vision' # testnet base url
requests.packages.urllib3.util.connection.HAS_IPV6 = False

def get_api():
    file_name = "0-Settings/Files/api.db"
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    cursor.execute("Select * FROM info")
    
    list_check = cursor.fetchall()
    
    #COMES OUT as a LIST
    recent_log = list_check[-1] #Most Recent data gathered from file
  
    connection.commit()
    #Closing the database
    connection.close()

    return recent_log

class Client:

    """ ======  Initialise Variables ====== """
    
    def __init__(self, api_key: Optional[str], secret_key: Optional[str], method, url_path, payload):
        self.api_key = api_key
        self.secret_key = secret_key
        self.method = method
        self.BASE_URL = BASE_URL
        self.url_path = url_path
        self.payload = payload
        

    def hashing(self, query_string):
        return new(
            self.secret_key.encode("utf-8"), query_string.encode("utf-8"), sha256
        ).hexdigest()


    def get_timestamp(self):
        return int(time() * 1000)


    def dispatch_request(self):
        session = requests.Session()
        session.headers.update(
            {"Content-Type": "application/json;charset=utf-8", "X-MBX-APIKEY": self.api_key}
        )
        return {
            "GET": session.get,
            "DELETE": session.delete,
            "PUT": session.put,
            "POST": session.post,
        }.get(self.method, "GET")


    # used for sending request requires the signature
    def send_signed_request(self):
        query_string = urlencode(self.payload, True)
        if query_string:
            query_string = "{}&timestamp={}".format(query_string, self.get_timestamp())
        else:
            query_string = "timestamp={}".format(self.get_timestamp())

        url = (
            self.BASE_URL + self.url_path + "?" + query_string + "&signature=" + self.hashing(query_string)
        )
        #print("{} {}".format(self.method, url))
        params = {"url": url, "params": {}}
        response = self.dispatch_request()(**params)
        return response.json()


    # used for sending public data request
    def send_public_request(self):
        query_string = urlencode(self.payload, True)
        url = self.BASE_URL + self.url_path
        if query_string:
            url = url + "?" + query_string
        print("{}".format(url))
        response = self.dispatch_request("GET")(url=url)
        return response.json()



def run(method, path, params, r_type):
    # r_type = 0 if the request is private or 1 if the request is public
    try:
        keys = get_api()
        KEY = keys[0]
        SECRET = keys[1]

        if r_type == 0:
            return Client(KEY, SECRET, method, path, params).send_signed_request()
        elif r_type == 1:
            return Client(KEY, SECRET, method, path, params).send_public_request()

    except Exception as e:
        print(f"Misc/Binance_Rest_Api.py: {e}")
 

"""KEY = "GTgis85VIseFCzAo7DYbQGeIJFMZDyprbsBoK7M5VMdxMUYEcfE9fsENnOPYcNL6"
SECRET = "op5SxVWbBbclYdSsYze0WSIPuYR8xbpTAuustfQ9S11ZuMObG7ul0NgZ4uX8yyYh"""


""" ======  end of CLASS ====== """

# TEST FOR HIR
"""params = {
    "assets": "BTC",
    "isIsolated": "FALSE"
}

method = "GET"
path = "/sapi/v1/margin/next-hourly-interest-rate"
r_type = 0


   


print(run(method, path, params, r_type))
"""
















"""### public data endpoint, call send_public_request #####
# get klines
response = send_public_request(
    "/api/v3/klines", {"symbol": "BTCUSDT", "interval": "1d"}
)
print(response)
"""

### USER_DATA endpoints, call send_signed_request #####
# get account informtion
# if you can see the account details, then the API key/secret is correct


#response = send_signed_request("GET", "/api/v3/account")
#print(response)

"""params = {
    "assets": "BTC",
    "isIsolated": "FALSE"
}

response = send_signed_request("GET", "/sapi/v1/margin/next-hourly-interest-rate", params)
print(response)"""





"""
# # place an order
# if you see order response, then the parameters setting is correct
params = {
    "symbol": "BNBUSDT",
    "side": "BUY",
    "type": "LIMIT",
    "timeInForce": "GTC",
    "quantity": 1,
    "price": "20",
}
response = send_signed_request("POST", "/api/v3/order", params)
print(response)


# User Universal Transfer
params = {"type": "MAIN_MARGIN", "asset": "USDT", "amount": "0.1"}
response = send_signed_request("POST", " /sapi/v1/asset/transfer", params)
print(response)


# New Future Account Transfer (FUTURES)
params = {"asset": "USDT", "amount": 0.01, "type": 2}
response = send_signed_request("POST", "/sapi/v1/futures/transfer", params)
print(response)


"""