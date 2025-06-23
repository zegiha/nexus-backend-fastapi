import asyncio

llm_request_queue = asyncio.Queue()

async def llm_worker():
    while True:
        task = await llm_request_queue.get()
        try:
            print('llm worker start')
            await task()  # task는 LLM 요청을 래핑한 async 함수
        except Exception as e:
            print(f"LLM 작업 실패: {e}")
        finally:
            llm_request_queue.task_done()

# 워커 여러 개 띄우되, 예를 들어 1~3개만 동시 실행
async def start_llm_workers(num_workers=1):
    workers = [asyncio.create_task(llm_worker()) for _ in range(num_workers)]
    await llm_request_queue.join()  # 큐가 비워질 때까지 대기
    for w in workers:
        w.cancel()
