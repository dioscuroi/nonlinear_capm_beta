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
#aws ecr get-login --region us-west-2

docker tag awsbatch/beta_estimation:latest 026533969070.dkr.ecr.us-west-2.amazonaws.com/awsbatch/beta_estimation:latest

echo ""
echo "Pushing the container to AWS"

docker push 026533969070.dkr.ecr.us-west-2.amazonaws.com/awsbatch/beta_estimation:latest


