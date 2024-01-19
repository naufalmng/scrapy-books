import requests

res = requests.get('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt')
res.raise_for_status()
test = res.text.strip().splitlines()
print(test)
