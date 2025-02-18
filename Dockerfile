FROM python:3.9-alpine

VOLUME /in
VOLUME /out

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY python python
COPY templates templates

COPY build/distributions/static-bundle.zip .
RUN unzip static-bundle.zip -d static && rm static-bundle.zip

ENTRYPOINT [ "python", "-u", "python/page_generator.py" ]
