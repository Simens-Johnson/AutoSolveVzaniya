import httpx, time,random

token = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzIiwianRpIjoiYjFjZWU1ZDMxZTBiNzlmMTc1ZmRkNWI5ZGIzZmZlMTU3ZGM1MWVjMzc0NzY0NTE4ZGJiMjExOWRmZmZhYjU3NjVmNDRiOTJhZjE5OWNlZGQiLCJpYXQiOjE2OTgyNDEzMDYuMDc5Mjc2LCJuYmYiOjE2OTgyNDEzMDYuMDc5Mjc4LCJleHAiOjE3Mjk4NjM3MDYuMDc2ODIxLCJzdWIiOiIzNjQ2ODIiLCJzY29wZXMiOltdfQ.C5ibgzu2l58tQcD1uP3OLzWtiY9G9zop91ws2vo45Nvs0tNOHzFw5jOtuQHJ5cWTuwVAB84mmKkmIybO-H_JloCsSK8NOYarLkztLE8oLhB8X4sfTG8QS-D8nXoTdJqLS35frCVkPlxqKTJhNZfwbJDfqeM8nhH2Vvi_QJHEpErpJ14otIoCT4z9TLloVbJI3tCimEcjfSG3L0lDK_SI_RvZvXpQ2DJhDVdvxb5xEJdVf5VtDTJfkPkpauiiddC-_-g6LjSnbzG3XdLQNnyP2fubSYoc6-C7a4oz7AyleBtBG0OaxmnmhP23wJE2Shl4KoMWLteIWPyYGGSZX2d34mtJsJfizIA8VdFLdXQIsuL3Iq6lCcx5OJEOjbQvsM69FXAiAOGQRiXV-8nRAWQ_NYcxyT8JP7KvnlcptNSonI-YBc1ti8qwh8qk3No6m2lMfK_FhDMyQZTY2qV6Y5RV6V6dIv2KBzGaWV7QXxZcyiSPEo0uP5zpEgWxzIBFmtg6_jFlI2s2ei-uPsseLBJne4WjtBiaxv0HQaBxIFWjzLZCYYv44QTYpTx4LHQLbqnbhjKx9P11Y7ukkrGxBL8WTa5DT5dg9GWbqVHyXmz2j309wH-ppB4ZbDU9A5WLSB8vWjEJ5lcDT8EfD9P6jFI6HDAW94XLVWRyHlgG_sHLW7E'

ids = int(input('Введите айди группы '))
group_id = int(input('Введите айди урока '))
tasks = httpx.get(
    f'https://vznaniya.ru/api/v2/lessons/{group_id}?group_id={ids}',
    headers={
        "Authorization": token
    }
)
print(tasks.text)
tasks = tasks.json()['data']["additional_info"]['tasks']
print(tasks)
for task in tasks:
    for i in range(int(tasks[task])):
        p = httpx.post(
            f'https://vznaniya.ru/api/v2/lr/complete-task/{task}/{group_id}',
            json={
                'group_id': ids
            },
            headers={
                "Authorization": token
            }
        )
        print(p.status_code, p.text)

test = httpx.get(
    f'https://vznaniya.ru/api/v2/lesson-words/filter?lesson_id={group_id}&timestamp={time.time()-random.randint(270,330)}',
    headers={
        "Authorization": token
    }

).json()['data']

answers = []
for t in test:
    answers.append({
        'id': t['id'],
        'test_type': "write_word",
        'text': t["text"]
    })

p = httpx.post(
    'https://vznaniya.ru/api/v2/lr/counting-test',
    headers={
        "Authorization": token
    },
    json={
        "lesson_id":group_id,
        'group_id': ids,
        "answers": answers
    }
)
print(p.status_code)