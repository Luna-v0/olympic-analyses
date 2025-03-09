FROM python:3.10

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Bundle app source

WORKDIR /usr/src/app/api

EXPOSE 8000


RUN python3 ../data_transformers/get_by_event.py
RUN python3 ../data_transformers/get_by_sport.py
RUN python3 ../data_transformers/get_features_dataset.py
RUN python3 ../data_transformers/global_data.py
RUN python3 ../data_transformers/noc_to_gdp.py
RUN python3 ../data_transformers/polished_dataset.py
RUN python3 ../data_transformers/polished_dataset_2.py

CMD ["python", "run.py"]