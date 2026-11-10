FROM python:3.13-alpine
WORKDIR /app
COPY public/ /app/public/
COPY server.py /app/server.py
EXPOSE 8099
CMD ["python3", "-u", "/app/server.py"]
