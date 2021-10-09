# pull official base image
FROM postgis/postgis:12-2.5-alpine

# run create.sql on init
ADD create.sql /docker-entrypoint-initdb.d/
