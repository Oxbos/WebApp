#!/bin/bash

# Обновление списка пакетов
sudo apt update

# Установка необходимых пакетов для добавления HTTPS репозитория
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Добавление официального ключа GPG Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавление официального репозитория Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Обновление списка пакетов после добавления репозитория
sudo apt update

# Установка Docker Engine
sudo apt install -y docker.io

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Установка Docker Machine
base=https://github.com/docker/machine/releases/download/v0.16.2 \
  && curl -L $base/docker-machine-$(uname -s)-$(uname -m) >/tmp/docker-machine \
  && sudo mv /tmp/docker-machine /usr/local/bin/docker-machine \
  && sudo chmod +x /usr/local/bin/docker-machine

# Добавление текущего пользователя в группу docker (чтобы не использовать sudo при каждой команде)
sudo usermod -aG docker $USER

# Перезагрузка для применения изменений в группах
sudo systemctl restart docker

echo "Docker и связанные компоненты успешно установлены."

apt install python3-pip
# Install python components

pip3 install -r requirements.txt
# install python components

pip3 install flask_sqlalchemy

pip install psycopg2-binary 
