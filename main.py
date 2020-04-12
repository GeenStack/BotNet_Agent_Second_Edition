import Bot




def main():
	bot = Bot.Bot()
	while True:
		sender, command = bot.wait_command()
		command = command.split(":")
		if command[0] == "echo":
			bot.echo(command[1], sender)
		if command[0] == "portscan":
			bot.portscan(command[1], sender)
		if command[0] == "nmap":
			bot.nmap(command[1], sender)


if __name__ == '__main__':
	main()