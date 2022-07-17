import requests
from celery import Celery


TOKEN = 'secret_g1QaxRFznUeFyCoDGhddpXDOfjkiNoAV6YBwn2Kshpx'
database_id = "cd720c822ec3457da911b6faa1fd576d"


app = Celery('tasks', broker="pyamqp://guest@localhost//")


def notion_add_member(name: str, is_checked: bool, TOKEN: str, database_id: str) -> str:

    headers = {
    'Authorization': 'Bearer ' + TOKEN,
    'Notion-Version': '2022-02-22',
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
            'check': {
                'checkbox': is_checked
            },
        },
    }

    response = requests.post('https://api.notion.com/v1/pages', headers=headers, json=json_data)
    return response.text

def notion_add_members(n):
    for i in range(1, n+1):
        notion_add_member('member'+str(i), False, TOKEN, database_id)
        print(i, "done")
    return n


@app.task
def async_notion_add_members(n):
    return notion_add_members(n)


@app.task
def async_notion_add_member(name: str, is_checked: bool, TOKEN: str, database_id: str):
    return notion_add_member(name, is_checked, TOKEN, database_id)


def adv_notion_add_members(n):
    for i in range(1, n+1):
        async_notion_add_member.delay('member'+str(i), False, TOKEN, database_id)
        print(i, "done")
    return n
