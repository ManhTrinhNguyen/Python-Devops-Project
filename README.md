- [Website Mornitoring](#Website-Mornitoring)

    - [Create Server and run Nginx container](#Create-Server-and-run-Nginx-container)
 
    - [Website Request](#Website-Request)
 
    - [Email Notification](#Email-Notification)
 
    - [Hanlde Connection Error](#Hanlde-Connection-Error)
 
    - [Restart The Application](#Restart-The-Application)
 
    - [Schedule Monitor Task](#Schedule-Monitor-Task)

# Python-Devops-Project

## Website Mornitoring

#### Preparation Steps 

I will use Linode as a Cloud Server 

Once Server installed, I will create Docker and I will rung simple Nginx container on it 

Once I have Nginx Container up and running . I will write python program that checks the application  endpoint and check status of that applications

Bassically It just make an HTTP request to it and checks that we have a successful reply from the application and if the response from the application is not successful, either application has some problems or application isn't accessible at all, maybe server is down, maybe the container just crashed . If that happen my Python program will basically alert us or notify through email that website is down and we need to do something with it 

That mean I will configure Python program to send email to my email address 

As a next step, I will automate fixing the problem as well .

Once we get notified per email, we will then extend the Python Logic to restart the Docker container on the server or if the server is not accessible restart the server and then Docker container on it 

#### Create Server and run Nginx container 

Go to Linode -> Create Virtual Machine Linode -> Choose distribution Debian 11 -> Region -> 2 GB server -> rootpassword -> Create SSH key -> Create Server 

SSH to a Server : `ssh root@<ip-address>`

To install Docker, depend on the instruction that we are on we can follow the instruction in Docker Document 

To install Docker for Debian :(https://docs.docker.com/engine/install/debian/)

```
# Add Docker's official GPG key:
apt-get update
apt-get install ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
```

To install Docker : `apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin`

Start Nginx container : `docker run -d -p 8080:80 nginx`

To access it in the Server : `<public-ip>:80`


#### Website Request

I will try to access the Nignx endpoint in the Browser from the Python 

If I want to talk to other Application from Python I will use the library called `request`

```
import requests

# Access the application 
# This will give me an response

response = requests.get('http://50-116-2-196.ip.linodeusercontent.com:8080/')

print(response.status_code)

# I want to check if the Application accessible and it actually giving back status code 200 

if response.status_code == 200:
  print("Application is up and running successfully")
else: 
  print("Application downs. Fix it")
```

#### Email Notification 

Whenever the Status code is not 200 it mean the Application has some problem . It is giving a error message back or error Response 

In that case I need to be notify by our Python program that our application has problem, user cannot access it, so we need to do something about it 

To send email in Python, we have built-in module module for sending email and that is called `smtplib`. 

What I needs to send an email is a `sender` and `receiver` . Python program is basically need to be able to send email from certain email account

 - Example if we have certain Gmail account then Python need to access to the Gmail account and send an email on our behalf to some email address

 - I have Gmail account, I can allow Python to send email on my behalf from my account . Whenever I am allow Program to do something on my Personal account which has a required credentials I need to give Python those credentials as well

`smtplib.SMTP('')` is basically configure which email provider I want to use this work for everything 

 - In order to use STMP of Gmail I need to provide this value and Port : `smtplib.SMTP('smtp.gmail.com', 587)`. This will configure that I want to use an Gmail

 - `with smtplib.SMTP('smtp.gmail.com', 587) as smtp` This syntax wrap whatever come in annotation it belong to `with smtplib.SMTP('smtp.gmail.com', 587) as smtp`

 - Assining this `smtplib.SMTP('smtp.gmail.com', 587)` to a variable `smtp`

**with Statement**: What it does is  whenever we are using resource which is not in our control, so external resources maybe file that we are opening this basically a clean syntax for handling whatever issue may arrive with this external application . If we cannot connect our email, we can not login to it, If there is some problem with the SMTP Provider this will clean up all the resources for us in the background 

<img width="600" alt="Screenshot 2025-04-29 at 13 46 35" src="https://github.com/user-attachments/assets/baf4714e-f617-4e74-b413-2123743fe8bd" />


`smtp.starttls()`: When we working with a external application, generally security is a big issue so we need to be careful about secure . So starttls will basically encrypt the communication from python to our email server 

`smtp.ehlo()`: This identify our Python application with the mail Server and it encrypted communication or connection 

`smtp.login()`: Need username and password . Gmail allow two-factor authentication, more advance or more secure way to login to my account If I do not have a 2 ways authentication on Gmail I have to provide Gmail Password . However in that case I have to allow my Gmail account to accept call from application (Should use Gmail allow two-factor authentication)

 - Turn on 2-Step Verification for your Google account: (https://myaccount.google.com/security)

 - Go to: (https://myaccount.google.com/apppasswords)

 - Select "Mail" and the device you're using (e.g., Windows).

 - Google will give you a 16-digit App Password. Something like this `abdf fbft qwer qiny`

 - Use this in your script like: `smtp.login("your_email@gmail.com", "your_app_password")`

Not Secure if we put Username and Password direct in the code . Instead use ENV . 

 - To access  ENV in Python use built-in module called : `os`

 - To get ENV : `os.environ.get('')`

 - To set ENV so Python can read them:

     - In my Mac I can edit my `zshrc` by using `vim ~/.zshrc` then I will add `export USER_NAME=<my-username>` and `export PASSWORD_EMAIL=<my-password>` then I will restart my mac so it will actually run
  
     - Another way is install `pip install python-dotenv` . This one is for local development . Then I will create `.env` file and put my username and password in there
  
         - To use it :
      
           ```
           import os
           from dotenv import load_dotenv
        
           load_dotenv()  # load from .env file
           ``` 

 - All Caps Variables is a standard naming rule for variables that do not change their value so they are only assigned the value once at the beginning and the program doesn't change its value these kind of variables called `constant`

`smtp.sendmail(<sender>, <recevier>, <message>)` sendmail function has 3 parameters

My whole code look like this :

```
import requests
import smtplib
import os

# Access the application 
# This will give me an response

# "nguyenmanhtrinh17041998@gmail.com", "difizfotkyhbqiny"

EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

try:
  response = requests.get('http://50-116-2-196.ip.linodeusercontent.com:8080/')

  # I want to check if the Application accessible and it actually giving back status code 200 

  if response.status_code == 200:
    print("Application is up and running successfully")
  else: 
    print("Application downs. Fix it")
    
    # Send email to me 
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
      smtp.starttls()
      smtp.ehlo()
      smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
      msg = f"Subject: SITE DOWN\n Application return {response.status_code}. Fix the issue! Restart the Application"
      smtp.sendmail(EMAIL_USERNAME, EMAIL_USERNAME, msg)
```

#### Hanlde Connection Error 

Above I just checking the response code . What if the server doesn't return reponse . 

If this `response = requests.get('http://50-116-2-196.ip.linodeusercontent.com:8080/')` doesn't response I would need an email as well . 

I will use `try except` to handle this situation  

`try-except`should be use to handle exception or any error might happen that we cannot handle with If else . 

For example : If I stop the nginx container then run python I will get an connection error . But also none of the code after execute 

The whole code will look like this 

```
import requests
import smtplib
import os

# Access the application 
# This will give me an response

# "nguyenmanhtrinh17041998@gmail.com", "difizfotkyhbqiny"

EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

try:
  response = requests.get('http://50-116-2-196.ip.linodeusercontent.com:8080/')

  # I want to check if the Application accessible and it actually giving back status code 200 

  if response.status_code == 200:
    print("Application is up and running successfully")
  else: 
    print("Application downs. Fix it")
    
    # Send email to me 
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
      smtp.starttls()
      smtp.ehlo()
      smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
      msg = f"Subject: SITE DOWN\n Application return {response.status_code}. Fix the issue! Restart the Application"
      smtp.sendmail(EMAIL_USERNAME, EMAIL_USERNAME, msg)
except Exception as ex:
  print('Connection error happen')
  print (ex)
  # Send email to me 
  with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.starttls()
    smtp.ehlo()
    smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    msg = f"Subject: SITE DOWN\n Application not accessible at all !!!"
    smtp.sendmail(EMAIL_USERNAME, EMAIL_USERNAME, msg)
```

Instead of repeating the code in multiple places . It will put the logic in the function then I can call it multiple time 

```
import requests
import smtplib
import os

# Access the application 
# This will give me an response

# "nguyenmanhtrinh17041998@gmail.com", "difizfotkyhbqiny"

EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

def send_notifications(msg):
  with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
      smtp.starttls()
      smtp.ehlo()
      smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
      smtp.sendmail(EMAIL_USERNAME, EMAIL_USERNAME, msg)

try:
  response = requests.get('http://50-116-2-196.ip.linodeusercontent.com:8080/')

  # I want to check if the Application accessible and it actually giving back status code 200 

  if response.status_code == 200:
    print("Application is up and running successfully")
  else: 
    print("Application downs. Fix it")
    
    # Send email to me 
    msg = f"Subject: SITE DOWN\n Application return {response.status_code}. Fix the issue! Restart the Application"
    send_notifications(msg)
except Exception as ex:
  print('Connection error happen')
  print (ex)
  # Send email to me 
  msg = f"Subject: SITE DOWN\n Application not accessible at all !!!"
  send_notifications(msg)
```

#### Restart The Application

Next step I also want to repair also using Python 

When the application returning non-successful status code, just restarting the application may help bcs maybe something just got messed up in the application, so we just need to start it new, maybe that will fix the issue   

To restart Application I need to connect to a Server using SSH from my Python Program and then execute basically just Docker start command from there  

Gerenally this logic for connecting to a remote server using SSH can be very helpful knowledge to have when I am writing Python applications, bcs it could be that in many case I need to do some maintainence task or maybe some automation task on server directly, so knowing how to connect to the remote server and execute command there will very valuable 

To do that I use library call `paramiko` that allow me to `ssh` connection . 

 - `ssh = paramiko.SSHClient()` give me ssh client

 - ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) : Automatically allow connection without have to type Yes manually

 - `ssh.connect(<ip-address-of-remote-server>, <ssh-port>, <username>, <private_key_location>)` I need couple parameters to connect. The code should look like this `ssh.connect(hostname='164.92.126.100', username='root', key_filename='/Users/trinhnguyen/.ssh/id_rsa')` . I don't need to provide PORT bcs it will provide by default

 - `ssh.exec_command('docker ps')` to execute Linux command .

     - If I want to see output of execute command `stdin, stdout, sdterr = ssh.exec_command('docker ps')`  . I actually get 3 outputs or 3 values back from the execute command that is : `stdin`, `stdout, stderr`
  
     - `stdin` is what I typed in the terminal
  
     - `stdout` is what I get from the Terrminal
  
     - `stderr` is when I execute command it give me error
  
 - When I don't have any other command to execute I need to close th ssh connection : `ssh.close()`

 - To restart Application : `stdin, stdout, stderr = ssh.exec_command("docker start <container-id>")`

I also want to restart a Server bcs the Server itself might also be a problem 

 - First I need Python Linode Client to connect to Linode account then reboot Linode Server . Install `pip install linode-api4`

 - Any external Application I want to connect I alway need some kind of Authentication . So I need a API Token to connect to Linode .

 - API Token are token that I can create myself to give program like Python access to my Linode account

 - Once I have the Token I will set it as a ENV then I will get a token like this : `LINODE_TOKEN = os.environ.get('LINODE_TOKEN')` . Then I can use that Token to connect to Linode like this :`client = linode_api4.LinodeClient(LINODE_TOKEN)`

 - `nginx_server = client.load(linode_api4.Instance, <linode-id>)` can be use to Connect to Linode server .

     - `linode_api4.Instance` connect to Linode Instance
  
     - `<linode-id>`: Connect to specific Linode
  
 - To reboot server : `nginx_server.reboot()`

 - Reboot will take sometime to reboot . So I want to wait before restart the Application . The logic is I will write a while loop until the status become `running` I will break a loop and restart the Application


#### Schedule Monitor Task 

```
import requests
import smtplib
import os
import paramiko
import linode_api4
import time
import schedule

# Access the application 
# This will give me an response

EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
LINODE_TOKEN = os.environ.get('LINODE_TOKEN')

def send_notifications(msg):
  with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
      smtp.starttls()
      smtp.ehlo()
      smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
      smtp.sendmail(EMAIL_USERNAME, EMAIL_USERNAME, msg)


def monitor_application():
  try:
    response = requests.get('http://50-116-12-203.ip.linodeusercontent.com:8080/')

    # I want to check if the Application accessible and it actually giving back status code 200 

    if response.status_code == 200:
      print("Application is up and running successfully")
    else: 
      print("Application downs. Fix it")
      
      # Send email to me 
      msg = f"Subject: SITE DOWN\n Application return {response.status_code}. Fix the issue! Restart the Application"
      send_notifications(msg)

      # Restart Application
      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

      # Load private key
      private_key = paramiko.RSAKey.from_private_key_file('/Users/trinhnguyen/.ssh/id_rsa')       

      # connect
      ssh.connect(hostname="50.116.12.203", username="root", pkey=private_key)

      # Execute a command
      stdin, stdout, stderr = ssh.exec_command("docker ps")
      print(stdout.readlines())
      ssh.close()
      print('Application restart')

  except Exception as ex:
    print('Connection error happen')
    print (ex)
    # Send email to me 
    msg = f"Subject: SITE DOWN\n Application not accessible at all !!!"
    send_notifications(msg)

    # Start Linode Server
    client = linode_api4.LinodeClient(LINODE_TOKEN)
    nginx_server = client.load(linode_api4.Instance, 421847)
    nginx_server.reboot()

    # Wait for the Server reboot

    while True:
      nginx_server = client.load(linode_api4.Instance, 421847)
      if nginx_server.status == 'running':
        time.sleep(5)
        # Restart Application
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load private key
        private_key = paramiko.RSAKey.from_private_key_file('/Users/trinhnguyen/.ssh/id_rsa')       

        # connect
        ssh.connect(hostname="50.116.12.203", username="root", pkey=private_key)

        # Execute a command
        stdin, stdout, stderr = ssh.exec_command("docker ps")
        print(stdout.readlines())
        ssh.close()
        print('Application restart')

        break

schedule.every(5).minutes.do(monitor_application)

while True:
  schedule.run_pending()
```
