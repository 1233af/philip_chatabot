import requests
from datetime import *

database_id = '25565bb266d148feadddc82628054b21'
TOKEN = 'secret_g1QaxRFznUeFyCoDGhddpXDOfjkiNoAV6YBwn2Kshpx'


def str_datetime(datetime):
    return datetime.strftime("%Y-%m-%d %H:%M:%S")


def add_event_to_notion(name, sdatetime, edatetime, TOKEN, database_id):

    sdatetime = str_datetime(sdatetime)
    edatetime = str_datetime(edatetime)

    headers = {
    'Authorization': ('Bearer ' + TOKEN),
    'Notion-Version': '2021-08-16',
    }

    json_data = {
        'parent': {
            'type': 'database_id',
            'database_id': database_id,
        },
        'properties': {
            'Name': {
                'type': 'title',
                'title': [
                    {
                        'type': 'text',
                        'text': {
                            'content': name,
                        },
                    },
                ],
            },
            'date': {
                'date': {
                    'start': sdatetime,
                    'end': edatetime,
                    'time_zone': 'Asia/Seoul',
                },
            },
        },
    }

    response = requests.post('https://api.notion.com/v1/pages', headers=headers, json=json_data)

    print(f"Added {name} at {sdatetime} ~ {edatetime} on database {database_id}")
    return 0
    
def 샤워하기(t):
    s = datetime.fromisoformat('2022-07-03 06:30:00')
    e = s + timedelta(hours=1)
    d = timedelta(days=1)
    n0 = '샤워하기'

    for i in range(t):
        n = n0 + str(i)
        add_event_to_notion(n, s, e, TOKEN, database_id)
        s += d
        e += d

샤워하기(30)