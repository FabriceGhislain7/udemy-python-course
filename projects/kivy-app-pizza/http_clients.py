from kivy.network.urlrequest import UrlRequest
import json


class HttpClient:
    def get_pizzas(self, on_complete):
        url = "https://fabricedeveloper.pythonanywhere.com/api/GetPizzas"

        def data_received(reg, result):
            data = json.loads(result)
            pizzas_dict = []
            for i in data:
                pizzas_dict.append(i["fields"])
            print("data_received")
            if on_complete:
                on_complete(pizzas_dict)

        req = UrlRequest(url, on_succes=data_received)