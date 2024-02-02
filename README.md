# CSE310-Pinger
A python script that pings the target URL<br>
<br>
<details><summary>Usage: </summary>
Run the program in the terminal using: py\PATH\pinger.py *URL HERE* <br>
Example: py\PATH\pinger.py www.google.com<br>
or run in an IDE like PyCharm using "First ran the program using sys.argv.append("*URL*")"<br>
</details>
<br>
<details> <summary>Details:</summary>
-Added a list to hold all of the pings.<br>
-Edits to the Ping method:<br>
	-Created a variable for the average ping<br>
	-If the length of the list is > 0, a for loop goes through all of the pring variables and updates the avg<br>
	-Added to the try/except for keyboard interruption:<br>
		If the user terminates the program, it'll print min/avg/max ping.<br>
<br>
-Edits to the receiveOnePing method:<br>
	-Fetch the ICMP header and the size of the packet.<br>
	-Calulate the RTT and places it in the list of pings.<br>
	-Print out the size, address, and RTT of the packet.<br>
<br>
Edits in doOnePing method:<br>
	-Create mySocket using SOCK_RAW<br>
</details>
