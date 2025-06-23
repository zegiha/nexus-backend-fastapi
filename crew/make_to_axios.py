from typing import List
from crewai import Agent, Task, Crew, Process
from pydantic import BaseModel, ValidationError
import json
from crew.llm_instance import llm
import asyncio
import random
from models.raw_article_dto import RawArticleDTO

class LLMContentItem(BaseModel):
    bullet: str
    contents: List[str]


class LLMParsedOutput(BaseModel):
    title: str
    contents: List[LLMContentItem]
    raw: object# 여긴 자유롭게

async def make_to_axios(data: RawArticleDTO)->LLMParsedOutput or None:
    # 🔍 분석 프레임 Agent
    analysis_agent = Agent(
        role='뉴스 분석가',
        goal='뉴스의 전체 내용 파악, 중요성 평가, 구조화 분석을 수행한다.',
        backstory='저널리즘 훈련을 받은 분석가로서, 뉴스의 핵심과 맥락을 정리하고 독자의 이해를 돕는다.',
        llm=llm,
        max_retry_limit=3
    )

    # 🔍 분석 프레임 Task
    analysis_task = Task(
        description=f"""
        {data.contents}
        ---
        위 뉴스 기사를 다음 세 단계로 분석해줘:
        1. 전체 내용 파악: 핵심 메시지와 주요 사실들을 정리
        2. 중요성 평가: 왜 이 기사가 중요한지, 독자에게 어떤 영향을 미치는지 분석
        3. 구조화: 내용을 논리적 순서로 재배열하고, 요점별로 분류
        출력은 아래 형식이어야 해:
        {{
            "overview": "...",
            "importance": "...",
            "structured_points": ["...", "..."]
        }}
        """,
        agent=analysis_agent,
        expected_output="Dict[str, Union[str, List[str]]]"
    )

    # 1. 핵심 문장 추출 Agent
    summary_sentence_agent = Agent(
        role='뉴스 요약 핵심 문장 추출가',
        goal='기사를 한 문장으로 요약해 독자가 왜 읽어야 하는지 알려준다.',
        backstory='저널리즘 전문가로서 뉴스의 본질을 간결하게 요약하는 데 특화되어 있다.',
        llm=llm,
        max_retry_limit=3
    )

    summary_sentence_task = Task(
        description=f"""
        {data.contents}
        ---
        위 뉴스 데이터를 기반으로 '왜 이 기사를 읽어야 하는가'에 대한 핵심 요약 문장을 작성해줘. 
        결과는 반드시 문자열 1개여야 하며, 최대 1문장으로 작성해.
        """,
        agent=summary_sentence_agent,
        expected_output="str (뉴스 핵심 요약 1문장)",
        context=[analysis_task]
    )

    # 2. 요점 추출 Agent
    keypoints_agent = Agent(
        role='뉴스 요점 추출가',
        goal='기사를 이해하는 데 꼭 필요한 요점들을 문장 리스트로 추출한다.',
        backstory='뉴스를 빠르게 파악할 수 있도록 핵심 정보만 정리하는 역할을 한다.',
        llm=llm,
        max_retry_limit=3
    )

    keypoints_task = Task(
        description=f"""
        {data.contents}
        ---
        위 뉴스 데이터를 바탕으로 이 기사를 이해하는 데 꼭 필요한 요점들을 5개 내외로 추출해줘.
        형식은 반드시 리스트형 문자열이어야 해. 예: ["요점1", "요점2", ...]
        """,
        agent=keypoints_agent,
        expected_output="List[str]",
        context=[analysis_task]
    )

    # 3. bullet 및 설명 추출 Agent
    bullet_agent = Agent(
        role='뉴스 요점 정리자',
        goal="요점 리스트 각각에 대해 bullet과 부가 설명 요소를 추출해 [{bullet: str, contents: [str, ...]}] 형식으로 정리한다.",
        backstory='뉴스의 요점을 독자가 쉽게 파악할 수 있도록 시각적으로 정리하는 데 능숙하다.',
        llm=llm,
        max_retry_limit=3
    )

    bullet_task = Task(
        description=f"""
        {data.contents}
        ---
        위 뉴스 데이터를 바탕으로 주어진 요점 리스트에 대해 각 요점의 핵심을 bullet로 요약하고, 이해를 돕기 위한 부가 설명을 리스트로 만들어줘.
        출력 형식은 반드시 [{{bullet: str, contents: [str, ...]}}, ...] 이어야 해.
        """,
        agent=bullet_agent,
        expected_output="List[Dict[str, List[str]]]",
        context=[analysis_task, keypoints_task]
    )

    crew = Crew(
        agents=[analysis_agent, summary_sentence_agent, keypoints_agent, bullet_agent],
        tasks=[analysis_task, summary_sentence_task, keypoints_task, bullet_task],
        process=Process.sequential,
        verbose=True
    )


    # ✅ 재시도 로직 직접 구현
    for i in range(10):
        try:
            res = await crew.kickoff_async()
            break
        except Exception as e:
            err_str = str(e).lower()
            if any(keyword in err_str for keyword in ["592", "529", "overload", "rate_limit", "anthropic"]):
                wait_time = (2 ** i) + random.uniform(0, 1)
                print(f"[make_to_axios] LLM RateLimit 에러 감지, {wait_time:.1f}초 대기 후 재시도 ({i+1}/10)")
                await asyncio.sleep(wait_time)
            else:
                raise
    else:
        print("[make_to_axios] 최대 재시도 초과")
        return None

    # ✅ 결과 파싱
    try:
        parsed = LLMParsedOutput(
            title=res.tasks_output[1].raw,
            contents=json.loads(res.tasks_output[3].raw),
            raw=res
        )
        return parsed

    except ValidationError as e:
        print(f"[make_to_axios] 응답 구조 오류: {e}")
        return None
