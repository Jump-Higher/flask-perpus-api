#!/bin/bash

# Load environment variables from .env
export $(cat .env | xargs)

# Run Gunicorn with your Flask app
gunicorn wsgi:app -b '0.0.0.0:5000'
