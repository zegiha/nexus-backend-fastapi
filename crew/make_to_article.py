from models.article import Article_contents, article_contents_adapter
from crew.make_to_axios import LLMParsedOutput
from crewai import Agent, Task, Crew, Process
import json
from crew.llm_instance import llm
import asyncio
import random

async def make_to_article(data: LLMParsedOutput)->Article_contents | None:
    format_to_article_agent = Agent(
        role="뉴스 형식 변환 전문가",
        goal="뉴스 데이터를 지정된 JSON 형식에 맞게 구조화한다",
        backstory=(
            "당신은 수많은 뉴스 콘텐츠를 구조화해본 뉴스 전문 데이터 포맷터입니다. "
            "기사 내용을 자연스럽고 논리적인 흐름에 맞게 subject, description, list 등으로 변환하며, "
            "주어진 출력 규칙과 JSON 스키마를 철저히 따릅니다."
        ),
        llm=llm,
        max_retry_limit=3,
    )

    format_to_article_task = Task(
        description=f"""
다음은 LLM이 분석한 뉴스 기사 데이터입니다:

{data}

이 데이터를 아래의 규칙에 맞는 JSON 형식으로 변환하세요.

📌 출력 예시 구조:
{get_example_protocol()}
{get_prompt_rule()}
🎯 목표:
주어진 내용을 바탕으로 명확하고 논리적인 단락으로 나누고, 각 단락을 위 규칙에 따라 JSON 배열 안에 작성하세요.""",
        expected_output="정해진 JSON 형식의 배열 (Python dict 형태)",
        agent=format_to_article_agent
    )

    linking_article_agent = Agent(
        role="내용 연결 전문가",
        goal="논리적 흐름에 맞게 주어진 글 중 연결 시 논리 흐름 파악 및 이해에 도움이 되는 부분을 scroll로 연결한다",
        backstory=(
            "당신은 수많은 글의 논리적 흐름을 연결해본 뉴스 전문 내용 연결 전문가입니다."
            "기사의 내용을 자연스럽고 논리적 흐릅에 맞게 scroll로 변환하여 연결하십시오."
            "to는 클릭 시 스크롤될 단락의 id를 지정합니다.\n존재하는 id만을 이용하십시오."
            "주어진 출력 규칙과 JSON 스키마를 철저히 따릅니다."
        ),
        llm=llm,
        max_retry_limit=3
    )

    linking_article_task = Task(
        description=f"""다음은 당신이 연결할 뉴스 기사 데이터입니다:

{data}

이 데이터를 아래의 규칙에 맞는 JSON 형식으로 연결하세요.

📌 출력 예시 구조:
{get_example_protocol()}
{get_prompt_rule()}
🎯 목표:
주어진 내용을 바탕으로 명확하고 논리적인 연결이 필요한 단락을 탐색하고, 각 단락을 위 규칙에 따라 JSON 배열 안에서 연결하세요.
연결이 필요한 내용만을 scroll로 감싸고, 이전 내용과 이후 내용은 기존 type대로 작성하세요.
예시
[
{{

 "type": "description",

"id": "investigation-desc1",

"content": "구체적인 수사 방향에 대해 '차차 논의하겠다'는 입장을 표명하며, "

}},

{{

“type”: “scroll”,

“to”: “investigation-direction”,

“content”: “수사 방향”

}},

{{

 "type": "description",

"id": "investigation-desc2",

"content": "에 대한 언급을 자제하고 신중한 태도를 유지하고 있습니다."

}},
]
""",
        expected_output="정해진 JSON 형식의 배열 (Python dict 형태)",
        agent=linking_article_agent
    )

    crew = Crew(
        agents=[format_to_article_agent, linking_article_agent],
        tasks=[format_to_article_task, linking_article_task],
        process=Process.sequential
    )

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

    try:
        parsed_json = json.loads(res.raw)

        if "contents" in parsed_json and parsed_json["contents"] is not None:
            res = article_contents_adapter.validate_python(parsed_json["contents"])
        else:
           res = article_contents_adapter.validate_python(parsed_json)
        return res

    except Exception as e:
        print("파싱 오류:", e)
        return None

def get_example_protocol():
    with open("./protocol.json", 'r', encoding='utf-8') as file:
        return json.dumps(json.load(file), ensure_ascii=False, indent=2)

def get_prompt_rule():
    return """📏 반드시 지켜야 할 규칙:
1. 모든 항목은 JSON 배열 내부에 위치해야 함
2. "content" 필드에는 문자열만 포함 (객체 금지)
3. "scroll", "link"는 반드시 description/list와 같은 레벨에서 형제로 위치
4. "list"는 다음 구조만 허용:
   {{
     "type": "list",
     "contents": [
       {{ "id": "list-1", "content": "항목 내용1" }},
       {{ "id": "list-2", "content": "항목 내용2" }}
     ]
   }}
5. 모든 id는 고유 문자열이어야 함
6. 각 단락은 다음 구성 순서를 따라야 함:
   subject → description → (scroll) → (footnote) → (list) → (link) → (media)"""
