# from database.db import engine, Base
#
# def init_db():
#     # 동기식으로 DB 연결을 시작합니다
#     with engine.begin() as conn:
#         # 메타데이터에 정의된 모든 테이블을 생성합니다
#         Base.metadata.create_all(bind=conn)
#
# if __name__ == "__main__":
#     init_db()
