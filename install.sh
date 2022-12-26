#!/bin/bash
export `cat .env|grep SQL_USER`
# Build from docker-compose.yml'
docker-compose build
# Start docker-compose, deattach
docker-compose up -d
# Make migration django
docker-compose exec web python manage.py migrate
# Create user django
docker-compose exec web python manage.py createsuperuser
# Copy staticfiles 
docker-compose run --rm web python manage.py collectstatic
# Restart docker compose
docker-compose restart

