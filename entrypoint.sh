#!/usr/bin/env bash


chmod 644 /app/service-account-key.json
exec python main.py
