# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# create directory for the app user
RUN mkdir /app
WORKDIR /app

# # The environment variable ensures that the python output is set straight
# # to the terminal without buffering it first
ENV PYTHONUNBUFFERED=1

# Install system dependencies in venv
RUN python3 -m venv /opt/venv
COPY requirements.lock.txt .
RUN . /opt/venv/bin/activate && python3 -m pip install --no-cache-dir -r requirements.lock.txt

# Copy the current directory contents into the container at /app
COPY . /app

# run the command to start streamlit frontend
# CMD . /opt/venv/bin/activate && streamlit run main.py
CMD ["/bin/sh", "-c", ". /opt/venv/bin/activate && streamlit run Main.py"]
