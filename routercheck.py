import re, platform, os, sys
from datetime import datetime
from urllib.request import urlopen as url
try:
    import paramiko
except ModuleNotFoundError:  # Paramiko not installed by default
    print("INSTALL MISSING MODULE")
    try:
        url("https://pypi.org/")
    except:
        print("The Internet is required to install missing module")
        sys.exit(0)
    from pip._internal import main as pip
    pip(['install', 'paramiko'])
    import paramiko
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# SERVER ACCESS
HOST = '' # IP or domain
USER = '' # Username
PSWD = '' # Password
PATH = '' # Directory with backups
  
FAIL = '\033[91m'  # Colors for terminal
ENDC = '\033[0m'

client = paramiko.SSHClient()  # SSH connection
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=HOST, username=USER, password=PSWD)
sftp = client.open_sftp()
print('Connected')
lastbackups = []
print('Geting the current backups')
for ip in sftp.listdir(PATH):
    max = -9999999999  # Will compare the sequence numbers or timestamps
    filePath = ''
    number = True
    for archive in sftp.listdir(PATH + '/' + ip):
        if re.fullmatch("\d+[\.]\d+-\d+", archive):  # If format "IP-number"
            if int(archive.split('-')[1]) > max and number:
                max = int(archive.split('-')[1])
                filePath = PATH + '/' + ip + '/' + archive
        else:  # If format "IP-date"
            if number:
                max = -9999999999
                number = False
            date = archive.replace(ip, '').split('-')[:-1]  # Clear filename from ip and milliseconds 
            for i in range(len(date) - 2):
                if date[i] == "":
                    date.pop(i)  # If filename has 2 dashes - clear it
                if re.fullmatch("[\.]\D{3}", date[i]):  
                    date[i] = date[i].replace('.', '')  #  If there is a dot before the month - clear it
            dateString = ''.join('-'.join(date).split('.')[0])  # Collect a standardized string
            try:
                dateObject = datetime.strptime(dateString, '%b-%d-%H-%M-%S').timestamp()
            except ValueError:  # If the seconds are more than 60 - set 00. Btw it doesn't matter
                dateParse = dateString.split('-')
                dateParse[-1] = "00"
                dateObject = datetime.strptime('-'.join(dateParse), '%b-%d-%H-%M-%S').timestamp()
            if dateObject > max:
                max = dateObject
                filePath = PATH + '/' + ip + '/' + archive
    if filePath != '' and filePath not in lastbackups:  # Avoid repeats
        lastbackups.append([ip, filePath])
while True:
    register = False
    try:
        SRCH = input('\nSearch request: ')
    except KeyboardInterrupt:
        print()
        sys.exit(0)
    if re.fullmatch('".+"', SRCH):
        register = True
    for backup in lastbackups:
        with sftp.open(backup[1]) as file:
            hostname = ''
            lineNum = 0
            found = False
            for line in file:
                lineNum += 1
                if 'hostname' in line and not found:  # Search for hostname or request
                    hostname = line.replace('hostname ', '').replace('\n', '')
                    found = True
                if register:
                    if SRCH in line:
                        if found:
                            print(backup[0], hostname, 'Ln:' + str(lineNum), backup[1])
                        else:
                            print(backup[0], FAIL +  'Hostname_not_found' + ENDC, 'Ln:' + str(lineNum), backup[1])
                else:
                    if SRCH.lower() in line.lower():
                        if found:
                            print(backup[0], hostname, 'Ln:' + str(lineNum), backup[1])
                        else:
                            print(backup[0], FAIL +  'Hostname_not_found' + ENDC, 'Ln:' + str(lineNum), backup[1])