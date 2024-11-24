FROM python:3.10

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Bundle app source

WORKDIR /usr/src/app/api

EXPOSE 8000

CMD ["python", "run.py"]