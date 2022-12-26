# Dockerfile

# Pull base image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /movie_admin
RUN mkdir "staticfiles"
# Create user web
RUN groupadd -r web && useradd -d /movie_admin -r -g web web \
    && chown web:web -R /movie_admin

USER web
ENV PATH="/movie_admin/.local/bin:$PATH"
COPY requirements.txt requirements.txt
# Install dependencies
RUN pip install --disable-pip-version-check --user --no-cache-dir -r requirements.txt
# Copy project
COPY   .   .
EXPOSE 8000
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi"]



