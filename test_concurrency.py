import json
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen

URL = "http://127.0.0.1:8000/initialize-payment"


def make_payment():
    data = json.dumps({
        "user_id": 4,
        "merchant_id": 1,
        "amount": 500
    }).encode()

    request = Request(
        URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urlopen(request) as response:
            return response.status, response.read().decode()

    except Exception as e:
        return "ERROR", str(e)


with ThreadPoolExecutor(max_workers=2) as executor:
    results = list(executor.map(lambda _: make_payment(), range(2)))


for result in results:
    print(result)