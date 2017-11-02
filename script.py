import csv
import telnetlib
import time
import socket
#import progressbar
import paramiko



x = input("Please choose administative service: \n1)SSH\n2)TELNET\nSERVICE: ")
HOST = str()
LOGIN = str()
PASSWORD = str()
ENABLE_PASSWORD = str()
ENABLE_WTHPASSWORD = str()

#Status bar (inactive now)
#def statusbar():
#    bar = progressbar.ProgressBar().start()
#    for i in xrange(100):
#       bar.update(i+1)
#      time.sleep(0.1)
#    bar.finish()

# This function read CSV file with target network devices
def csv_read_devices(i,j):
    global csvdevices
    csvdevices = []
    with open ('nxlist.csv') as Devices:
      device_reader = csv.reader(Devices,delimiter=";")
      for row in device_reader:
        csvdevices.append(row)
    credentials = csvdevices[i][j]
    return credentials

# This function read CSV file with commands for target devices
def csv_read_commands(c,k):
    global csvcommands
    csvcommands = []
    with open ('commandlist.csv') as Commands:
        commands_reader = csv.reader(Commands,delimiter=";")
        for row in commands_reader:
            csvcommands.append(row)
    commands = csvcommands[c][k]
    return commands

csv_read_commands(1, 1)
row_command = len(csvcommands)

# Telnet client
def telnet_client():
    global telnet_session
    telnet_session = telnetlib.Telnet(HOST)
    telnet_session.read_until("Username: ")
    telnet_session.write(LOGIN + "\n")
    if PASSWORD:
         telnet_session.read_until("Password: ")
         telnet_session.write(PASSWORD + "\n")

    telnet_session.read_until(">")
    telnet_session.write("enable\n")
    if ENABLE_PASSWORD:
        telnet_session.read_until("enable\r\npassword:")
        telnet_session.write("redfox\n")
    elif ENABLE_WTHPASSWORD:
         telnet_session.read_until("#")
         pass

    rg = xrange(row_command)
    for command in rg:
        SHELL = str((csv_read_commands(command,0)) + "\n")
        telnet_session.write(SHELL)
        time.sleep(3)
        print telnet_session.read_very_eager()



csv_read_devices(0, 0)
row_number = len(csvdevices)

# SSH client
def ssh_client():
    global ssh_session
    ssh_session = paramiko.SSHClient()
    ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_session.connect(hostname=HOST, username=LOGIN, password=PASSWORD)
    stdin, stdout, stderr = ssh_session.exec_command()
    error = stderr.read() + stdout.read
    print error


# Establish connection to network devices from CSV file
def session_to_NX(row_number,choosed_servise):
    global LOGIN
    global HOST
    global PASSWORD
    position = xrange(row_number)
    choosed_servise = x
    for number in position:
        HOST = str(csv_read_devices(number, 0))
        LOGIN = str(csv_read_devices(number, 1))
        PASSWORD = str(csv_read_devices(number, 2))
        print ("Trying to configure host: " + HOST + " with login: " + "'" + LOGIN + "'" )
        # statusbar()
        if choosed_servise == 1:
           try:
               ssh_client()
               print("SSH OK")
           except socket.error:
               print "Connection timeout"
           except EOFError:
               print "System error"

        elif choosed_servise == 2:
           try:
             return telnet_client()

           except socket.error:
                print "Connection timeout"
                pass

           except EOFError:
                print "System error"
                pass

           finally:
                print "Host is unreachable"
        else:
            print ("Error")



if   x == 1:
    print("SSH Client")
    session_to_NX(row_number, 1)
elif x == 2:
    print("Telnet Client")
    session_to_NX(row_number,2)
else:
    print ("Wrong number")


# telnet_to_NX(row_number)


# def ssh_to_NX():
