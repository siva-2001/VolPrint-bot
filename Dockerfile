FROM python:3.14-rc-slim-bookworm
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
EXPOSE 80