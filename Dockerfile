FROM alpine:edge

EXPOSE 8081

RUN apk update && \
    apk add --no-cache --update \
        supervisor \
        uwsgi-python3 \
        python3 \
        nginx \
        git \
        curl \
        tzdata && \
     rm -rfv /var/cache/apk/*

ENV TZ=Europe/Stockholm

COPY . /app

# COPY nginx.conf /etc/nginx/nginx.conf

RUN date +"%Y-%m-%dT%H:%M:%S %Z" && \
    mkdir -p /var/run/nginx && \
    chmod -R 777 /var/run/nginx && \ 
    mkdir -p /var/run/supervisord /var/log/supervisord && \
    chmod -R 777 /var/run/supervisord && \
    chmod -R 775 /app && \
    chmod -R 777 /usr/sbin && \
    chmod -R 775 /usr/lib/python* && \
    chmod -R 775 /var/lib/nginx && \
    mkdir -p /var/lib/nginx/tmp/client_body /var/lib/nginx/tmp/proxy /var/lib/nginx/tmp/fastcgi /var/lib/nginx/tmp/uwsgi /var/lib/nginx/tmp/scgi && \
    chmod -R 775 /var/lib/nginx/tmp/* && \
    chmod -R 777 /var/log/* && \
    mkdir -p /var/tmp/nginx && \
    chmod -R 777 /var/tmp/nginx


WORKDIR /app

RUN  time pip3 install -r requirements.txt
# RUN find tests -type d -name __pycache__ -prune -exec rm -rf -vf {} \; && \
#     python3 -m pytest -svv -m unit tests/ && \
#     find tests -type d -name __pycache__ -prune -exec rm -rf -vf {} \;


USER 10000
CMD ["/usr/bin/supervisord", "-n", "-c", "/app/supervisord.conf"]
