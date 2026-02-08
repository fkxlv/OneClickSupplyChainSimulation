import requests

payload = {
    "request_id" : "10",
    "region" : "Darmstadt"
}

req = requests.post("http://127.0.0.1:5002", json=payload)
print(req.text)