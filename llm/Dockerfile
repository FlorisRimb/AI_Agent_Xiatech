FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --verbose

RUN mkdir -p /app/models

COPY . .

RUN hf download TheBloke/Mistral-7B-Instruct-v0.2-GGUF mistral-7b-instruct-v0.2.Q4_K_M.gguf --local-dir /app/models

EXPOSE 5001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001", "--reload"]