Setting Up SQS on Docker 

docker pull localstack/localstack

docker run -d -p 4566:4566 -p 4510-4559:4510-4559 localstack/localstack

docker ps


Make Sure Docker and this is running before turning on the Microservices