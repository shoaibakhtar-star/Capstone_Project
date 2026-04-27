# FastAPI
docker build -t fastapi-repo:latest ./backend/python-fastapi
docker tag fastapi-repo:latest 639914974908.dkr.ecr.ap-south-1.amazonaws.com/fastapi-repo:latest
docker push 639914974908.dkr.ecr.ap-south-1.amazonaws.com/fastapi-repo:latest

# Django
docker build -t django-repo:latest ./backend/python-django
docker tag django-repo:latest 639914974908.dkr.ecr.ap-south-1.amazonaws.com/django-repo:latest
docker push 639914974908.dkr.ecr.ap-south-1.amazonaws.com/django-repo:latest

# Node.js
docker build -t node-repo:latest ./backend/backend-node
docker tag node-repo:latest 639914974908.dkr.ecr.ap-south-1.amazonaws.com/node-repo:latest
docker push 639914974908.dkr.ecr.ap-south-1.amazonaws.com/node-repo:latest

# .NET
docker build -t dotnet-repo:latest ./backend/backend-dotnet
docker tag dotnet-repo:latest 639914974908.dkr.ecr.ap-south-1.amazonaws.com/dotnet-repo:latest
docker push 639914974908.dkr.ecr.ap-south-1.amazonaws.com/dotnet-repo:latest
