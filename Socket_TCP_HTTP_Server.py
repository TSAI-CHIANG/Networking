import socket # import the socket library provided by Python
import threading # threading is a python library that can spawn multiple threads in a single app (process)


# Server details
SERVER_IP = '127.0.0.1'
SERVER_PORT = 8888 #open port 8888
SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)  

# HTML and CSS content
GOOD_HTML_CONTENT = "<html><head><link href='style.css' rel='stylesheet' type='text/css'></head><body>My student ID: 112356012</body></html>"
CSS_CONTENT = "Body {color: red;}"
NOTFOUND_HTML_CONTENT = "<html><head></head><body><h1>Oops... 404 Not found<h1></body></html>" #404 not found msg


#建立response dict：包含headers, status, content type等
response_dict = {
    '/good.html': {
        "status": "HTTP/1.1 200 OK", #/good.html response status須為：200 OK
        'content': GOOD_HTML_CONTENT, 
        'headers': {
            "Content-Type": "text/html",
            "Content-Length": str(len(GOOD_HTML_CONTENT)), #GOOD_HTML_CONTENT變數的長度
        }
    },
    '/style.css': {
        "status": "HTTP/1.1 200 OK",  #/style.css response status須為：200 OK
        'content': CSS_CONTENT,
        'headers': {
            "Content-Type": "text/css",
            "Content-Length": str(len(CSS_CONTENT)),
        }
    },
    '/redirect.html': { 
        "status": "HTTP/1.1 301 Moved Permanently", #/redirect.html response status須為： 301 Moved Permanently
        'content': "",
        'headers': {
            "Location": "/good.html", #The redirected page is good.html.
        }
    },
    'default': {   #define the response of 'notfound.html' or other domain name that not defined in this assignment
        "status": "HTTP/1.1 404 Not Found", #notfound.html 的response status:404
        'content': NOTFOUND_HTML_CONTENT,
        'headers': {
            "Content-Type": "text/html",
            "Content-Length": str(len(NOTFOUND_HTML_CONTENT)), 
        }
    }
}

def serveClient(clientsocket, address):
    '''
    #This function will be called after 'accept'
    # a new thread is created for every new accepted client
    # every new thread starts from the function below
    '''
    print(f"[NEW CONNECTION] {address} created") #just wanna know the status of connection
    request_count = 0 #count the object number in a connection 

    try:     
        # we need a loop to continuously receive messages from the client
        while request_count < 2: #if the object number in a connection >=2, leave the while loop
            data = clientsocket.recv(1024).decode() #byte to string 
            # then receive at most 1024 bytes message and store these bytes in a variable named 'data'
            # you can set the buffer size to any value you like
            
            if not data: 
                break
            print(data) #print("from client", data)
            filename = data.split('\n')[0].split()[1] #split the data to find what kind of request(e.g. /good.html...)
            response_data = response_dict.get(filename, response_dict["default"]) 
            status = response_data['status']
            content = response_data['content']
            headers = response_data['headers']
            
            # Increment the request count and prepare the connection header
            request_count += 1 #track object amount
            headers["Connection"] = "close" if request_count == 2 else "keep-alive"  #if it's 2nd object, close the connection, else make connection keep alive
            headers_str = "\r\n".join([f"{key}: {val}" for key, val in headers.items()]) #add \r\n
            """
            e.g.
            headers = {
                "Content-Type": "text/html",
                "Content-Length": 6, 
            }
            -> ["Content-Type: text/html", "Content-Length: 6"]
            headers_str = "Content-Type: text/html\r\nContent-Length: 6"
            """
            # Prepare and send the response # if the received data is not empty, then we send something back by using send() function
            response = f"{status}\r\n{headers_str}\r\n\r\n{content}"   #add \r\n
            clientsocket.send(response.encode()) #encode():string to bytes
            print(f"[RESPONSE SENT TO {address} {request_count}]") #just wanna know the status
            
    finally: #try-finally         
        
        # we need some condition to terminate the socket:
        clientsocket.close() #close the connection if leave the while loop above 
        print(f"[CLOSE CONNECTION {address}]")


# create socket instance
# socket.AF_INET is a constant value that indicates I want to use IP (Internet Protocol) as my L3 protocol
# socket.SOCK_STREAM is a constant value that indicates I want to use TCP as my L4 protocol
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #with: context manager
    s.bind(SERVER_ADDRESS)  
    # ask the OS to bind the created socket to user-specified parameters: (IP, TCP port)
    # the 1st parameter is the binded IP, the 2nd parameter is the binded port number
    # So that when the OS receives a datagram, the OS knows how to demux the datagram to the corresponding application 
    s.listen() 
    #server start listening 
    # # it makes this python program waiting for receiving message
    # listen() function has one parameter that limits how many clients can be connected to this server
    print(f"[LISTENING] Server is listening on {SERVER_ADDRESS}") #just wanna know the status
    
    while True:     # we need a loop to continuously receive messages from the client
        # we need a way to distinguish clients
        # TCP use 4-tuple (src IP, dst IP, src port, dst port) to distinguish a socket
        # we use accept() function to confirm that we connect to the client socket
        # and accept() function will return the client's socket instance and IP
        # we need a loop to keep accepting new clients 
        (clientsocket, address) = s.accept()

         # create a new thread to serve this new client
         # after the thread is created, it will start to execute 'target' function with arguments 'args'
        threading.Thread(target=serveClient, args=(clientsocket, address)).start() #multi-thread
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}") #just wanna know the threading status