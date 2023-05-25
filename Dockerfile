FROM python:3.11.3-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip
# pipenv run pip freeze > requirements.txt
# delete requirements: pywin32==306 & pywinpty==2.0.10
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python setup.py develop

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]

# docker build -t bt_project .
# docker run -d -p 8888:8888 bt_project