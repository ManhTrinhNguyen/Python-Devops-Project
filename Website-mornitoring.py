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
