#!/usr/bin/python3
#This script allows you to run a console command against a mobility master or the "MD" switches connected to it
#If the command does not return any output from the mobility master, it will query each fo the "MD" switches
#listed by the master, and provide the output from each.  No formatting is done to the output.

import requests
import urllib
import json
import urllib3
from re import search
#This supresses all HTTPS cert warnings.  Use with caution
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#These parameters can be hard coded as preferred to make it easier to use.
aruba_user=''
aruba_pass=''
aruba_hostname=''
#Nothing past this should need to be changed for normal use

if aruba_user == "":
    aruba_user = input("Enter username for aruba devices: ")
if aruba_pass == "":
    aruba_pass = input("Enter password for aruba devices: ")
if aruba_hostname == '':
    aruba_hostname = input("Enter ip or dns name for aruba mobility master: ")

command = input("Enter the command you would like to run: ")
command_parsed=urllib.parse.quote_plus(command)

base_url = "https://" + aruba_hostname + ":4343"

def aruba_login(hostname, username, password):
    login = requests.post( hostname + "/v1/api/login", data = {'username': aruba_user, 'password':aruba_pass}, verify=False)
    if "null" in login.headers['Set-Cookie']:
        print("Cookie empty")
        print("Login failed, check credentials")
        quit()
    else:
        return dict(SESSION=login.cookies['SESSION'])
    

def aruba_logout(hostname, logout_cookie):
    logout = requests.post( hostname + "/v1/api/logout", cookies=logout_cookie, verify=False)

send_cookies=aruba_login(base_url, aruba_user, aruba_pass)

#Get Attempt
url=base_url + '/v1/configuration/showcommand?command=' + command_parsed + '&UIDARUBA=' + send_cookies['SESSION']
# print('Attempting to get ' + url + ' from mobility master')
# print('Using cookie: ' + send_cookies['SESSION'] +'<---')   
#data = {'username': aruba_user, 'password':aruba_pass}, 
r = requests.get( url, cookies=send_cookies, verify=False)
print(r.headers)

if "Content-Length" in r.headers and r.headers["Content-Length"] == "0":
    print('No data returned from Master.  Would you like to try the command against the MD devices listed on the master via "show switches"?')
    result = input("y/n: ")
    if result == "n":
        aruba_logout(base_url, send_cookies)
        quit()
else:
    print(r.text)
    aruba_logout(base_url, send_cookies)
    quit()


#Get Controllers
url=base_url + '/v1/configuration/showcommand?command=show+switches+all&UIDARUBA=' + send_cookies['SESSION']
# print('Attempting to get ' + url + ' from mobility master')
# print('Using cookie: ' + send_cookies['SESSION'] +'<---')   
r = requests.get( url, cookies=send_cookies, verify=False)

switches = json.loads(r.text)
controllers = []
for i in switches["All Switches"]:
    if i["Type"] == "MD":
        controllers.append(i["IP Address"])
r.close()

for i in controllers:
    base_url = "https://" + i + ":4343"
    send_cookies=aruba_login(base_url, aruba_user, aruba_pass)
    url=base_url + '/v1/configuration/showcommand?command=' + command_parsed + '&UIDARUBA=' + send_cookies['SESSION']
    r = requests.get( url, cookies=send_cookies, verify=False)
    print("Output from: " + i)
    print(r.text)
    aruba_logout(base_url, send_cookies)

# url=base_url + '/v1/configuration/showcommand?command=show+ap+database+long&UIDARUBA=' + send_cookies['SESSION']
# print('Attempting to get ' + url + ' from mobility master')
# print('Using cookie: ' + send_cookies['SESSION'] +'<---')   
# r = requests.get( url, data = {'username': aruba_user, 'password':aruba_pass}, cookies=send_cookies, verify=False)

#print(r.text)

aruba_logout(base_url, send_cookies)
