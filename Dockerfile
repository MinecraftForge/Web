FROM python:3.11

VOLUME /in
VOLUME /out

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY python python
COPY templates templates

ENTRYPOINT [ "python", "python/page_generator.py" ]
