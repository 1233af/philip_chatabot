import requests

page_id = "4f6...ab5b4f"
url = "https://api.notion.com/v1/pages/" + page_id
database_id = '25565bb26...628054b21'
TOKEN = 'secret_g1Qa...NoAV6YBwn2Kshpx'

headers = {
    "Notion-Version": "2022-02-22",
    "Content-Type": "application/json",
    "Authorization": "Bearer " + TOKEN
}

json_data = {
    'parent': {
        'database_id': database_id,
    },
    'properties': {
        'Name': {
            'title': [
                {
                    'type': 'text',
                    'text': {
                        'content': "샤워하지말기"
                    }
                }
            ]
        }
    }
}

response = requests.patch(url, headers=headers, json=json_data)
print(response.text)
