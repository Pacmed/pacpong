FROM python:3.7

# Copy the files to the container
COPY . /www

# Install the pingpong16 package
RUN cd /www && pip install -e .

# Run the script
CMD ["python", "-u", "/www/run.py"]
