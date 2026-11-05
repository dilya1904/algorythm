# Google Cloud Run 배포를 위한 경량화 Python Dockerfile
FROM python:3.11-slim

# 표준 출력/에러 버퍼링 방지 및 파이썬 바이트코드 생성 억제
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# 시스템 의존성 및 pip 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스코드 복사
COPY algorithms.py main.py ./

# Cloud Run 기본 포트 문서화
EXPOSE 8080

# Cloud Run 환경변수 PORT를 주입받아 uvicorn 서버 실행
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]

