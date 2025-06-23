import asyncio
import random
from crewai import Agent, Task, Crew
from crew.llm_instance import llm
from models.raw_article_dto import RawArticleDTO


async def check_is_proper(data: RawArticleDTO):
    check_is_proper_agent = Agent(
        role='뉴스 검증인',
        goal="뉴스가 한국 뉴스인지 검증한다\n꼭 true, false로만 대답한다",
        backstory="전문 뉴스 검증인으로서 뉴스의 내용을 토대로 일반적인 한국 뉴스 기사인지 검증하는데 특화되어있다\n꼭 true, false로만 대답한다",
        llm=llm,
        max_retry_limit=3
    )

    check_is_proper_task = Task(
        description=f"""
title: {data.title}
content: {data.contents}
---
위 뉴스 데이터를 기반으로 이 기사가 한국의 일반적인 기사인지 확인해줘
결과는 반드시 boolean값 1개여야 해
""",
        agent=check_is_proper_agent,
        expected_output="boolean"
    )

    crew = Crew(
        agents=[check_is_proper_agent],
        tasks=[check_is_proper_task],
    )

    for i in range(10):
        try:
            res = await crew.kickoff_async()
            break
        except Exception as e:
            err_str = str(e).lower()
            if any(keyword in err_str for keyword in ["592", "529", "overload", "rate_limit", "anthropic"]):
                wait_time = (2 ** i) + random.uniform(0, 1)
                print(f"[check_is_proper] RateLimit 에러 감지, {wait_time:.1f}초 대기 후 재시도 ({i+1}/10)")
                await asyncio.sleep(wait_time)
            else:
                raise
    else:
        print("[check_is_proper] 최대 재시도 초과")
        return False

    result = res.tasks_output[0].raw
    if result == 'true':
        return True
    elif result == 'false':
        return False
    else:
        print("[check_is_proper] boolean값이 아님")
        return False