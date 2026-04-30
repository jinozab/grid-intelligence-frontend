FROM python:3.10.6-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD streamlit run app.py --server.port $PORT --server.address 0.0.0.0
