import requests
from decimal import Decimal

class Zibal:
    merchant = "66c0aaafba643d001c510535"
    callback_url = "https://arzdex.shop/"

    def request(self, amount, order_id, mobile, description, multiplexingInfos=None):
        data = {
            'merchant': self.merchant,
            'callbackUrl': self.callback_url,
            'amount': self.convert_decimal_to_float(amount),
            'orderId': order_id,
            'mobile': mobile,
            'description': description,
            'multiplexingInfos': multiplexingInfos
        }

        response = self.postTo('request', data)
        return response

    def verify(self, trackId):
        data = {
            'merchant': self.merchant,
            'trackId': trackId
        }
        return self.postTo('verify', data)

    def postTo(self, path, parameters):
        url = "https://gateway.zibal.ir/v1/" + path
        parameters = self.convert_decimal_to_float(parameters)
        response = requests.post(url=url, json=parameters)
        return response.json()

    def convert_decimal_to_float(self, data):
        if isinstance(data, Decimal):
            return float(data)
        elif isinstance(data, dict):
            return {key: self.convert_decimal_to_float(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.convert_decimal_to_float(item) for item in data]
        else:
            return data
