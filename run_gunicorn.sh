#!/bin/sh
gunicorn -b unix:/tmp/gunicorn.sock wsgi:application
