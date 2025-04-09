FROM nginx:latest

COPY build/ /usr/share/nginx/html/

EXPOSE 8080

# Create a custom nginx configuration file
COPY custom-nginx.conf /etc/nginx/conf.d/custom-nginx.conf

RUN chown -R nginx:nginx /var/log/nginx
