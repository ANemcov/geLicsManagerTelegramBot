FROM python:3.12-slim AS builder
WORKDIR /install
RUN apt-get update && apt-get install -y build-essential
COPY sources/requirements.txt ./
RUN pip install --upgrade pip && \
    pip wheel --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
# Create app directory
WORKDIR /app
COPY --from=builder /wheels /wheels
# Install app dependencies
COPY sources/requirements.txt ./

RUN pip install --no-index --find-links=/wheels -r requirements.txt

# Bundle app source
COPY sources /app

EXPOSE 8000
CMD [ "python", "main.py" ]
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]