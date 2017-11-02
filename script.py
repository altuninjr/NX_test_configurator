import csv
import telnetlib
import time
import socket
import progressbar
import paramiko



x = input("Please choose terminal service: \n1)SSH\n2)TELNET\nSERVICE: ")



# Status bar
# def statusbar():
#     bar = progressbar.ProgressBar().start()
#     for i in xrange(100):
#        bar.update(i+1)
#        time.sleep(0.1)
#     bar.finish()
# statusbar()


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

csv_read_commands(0, 0)
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
    time.sleep(10)
    telnet_session.write(b"?\n")
    time.sleep(5)
    x = xrange(row_command)
    for command in x:
        SHELL = str((csv_read_commands(command,0)) + "\n")
        telnet_session.write(SHELL)
    time.sleep(5)

    print (telnet_session.read_very_eager())


# def ssh_client():



csv_read_devices(0, 0)
row_number = len(csvdevices)

# Establish connection to network devices from CSV file
def telnet_to_NX(row_number):
    global LOGIN
    global HOST
    global PASSWORD
    x = xrange(row_number)
    for number in x:
        HOST = str(csv_read_devices(number, 0))
        LOGIN = str(csv_read_devices(number, 1))
        PASSWORD = str(csv_read_devices(number, 2))
        print ("Trying to configure host: " + HOST + " with login: " + "'" + LOGIN + "'" )


        try:
            return telnet_client()
            AUF = telnet_session.read_until("\r\nAuthentication failed!\r\n\r\n")

        except AUF:
            print ("Wrong username or password for " + HOST)
            pass


        except socket.error:
            print "Connection timeout"
            pass

        except EOFError:
            print "System error"
            pass


        finally:
            print "Host is unreachable"



if   x == 1:
    print("SSH Client")
elif x == 2:
    telnet_to_NX(row_number)
    print("Telnet Client")
else:
    print ("Wrong number")


# telnet_to_NX(row_number)


# def ssh_to_NX():