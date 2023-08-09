FROM python:3.9


WORKDIR /app

RUN pip install --upgrade pip

COPY requirements/requirements.project.txt .

RUN pip install -r requirements.project.txt


COPY . .

CMD [ "make", "run" ]
