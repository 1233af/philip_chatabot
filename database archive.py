import requests

page_id = "4f67c1...59f96ab5b4f"
url = "https://api.notion.com/v1/pages/" + page_id
database_id = '25565bb26...82628054b21'
TOKEN = 'secret_g1QaxRFznU...AV6YBwn2Kshpx'

headers = {
    "Notion-Version": "2022-02-22",
    "Content-Type": "application/json",
    "Authorization": "Bearer " + TOKEN
}

json_data = {
    'parent': {
        'database_id': database_id,
    },
    'archived': False
}

response = requests.patch(url, headers=headers, json=json_data)
print(response.text)
