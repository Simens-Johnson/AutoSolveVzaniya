import httpx

from vznaniya.types.lesson import Lesson

class Account():
    def __init__(self, token = None) -> None:
        self.token = token

    async def getToken(self, email, password):
        async with httpx.AsyncClient() as r:
            self.token = await r.post(
                'https://vznaniya.ru/api/v2/auth/login',
                json={
                    "email": email,
                    "password": password
                }
            )
        if self.token.status_code == 200:
            return self.token.json().get("data").get("access_token")
        return False

    async def getLessons(self) -> list[Lesson]:
        async with httpx.AsyncClient() as r:
            res = await r.get('https://vznaniya.ru/api/v2/lessons/filter', headers={"Authorization": f"Bearer {self.token}"})
            actual_lessons = []

            is_end = False
            for page in range(int(res.json().get('meta').get('last_page'))):
                lessons = await r.get(f'https://vznaniya.ru/api/v2/lessons/filter?page={page}', headers={"Authorization": f"Bearer {self.token}"})
                for lesson in lessons.json().get('data'):
                    if lesson.get("test_result") == 0:
                        actual_lessons.append(Lesson(lesson))
                    else:
                        is_end = True
                        break
                if is_end:
                    break

            return actual_lessons