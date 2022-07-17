from flask import Flask, request, jsonify
import requests
import json
import datetime
import pprint
import pickle
import sys

with open('DBids.p', 'rb') as f:
    DBids = pickle.load(f)
    
TOKEN = sys.argv[1]
print('TOKEN :', TOKEN)
KST = datetime.timezone(datetime.timedelta(hours=9))


application = Flask(__name__)


def get_database_id(user):
    if user in DBids:
        return DBids[user]
    else:
        return None


def timedelta_to_korean_str(td):
    d = td.days
    s = td.seconds
    if d < 0 or s < 0:
        return "지나간 일정입니다."
    
    d, s = abs(d), abs(s)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    
    return f'일정 시작까지 {d}일 {h}시간 {m}분 남았습니다.'


def duration_unit_str_to_timedelta(duration, str_unit):

    dw, dd, dh, dm= 0, 0, 0, 0

    if str_unit == "month":
        dd = duration * 30
    elif str_unit == "week":
        dw = duration
    elif str_unit == "day":
        dd = duration
    elif str_unit == "hour":
        dh = duration
    elif str_unit == "minute":
        dm = duration
    else:
        dm = 1

    return datetime.timedelta(weeks=dw, days=dd, hours=dh, minutes=dm)


def add_event_to_notion(name, sdatetime, edatetime, TOKEN, database_id):
    headers = {
    'Authorization': 'Bearer ' + TOKEN,
    'Notion-Version': '2022-02-22',
    }
    sdatetime = sdatetime.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    edatetime = edatetime.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
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
                    'end': edatetime
                },
            },
        },
    }
    response = requests.post('https://api.notion.com/v1/pages', headers=headers, json=json_data)
    
    return response.text


def notion_get_events_from_datetimes(t1, t2, database_id, TOKEN, has_more = True, next_cursor = None):
    events = []
    headers = {
    'Authorization': 'Bearer ' + TOKEN,
    'Notion-Version': '2022-02-22',
    }

    json_data = {
        "filter": {
            "and": [
            {
                "property": "date",
                "date": {
                    "on_or_after": t1.strftime('%Y-%m-%dT%H:%M:%S.%f%z') #
                }
            },
            {
                "property": "date",
                "date": {
                    "on_or_before": t2.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
                }
            }
            ]
        },
        "page_size": 100
    }
    if next_cursor is not None:
        json_data['start_cursor'] = next_cursor
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    response = requests.post(url, headers=headers, json=json_data)
    res = json.loads(response.text)
    has_more = res['has_more']
    next_cursor = res['next_cursor']
    r = res['results']

    for i in r:
        name = i["properties"]["Name"]["title"][0]["text"]["content"]
        s_date = i["properties"]["date"]["date"]["start"]
        s_date = datetime.datetime.strptime(s_date, '%Y-%m-%dT%H:%M:%S.%f%z')
        e_date = i["properties"]["date"]["date"]["end"]
        e_date = datetime.datetime.strptime(e_date, '%Y-%m-%dT%H:%M:%S.%f%z')
        page_id = i['id']
        events.append({"name": name, "start": s_date, "end": e_date, "page_id": page_id})
        
    if has_more:
    	return events + notion_get_events_from_datetimes(t1, t2, database_id, TOKEN, next_cursor = next_cursor)
    else:
        return events


def sorted_events_ascending_start_time(events):
    return sorted(events, key=lambda e: e["start"])


def notion_get_events_from_name(name, database_id, TOKEN, has_more = True, next_cursor = None):
    events = []
    headers = {
    'Authorization': 'Bearer ' + TOKEN,
    'Notion-Version': '2022-02-22',
    }

    json_data = {
    "filter": {
        "property": "Name",
        "title": {
            "equals": name
    	    }
    	},
    "page_size": 100
	}
    if next_cursor is not None:
        json_data['start_cursor'] = next_cursor
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    response = requests.post(url, headers=headers, json=json_data)
    pprint.pprint(json.loads(response.text))
    res = json.loads(response.text)
    has_more = res['has_more']
    next_cursor = res['next_cursor']
    r = res['results']

    for i in r:
        name = i["properties"]["Name"]["title"][0]["text"]["content"]
        s_date = i["properties"]["date"]["date"]["start"]
        s_date = datetime.datetime.strptime(s_date, '%Y-%m-%dT%H:%M:%S.%f%z')
        e_date = i["properties"]["date"]["date"]["end"]
        e_date = datetime.datetime.strptime(e_date, '%Y-%m-%dT%H:%M:%S.%f%z')
        page_id = i['id']
        events.append({"name": name, "start": s_date, "end": e_date, "page_id": page_id})
        
    if has_more:
        return events + notion_get_events_from_name(name, database_id, TOKEN, next_cursor = next_cursor)
    else:
        return events


def notion_get_event_from_page_id(page_id, TOKEN):
    url = f'https://api.notion.com/v1/pages/{page_id}'
    headers = {
    'Authorization': 'Bearer ' + TOKEN,
    'Notion-Version': '2022-02-22',
    }
    response = requests.get(url, headers=headers)
    response = json.loads(response.text)
    name = response["properties"]["Name"]["title"][0]["text"]["content"]
    s_date = response["properties"]["date"]["date"]["start"]
    s_date = datetime.datetime.strptime(s_date, '%Y-%m-%dT%H:%M:%S.%f%z')
    e_date = response["properties"]["date"]["date"]["end"]
    e_date = datetime.datetime.strptime(e_date, '%Y-%m-%dT%H:%M:%S.%f%z')
    page_id = response['id']
    return {"name": name, "start": s_date, "end": e_date, "page_id": page_id}


def notion_archive_from_page_id(page_id, is_archived, TOKEN):
    url = "https://api.notion.com/v1/pages/" + page_id
    
    headers = {
        "Notion-Version": "2022-02-22",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + TOKEN
    }

    json_data = {
        'archived': is_archived
    }

    response = requests.patch(url, headers=headers, json=json_data)
    return response.text


@application.route("/add_DBid",methods=['POST'])
def add_DBid():
    req = request.get_json()
    pprint.pprint(req)
    
    DBid = req['action']['detailParams']['DBid']['value']
    user = req['userRequest']['user']['id']
    DBids[user] = DBid
    
    with open('DBids.p', 'wb') as f:
    	pickle.dump(DBids, f) 
    
    answer = '성공적으로 등록되었습니다.'
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": answer
                    }
                }
            ]
        }
    }
    
    return res


@application.route("/add_event",methods=['POST'])
def add_event():
    req = request.get_json()
    pprint.pprint(req)
    
    user = req['userRequest']['user']['id']
    database_id = get_database_id(user)
    if database_id is None:
        answer = '먼저 데이터베이스 id를 등록해주세요.'
        res = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": answer
                        }
                    }
                ]
            }
        }
        return res
    
    p = req['action']['params']
    
    name = p['name']
    
    s = json.loads(p['sys_date_time'])
    sdate = s['date']
    stime = s['time']
    sdatetime = sdate + 'T' + stime + '+0900'
    sdatetime = datetime.datetime.strptime(sdatetime, "%Y-%m-%dT%H:%M:%S%z")

    
    d = json.loads(p['duration'])
    duration = d['amount']
    str_unit = d['unit']
    duration = duration_unit_str_to_timedelta(duration, str_unit)

    edatetime = sdatetime + duration
    
    response = json.loads(add_event_to_notion(name, sdatetime, edatetime, TOKEN, database_id))
    name = response["properties"]["Name"]["title"][0]["text"]["content"]
    s_date = response["properties"]["date"]["date"]["start"]
    s_date = datetime.datetime.strptime(s_date, '%Y-%m-%dT%H:%M:%S.%f%z')
    e_date = response["properties"]["date"]["date"]["end"]
    e_date = datetime.datetime.strptime(e_date, '%Y-%m-%dT%H:%M:%S.%f%z')
    page_id = response['id']
    event = {"name": name, "start": s_date, "end": e_date, "page_id": page_id}

    items = []
    name = event['name']
    start = event['start'].strftime('%m월 %d일 %H시 %M분')
    end = event['end'].strftime('%m월 %d일 %H시 %M분')
    time = start + ' ~ ' + end
    items.append({'title': name, 'description': time})
    res = {
      "version": "2.0",
      "template": {
        "outputs": [
            {
                    "simpleText": {
                        "text": "일정이 추가되었습니다."
                    }
            },
          {
            "listCard": {
              "header": {
                "title": timedelta_to_korean_str(event["start"] - datetime.datetime.now(KST))
              },
              "items": items,
              "buttons": [
                {
                  "label": "일정 삭제",
                  "action": "block",
                  "blockId": "62d41e7fc7d05102c2cc7179",
                  "extra": {
                    "name": name,
                    "page_id": page_id
                  }
                }
              ]
            }
          }
        ]
      }
    }


    # 답변 전송
    return jsonify(res)


@application.route("/get_event",methods=['POST'])
def get_event():
    req = request.get_json()
    pprint.pprint(req)
    
    user = req['userRequest']['user']['id']
    database_id = get_database_id(user)
    if database_id is None:
        answer = '먼저 데이터베이스 id를 등록해주세요.'
        res = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": answer
                        }
                    }
                ]
            }
        }
        return res
    
    t1 = datetime.datetime.now(KST)
    t2 = t1 + datetime.timedelta(weeks=1)
    events = notion_get_events_from_datetimes(t1, t2, database_id, TOKEN)
    events = sorted_events_ascending_start_time(events)
    pprint.pprint(events)
    items = []
    for event in events:
        if len(items) >= 5:
            break
        name = event['name']
        start = event['start'].strftime('%m월 %d일 %H시 %M분')
        end = event['end'].strftime('%m월 %d일 %H시 %M분')
        time = start + ' ~ ' + end
        items.append({'title': name, 'description': time})
    pprint.pprint(items)
    res = {
      "version": "2.0",
      "template": {
        "outputs": [
            {
                    "simpleText": {
                        "text": "향후 일주일간의 일정 중 앞에 5개의 일정 입니다."
                    }
            },
          {
            "listCard": {
              "header": {
                "title": '현재 시간 : ' + datetime.datetime.now(KST).strftime('%m월 %d일 %H시 %M분')
              },
              "items": items
            }
          }
        ]
      }
    }

    # 답변 전송
    return jsonify(res)


@application.route("/delete_event",methods=['POST'])
def delete_event():
    req = request.get_json()
    pprint.pprint(req)
    
    user = req['userRequest']['user']['id']
    database_id = get_database_id(user)
    if database_id is None:
        answer = '먼저 데이터베이스 id를 등록해주세요.'
        res = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": answer
                        }
                    }
                ]
            }
        }
        return res
    
    t1 = datetime.datetime.now(KST)
    t2 = t1 + datetime.timedelta(weeks=4)
    events = notion_get_events_from_datetimes(t1, t2, database_id, TOKEN)
    events = sorted_events_ascending_start_time(events)
    items = []
    r = []
    cnt = 0
    for event in events:
            name = event['name']
            start = event['start'].strftime('%m월 %d일 %H시 %M분')
            end = event['end'].strftime('%m월 %d일 %H시 %M분')
            time = start + ' ~ ' + end
            page_id = event["page_id"]
            t = {
                    "title": name,
                    "description": time,
                    "action": "block",
                    "blockId": "62d41e7fc7d05102c2cc7179",
                    "extra": {
                            'name': name,
                            "page_id": page_id
                    }
            }
            r.append(t)
            cnt += 1
            if cnt >= 5:
                    items.append({"items": r})
                    r = []
                    cnt = 0
    if len(r) > 0:
            items.append({"items": r})

    for i in range(len(items)):
            items[i]['header'] = {'title': '향후 4주간의 일정 ' + str(i+1)+'/'+str(len(items))}

    res = {
            "version": "2.0",
            "template": {
                    "outputs": [
                        {
                    	"simpleText": {
                        	"text": "향후 4주간의 일정입니다. 삭제 할 일정을 눌러주세요."
                    		}
             			},
                            {
                                    "carousel": {
                                            "type": "listCard",
                                            "items": items
                                    }
                            }
                    ],
            }
    }
    pprint.pprint(res)
    return jsonify(res)


@application.route("/delete_event_from_id",methods=['POST'])
def delete_event_from_id():
    req = request.get_json()
    pprint.pprint(req)
    
    page_id = req['action']['clientExtra']['page_id']
    event = notion_get_event_from_page_id(page_id, TOKEN)
    name = event['name']
    start = event['start'].strftime('%m월 %d일 %H시%M분')
    end = event['end'].strftime('%m월 %d일 %H시%M분')
    time = start + ' ~ ' + end
    notion_archive_from_page_id(page_id, True, TOKEN)
    
    res = {
      "version": "2.0",
      "template": {
        "outputs": [
          {
            "listCard": {
              "header": {
                "title": "이 일정이 삭제되었습니다."
              },
              "items": [
                {
                  "title": name,
                  "description": time,
                  }
              ],
              "buttons": [
                {
                  "label": "일정 복구",
                  "action": "block",
                  "blockId": "62d42529903c8b5a8004f70f",
                  "extra": {
                    "name": name,
                    "page_id": page_id
                  }
                }
              ]
            }
          }
        ]
      }
    }
    return res


@application.route("/restore_event_from_id",methods=['POST'])
def restore_event_from_id():
    req = request.get_json()
    pprint.pprint(req)
    
    page_id = req['action']['clientExtra']['page_id']
    notion_archive_from_page_id(page_id, False, TOKEN)
    
    answer = '일정을 복구 했습니다.'
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": answer
                    }
                }
            ]
        }
    }
    return res


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000, threaded=True)
    
    
# https://developers.notion.com/docs/authorization#exchanging-the-grant-for-an-access-token
# 확인 하기