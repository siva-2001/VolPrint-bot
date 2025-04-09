FROM python:3.14-rc-slim-bookworm
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "TgBot..3
py"]