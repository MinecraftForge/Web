FROM python:3.9-alpine

VOLUME /in
VOLUME /out

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY python python
COPY templates templates

COPY build/distributions/files-bundle.zip .
RUN unzip files-bundle.zip -d static && rm files-bundle.zip

ENTRYPOINT [ "python", "-u", "python/page_generator_service.py" ]
