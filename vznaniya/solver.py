import httpx
import random
import time
from typing import List, Dict


class LessonSolver:
    def __init__(self, lesson_id: int, lesson_group_id: int, token: str) -> None:
        self.lesson_id = lesson_id
        self.lesson_group_id = lesson_group_id
        self.headers = {"Authorization": f"Bearer {token}"}

    async def solve_tasks(self) -> None:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://vznaniya.com/api/v2/lessons/{self.lesson_id}?group_id={self.lesson_group_id}",
                headers=self.headers
            )
            tasks = response.json().get('data', {}).get("additional_info", {}).get('tasks', {})
            for task_id, count in tasks.items():
                for _ in range(int(count)):
                    await client.post(
                        f"https://vznaniya.com/api/v2/lr/complete-task/{task_id}/{self.lesson_id}",
                        json={'group_id': self.lesson_group_id},
                        headers=self.headers
                    )

    async def solve_test(self) -> None:
        timestamp = time.time() - random.randint(270, 330)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://vznaniya.com/api/v2/lesson-words/filter?lesson_id={self.lesson_id}&timestamp={timestamp}",
                headers=self.headers
            )
            test_data = response.json().get('data', [])

            answers: List[Dict[str, str]] = [
                {
                    'id': item['id'],
                    'test_type': "write_word",
                    'text': item["text"]
                }
                for item in test_data
            ]

            await client.post(
                'https://vznaniya.com/api/v2/lr/counting-test',
                headers=self.headers,
                json={
                    "lesson_id": self.lesson_id,
                    "group_id": self.lesson_group_id,
                    "answers": answers
                }
            )