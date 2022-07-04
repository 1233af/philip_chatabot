import requests

page_id = "4f67c16e763542af98e5359f96ab5b4f"
url = "https://api.notion.com/v1/pages/" + page_id
database_id = '25565bb266d148feadddc82628054b21'
TOKEN = 'secret_g1QaxRFznUeFyCoDGhddpXDOfjkiNoAV6YBwn2Kshpx'

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