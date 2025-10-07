from alith.lazai import Client
import requests

client = Client()
node = "0xD878Fa6c04d99654Fb38d1245Fc6Ec2acE8913f0" #change this address with one you registered with admin 

try:
    print("try to get user")
    user =  client.get_user(client.wallet.address)
    print(user)
except Exception as e:
    print("try to get user failed")
    print(e)
    print("try to add user failed")
    client.add_user(1000000)
    print("user added")


print("try to get query account")

url = client.get_query_node(node)[1]
print(url)
headers = client.get_request_headers(node)
print("request headers:", headers)
print(
    "request result:",
    requests.post(
        f"{url}/query/rag",
        headers=headers,
        json={
            "file_id": 10, #change with your file_id 
            "query": "summarise the best character?",
        },
    ).json(),
)