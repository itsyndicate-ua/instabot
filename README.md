# FastAPI Instagram Scheduler

This application is designed to schedule Instagram posts automatically at specified times. It utilizes FastAPI framework to handle HTTP requests, DynamoDB to store post data, and Amazon S3 to store media files associated with the posts.

## Prerequisites
* Python 3.x installed on your system.
* AWS account with DynamoDB and S3 set up.
* Instagram Developer Account to obtain API access.

## Installation
1. Clone this repository to your local machine.
2. Install the required Python packages using pip:
3. Copy code
4. pip install -r requirements.txt

## Configuration
AWS Credentials:                                                                                                                                                                             
Ensure that your AWS credentials are configured properly either through environment variables or AWS CLI configuration.                                                                                                
Instagram API:                                                                                                                                                                     
Obtain your Instagram API credentials (login, password).                                                                                                                                                               
Add these credentials to the configuration file (config.py)                                                                                                                                                            

## Usage
Start the FastAPI server:                                                                                                                                                        
python main.py
