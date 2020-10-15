# tcp_broadcast
A simple TCP broadcast server. 
It replicates a data from the one incoming connection to an others.

# Using  
-i : The port for a source connection  
-b : The port for clients  
-t : The protocol of input connection (There are two options tcp(default) or udp)

For example: ```python tcp_broadcast.py -i 200 -b 555``` - everything that will be received from tcp connection on 200 port will be broadcasted to all tcp clients, connected to 555 port

or           ```python tcp_broadcast.py -i 200 -t udp -b 555``` - everything that will be received from udp connection on 200 port will be broadcasted to all tcp clients, connected to 555 port
