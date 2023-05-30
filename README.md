# build-ease - deploy-ready django project on docker

### How to use:

#### Clone the repo:

    git clone https://github.com/Olim2508/build-ease.git

#### Run the local develop server:

    docker-compose up -d --build
    docker-compose logs -f

##### Server will bind 8008 port. You can get access to server by browser [http://localhost:8008](http://localhost:8008)

### Configuration for local prod:
    docker-compose -f docker-compose.prod.yml up -d --build
##### Server will bind 1337 port. You can get access to server by browser [http://localhost:1337](http://localhost:1337)

### Configuration for staging on virtual server for checking ssl certificate:
    docker-compose -f docker-compose.staging.yml up -d --build
#### Don't forget to change:
#### - DJANGO_ALLOWED_HOSTS, VIRTUAL_HOST, LETSENCRYPT_HOST to your actual domain docker/prod/env/.staging.env file
#### - DEFAULT_EMAIL on docker/prod/env/.staging.proxy-companion.env to your email
#### - Database credentials on docker/prod/env/.db.staging.env and docker/prod/env/.staging.env (they should match)

### Configuration for production stage on virtual server
    docker-compose -f prod.yml up -d --build
#### Don't forget to change:
#### - DJANGO_ALLOWED_HOSTS, VIRTUAL_HOST, LETSENCRYPT_HOST to your actual domain docker/prod/env/.prod.env file
#### - DEFAULT_EMAIL on docker/prod/env/.prod.proxy-companion.env to your email
#### - Database credentials on docker/prod/env/.db.prod.env and docker/prod/env/.prod.env (they should match)
