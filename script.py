import csv
import telnetlib
import time
import socket
import paramiko
import argparse


verbose = False
output_view = False

def arguments():
    ''' Function to define the script command line arguments '''
    global hosts_file, cmd_file, verbose, output_view, enpasswd

    parser = argparse.ArgumentParser(
        description="Network Configurator v.0.3")
    parser.add_argument('-d', '--hosts', help='Specify a host file', required=True)
    parser.add_argument('-c', '--commands', help='Specify a commands file', required=True)
    parser.add_argument('-v', '--verbose', nargs='?', default=False, help='Enables a verbose debugging mode')
    parser.add_argument('-o','--view output', nargs='?', default=False, help='Enables a verbose mode with ouput view')
    parser.add_argument('-p', '--enable password', help='Enter enable password', required=True)

    args = vars(parser.parse_args())

    if args['hosts']:
        hosts_file = args['hosts']
    if args['commands']:
        cmd_file = args['commands']
    if args ['enable password']:
        enpasswd = args['enable password']
    if args['verbose'] == None:
        verbose = True
    if args['view output'] == None:
       output_view = True


    return hosts_file, cmd_file, verbose, output_view,enpasswd

arguments()

serviceOption = int(input("Please choose administative service: \n1)SSHv2\n2)TELNET\nSERVICE: "))

HOST = str()
LOGIN = str()
PASSWORD = str()
ENABLE_PROMPT = str()
WITHOUT_ENABLE_PROMPT = str()


#Status bar (inactive now)
#def statusbar():
#    bar = progressbar.ProgressBar().start()
#    for i in xrange(100):
#       bar.update(i+1)
#      time.sleep(0.1)
#    bar.finish()

# This function reads CSV file with target network devices
def csv_read_devices(i,j):
    global csvdevices
    csvdevices = []
    with open (hosts_file) as Devices:
      device_reader = csv.reader(Devices,delimiter=";")
      for row in device_reader:
        csvdevices.append(row)
    credentials = csvdevices[i][j]
    return credentials

# This function reads CSV file with commands for target devices
def csv_read_commands(c,k):
    global csvcommands
    csvcommands = []
    with open (cmd_file) as Commands:
        commands_reader = csv.reader(Commands,delimiter=";")
        for row in commands_reader:
            csvcommands.append(row)
    commands = csvcommands[c][k]
    return commands

csv_read_commands(1, 1)
row_command = len(csvcommands)

def write_session_output(data):
    with open('outputfile.txt', 'a') as fileText:
        fileText.write(data + "\r\n <<<<<<<" + HOST + " сonnection output >>>>>>>\r\n")

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
    if ENABLE_PROMPT:
        telnet_session.read_until("enable\r\npassword:")
        telnet_session.write(enpasswd + "\n")
    elif WITHOUT_ENABLE_PROMPT:
         telnet_session.read_until("#")
         pass

    rg = xrange(row_command)
    for command in rg:
        SHELL = str((csv_read_commands(command,0)) + "\n")
        telnet_session.write(SHELL)
        print "-Executing command: %s" % csv_read_commands(command, 0)
        time.sleep(3)
        telnet_output = telnet_session.read_very_eager()
        if vverbose:
            print telnet_output
        write_session_output(telnet_output)


csv_read_devices(0, 0)
row_number = len(csvdevices)

# SSH client
def ssh_client():
    global ssh_session
    rg = xrange(row_command)
    ssh_session = paramiko.SSHClient()
    ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_session.connect(hostname=HOST, username=LOGIN, password=PASSWORD)
    ssh_shell = ssh_session.invoke_shell()
    time.sleep(1)
    ssh_enable = ssh_shell.recv(1024)
    if "#" not in ssh_enable:
        if verbose:
           print "****Entering to enable mode"

        ssh_shell.send("enable\n")
        time.sleep(1)
        ssh_enable = ssh_shell.recv(1024)

        if "enable\r\nPassword: " in ssh_enable:
            if output_view:
                print "****Typing superuser password"
            ssh_shell.send(enpasswd + "\n")
            ssh_enable = ssh_shell.recv(1024)
        time.sleep(3)


    if "#" in ssh_enable:
        if verbose:
            print "User already has superuser rights"
        ssh_shell.send("terminal length 0\n")

    else:
        ssh_shell.send("terminal length 0\n")

    for command in rg:
        SHELL = str((csv_read_commands(command,0)))
        ssh_shell.send(SHELL)
        time.sleep(3)
        print "-Executing command: %s" % csv_read_commands(command,0)
        ssh_output = ssh_shell.recv(10000)
        if output_view:
            print ssh_output
        ssh_shell.send("\n")
        time.sleep(3)
        write_session_output(ssh_output)




# Establish connection to network devices from CSV file
def session_to_NX(row_number,choosed_servise):
    global LOGIN
    global HOST
    global PASSWORD
    position = xrange(row_number)
    choosed_servise = serviceOption
    for number in position:
        HOST = str(csv_read_devices(number, 0))
        LOGIN = str(csv_read_devices(number, 1))
        PASSWORD = str(csv_read_devices(number, 2))
        print ("***Trying to configure host: " + HOST + " with login: " + "'" + LOGIN + "'" )
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
                print "Connection closed"
                pass

           except EOFError:
                print "System error"
                pass

           finally:
                print "Done. Check ouput file"
        else:
            print ("Error")


if  serviceOption == 1:
    print("***Configuring devices via SSH")
    session_to_NX(row_number, 1)
elif serviceOption == 2:
    print("***Configuring devices via Telnet")
    session_to_NX(row_number,2)
else:
    print ("Wrong number")