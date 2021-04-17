FROM python:3.9

VOLUME /in
VOLUME /out

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY python .
COPY templates .

ENTRYPOINT [ "python", "python/page_generator.py" ]
