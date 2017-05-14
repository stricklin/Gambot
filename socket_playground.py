import socket
HOST = "imcs.svcs.cs.pdx.edu"
PORT = 3589
#username = input("username: ")
#password = input("password: ")
username = "human"
password = "leftfoot"

# connect socket and set up reader/writer with sockfile
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
sockfile = s.makefile(mode="rw", newline="\r\n")
welcome = sockfile.read_line().strip("\r\n")

# check to make sure the socket is connected and the server is the right version
if welcome != "100 imcs 2.5":
    print("wrong version of server")
    exit()
# login
sockfile.write("me " + username + " " + password + "\r\n")
sockfile.close()

sockfile = s.makefile(mode="rw", newline="\r\n")
message = sockfile.read_line().strip("\r\n")

print(message)
sockfile.close()
s.close()

