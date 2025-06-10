FROM python:3.12-alpine

# Create app directory
WORKDIR /app

# Install app dependencies
COPY sources/requirements.txt ./

RUN pip install -r requirements.txt

# Bundle app source
COPY sources /app

EXPOSE 8000
CMD [ "python", "main.py" ]
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]