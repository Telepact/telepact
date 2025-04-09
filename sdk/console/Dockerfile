FROM httpd:2.4

COPY build/ /usr/local/apache2/htdocs/

EXPOSE 8080

RUN sed -i 's/Listen 80/Listen 8080/' /usr/local/apache2/conf/httpd.conf

USER nobody
