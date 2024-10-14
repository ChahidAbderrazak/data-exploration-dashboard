FROM python:3.7
ARG WEBAPP_SERVER_PORT=8181

# copy the code files
WORKDIR /app
COPY . /app
# Build the environement
RUN ls
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Code PyTesting
RUN pip install pytest  black

# Run the software
EXPOSE $WEBAPP_SERVER_PORT
# CMD ["ls", "-a"]
CMD ["uvicorn", "webapp:app", "--host", "0.0.0.0", "--port", "${WEBAPP_SERVER_PORT}"]