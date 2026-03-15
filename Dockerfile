#FROM python:3.10-slim
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y ca-certificates python3-pip python3
#RUN mkdir -p /app
WORKDIR /app
COPY requirements.txt /app/
#RUN cd /app
RUN pip3 install -r requirements.txt  --break-system-packages
  
CMD ["python3","api.py"]
