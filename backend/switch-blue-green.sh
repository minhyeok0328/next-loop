#!/bin/bash

NGINX_CONFIG="/etc/nginx/sites-available/default"
DOCKER_COMMAND_HEAD="docker compose -f docker-compose.production.yml"
CURRENT_ENV=$(grep "proxy_pass" $NGINX_CONFIG | grep -o "blue_app\|green_app")

# blue green switch할 변수 추가
if [ "$CURRENT_ENV" = "blue_app" ]; then
    NEW_ENV="green_app"
else
    NEW_ENV="blue_app"
fi

# 이미지 새로 빌드
sudo $DOCKER_COMMAND_HEAD build
sudo $DOCKER_COMMAND_HEAD restart $NEW_ENV

# 혹시 모르니까 30초 정도 지연
sleep 30

# nginx proxy_pass 값 blue green switch
sudo sed -i "/proxy_pass/s/$CURRENT_ENV/$NEW_ENV/" $NGINX_CONFIG

# switch 하고 nginx 테스트 문제 없으면 switch 아니면 원래대로
if sudo nginx -t; then
    sudo nginx -s reload
    echo "Switched from $CURRENT_ENV to $NEW_ENV and reloaded Nginx."
else
    echo "Nginx configuration test failed. Rolling back changes."
    sudo sed -i "/proxy_pass/s/$NEW_ENV/$CURRENT_ENV/" $NGINX_CONFIG
fi

# 여기도 충분히 트래픽 전환될 시간 주기 위해 잠시 지연
sleep 10

# 기존 컨테이너는 stop
sudo $DOCKER_COMMAND_HEAD stop $CURRENT_ENV
