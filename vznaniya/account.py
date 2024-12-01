import httpx
from typing import List, Optional

from vznaniya.types.lesson import Lesson


class Account:
    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token

    async def get_token(self, email: str, password: str) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://vznaniya.ru/api/v2/auth/login',
                json={"email": email, "password": password}
            )
            if response.status_code == 200:
                self.token = response.json().get("data", {}).get("access_token")
                return self.token
            return None

    async def get_lessons(self) -> List[Lesson]:
        if not self.token:
            raise ValueError("Token is not set. Please authenticate first.")

        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get('https://vznaniya.ru/api/v2/lessons/filter', headers=headers)
            response_data = response.json()
            last_page = response_data.get('meta', {}).get('last_page', 1)
            actual_lessons: List[Lesson] = []

            for page in range(1, int(last_page) + 1):
                paged_response = await client.get(
                    f'https://vznaniya.ru/api/v2/lessons/filter?page={page}',
                    headers=headers
                )
                lessons = paged_response.json().get('data', [])
                for lesson_data in lessons:
                    if lesson_data.get("test_result") == 0:
                        actual_lessons.append(Lesson(lesson_data))
                    else:
                        return actual_lessons

            return actual_lessons