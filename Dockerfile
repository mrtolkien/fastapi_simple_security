FROM tiangolo/uvicorn-gunicorn-fastapi:latest

# Installing dev depedencies
RUN pip install pytest python-dotenv
