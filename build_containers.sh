#!/bin/bash

echo ""
echo ""
echo "**************************************************"
echo " Build and push docker container "
echo "**************************************************"

docker build -t awsbatch/beta_estimation .

# Register the container to AWS ECR repository from the AWS Management Console

# Get authorized using the AWS command line tool
#aws ecr get-login --region us-east-1

echo ""
docker tag awsbatch/beta_estimation:latest 026533969070.dkr.ecr.us-east-1.amazonaws.com/awsbatch/beta_estimation:latest

docker push 026533969070.dkr.ecr.us-east-1.amazonaws.com/awsbatch/beta_estimation:latest


