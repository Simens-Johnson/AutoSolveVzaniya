import httpx, time, random

class LessonSolver:

    def __init__(self, lesson_id, lesson_group_id, token) -> None:
        self.lesson_id = lesson_id
        self.lesson_group_id = lesson_group_id
        self.token = token
    
    async def solveTasks(self):
        async with httpx.AsyncClient() as r:
            tasks = await r.get(
                f'https://vznaniya.ru/api/v2/lessons/{self.lesson_id}?group_id={self.lesson_group_id}',
                headers={"Authorization": f'Bearer {self.token}'}
            )
            tasks = tasks.json()['data']["additional_info"]['tasks']
            for task in tasks:
                for i in range(int(tasks[task])):
                    await r.post(
                        f'https://vznaniya.ru/api/v2/lr/complete-task/{task}/{self.lesson_id}',
                        json={'group_id': self.lesson_group_id},
                        headers={"Authorization": f'Bearer {self.token}'}
                    )  
    
    async def solveTest(self):
        async with httpx.AsyncClient() as r:
            test = (await r.get(
                f'https://vznaniya.ru/api/v2/lesson-words/filter?lesson_id={self.lesson_id}&timestamp={time.time()-random.randint(270,330)}',
                headers={"Authorization": f'Bearer {self.token}'}
            )).json()['data']

            answers = []
            for t in test:
                answers.append({
                    'id': t['id'],
                    'test_type': "write_word",
                    'text': t["text"]
                })

            await r.post(
                'https://vznaniya.ru/api/v2/lr/counting-test',
                headers={"Authorization": f'Bearer {self.token}'},
                json={
                    "lesson_id": self.lesson_id,
                    'group_id': self.lesson_group_id,
                    "answers": answers
                }
            )