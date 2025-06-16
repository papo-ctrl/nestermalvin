#!/bin/bash

# Удаляем старую папку, если была
rm -rf dist

# Создаём новую папку
mkdir dist

# Генерим зашифрованный бот в папку dist
pyarmor gen -O dist nestermalvin.py
