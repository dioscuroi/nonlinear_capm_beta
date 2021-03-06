#!/bin/bash

echo ""
echo ""
echo "**************************************************"
echo " Build and push docker container "
echo "**************************************************"

docker build -t awsbatch/beta_estimation .

# Register the container to AWS ECR repository from the AWS Management Console

# Get authorized using the AWS command line tool
eval $(aws ecr get-login --region us-east-2 --no-include-email)

docker tag awsbatch/beta_estimation:latest 026533969070.dkr.ecr.us-east-2.amazonaws.com/awsbatch/beta_estimation:latest

echo ""
echo "* Pushing the container to AWS"

docker push 026533969070.dkr.ecr.us-east-2.amazonaws.com/awsbatch/beta_estimation:latest

echo ""
echo "* Deleting dangling Docker images"

docker rmi $(docker images -f "dangling=true" -q)

