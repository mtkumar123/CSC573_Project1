import socket
import threading
import os
import re
import random
import platform
import datetime


def format_add_message(rfc_number, rfc_title, clientHostName, upload_port):
    message = "ADD RFC " + rfc_number + " P2P-CI/1.0" + "\n" \
              + "HOST: " + clientHostName + "\n" \
              + "PORT: " + str(upload_port) + "\n" \
              + "TITLE: " + rfc_title
    return message


def format_list_message(clientHostName, upload_port):
    message = "LIST ALL P2P-CI/1.0\n" \
              + "HOST: " + clientHostName + "\n" \
              + "PORT: " + str(upload_port)
    return message


def format_lookup_message(rfc_number, rfc_title, clientHostName, upload_port):
    message = "LOOKUP RFC " + rfc_number + " P2P-CI/1.0" + "\n" \
              + "HOST: " + clientHostName + "\n" \
              + "PORT: " + str(upload_port) + "\n" \
              + "TITLE: " + rfc_title
    return message


def format_get_message(rfc_number, peer_host):
    message = "GET RFC " + rfc_number + " P2P-CI/1.0\n" \
              + "HOST: " + peer_host + "\n" \
              + "OS: " + platform.system() + " " + platform.release()
    return message


def format_send_message_peer(rfc_number):
    file_data = read_local_rfc(str(rfc_number))
    message = "P2P-CI/1.0 "
    if file_data:
        message += "200 OK\n"
        message += "DATE: " + str(datetime.datetime.today()) + " " + datetime.datetime.now(
            datetime.timezone.utc).astimezone().tzname() + "\n"
        message += "OS: " + platform.system() + " " + platform.release() + "\n"
        message += "LAST-MODIFIED: " + str(
            os.path.getmtime("./{}.txt".format(str(rfc_number)))) + datetime.datetime.fromtimestamp(
            os.path.getmtime("./{}.txt".format(str(rfc_number)))).astimezone().tzname() + "\n"
        message += "CONTENT-LENGTH: " + str(len(file_data.encode())) + "\n"
        message += "CONTENT-TYPE: text/text\n"
        message += file_data
        return message
    else:
        message = "P2P-CI/1.0 "
        message += "404 Not Found\n"
        message += "DATE: " + str(datetime.datetime.today()) + " " + datetime.datetime.now(
            datetime.timezone.utc).astimezone().tzname() + "\n"
        message += "OS: " + platform.system() + " " + platform.release() + "\n"
        return message


def get_file(peer_host, peer_port, get_message):
    clientDownloadSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientDownloadSocket.connect((peer_host, peer_port))
    clientDownloadSocket.sendall(get_message.encode())
    raw_response = clientDownloadSocket.recv(1024)
    response = raw_response.decode()
    # Find out the length of the data being sent first, and then call receive again
    response_lines = response.split("\n")
    if re.search(r"200 OK", response_lines[0]):
        # Content length is on line 4
        data_length = int(re.sub(r"CONTENT-LENGTH: ", "", response_lines[4]))
        # Find the header length
        header_length = len(("\n".join(response_lines[:6]) + "\n").encode())
        # Obtain the data already received
        data = response[header_length:]
        # Recieve the rest of the data
        remaining_data = clientDownloadSocket.recv(data_length - header_length)
        data += remaining_data.decode()
        clientDownloadSocket.close()
        return data
    else:
        print("There was an error from the peer. This is the error code and message")
        print(response)
        return


def read_local_rfc(rfc_number):
    try:
        with open("./{}.txt".format(rfc_number), "r") as f:
            data = f.read()
        return data
    except FileNotFoundError as e:
        return ""


def write_local_rfc(rfc_number, data):
    with open("./{}.txt".format(rfc_number), "w") as f:
        f.write(data)


def handler_upload_process(peerSocket, peerAddress):
    raw_request = peerSocket.recv(1024)
    request = raw_request.decode()
    # Get the RFC Number from the request
    request_lines = request.split("\n")
    if re.search(r"P2P\-CI\/1\.0", request_lines[0]):
        if re.search(r"GET", request_lines[0]):
            rfc_number = int(re.search(r"RFC (\d+)", request_lines[0]).group(1))
            send_message = format_send_message_peer(rfc_number)
            peerSocket.sendall(send_message.encode())
            peerSocket.close()
        else:
            message = "P2P-CI/1.0 "
            message += "505 P2P-CI Version Not Supported\n"
            message += "DATE: " + str(datetime.datetime.today()) + " " + datetime.datetime.now(
                datetime.timezone.utc).astimezone().tzname() + "\n"
            message += "OS: " + platform.system() + " " + platform.release() + "\n"
            peerSocket.sendall(message.encode())
            peerSocket.close()
    else:
        message = "P2P-CI/1.0 "
        message += "400 Bad Request\n"
        message += "DATE: " + str(datetime.datetime.today()) + " " + datetime.datetime.now(
            datetime.timezone.utc).astimezone().tzname() + "\n"
        message += "OS: " + platform.system() + " " + platform.release() + "\n"
        peerSocket.sendall(message.encode())
        peerSocket.close()



def upload_process(clientUploadSocket, upload_port):
    clientName = socket.gethostname()
    clientUploadSocket.bind((clientName, upload_port))
    clientUploadSocket.listen()
    while True:
        peerSocket, peerAddress = clientUploadSocket.accept()
        peer_thread = threading.Thread(target=handler_upload_process, args=(peerSocket, peerAddress))
        peer_thread.start()


def server_process(clientServerSocket, upload_port):
    serverPort = 7734
    serverName = "manojs-mbp.lan"
    clientName = socket.gethostname()
    clientServerSocket.connect((serverName, serverPort))
    clientPort = clientServerSocket.getsockname()[1]
    while True:
        request_type = input("Please input the request type: " + "\n")
        if request_type == "ADD":
            rfc_number = input("Please input the RFC Number: " + "\n")
            rfc_title = input("Please input the RFC Title " + "\n")
            add_message = format_add_message(rfc_number, rfc_title, clientName, upload_port)
            clientServerSocket.send(add_message.encode())
            raw_response = clientServerSocket.recv(1024)
            response = raw_response.decode()
            print(response)

        elif request_type == "LIST":
            list_message = format_list_message(clientName, upload_port)
            clientServerSocket.send(list_message.encode())
            raw_response = clientServerSocket.recv(1024)
            response = raw_response.decode()
            print(response)

        elif request_type == "LOOKUP":
            rfc_number = input("Please input the RFC Number you want to lookup: " + "\n")
            rfc_title = input("Please input the RFC Title of the RFC Number entered previously: " + "\n")
            lookup_message = format_lookup_message(rfc_number, rfc_title, clientName, clientPort)
            clientServerSocket.send(lookup_message.encode())
            raw_response = clientServerSocket.recv(1024)
            response = raw_response.decode()
            print(response)

        elif request_type == "GET":
            rfc_number = input("Please input the RFC number you want to get: " + "\n")
            rfc_title = input("Please input the RFC Title of the RFC Number entered previously: " + "\n")
            lookup_message = format_lookup_message(rfc_number, rfc_title, clientName, clientPort)
            clientServerSocket.send(lookup_message.encode())
            raw_response = clientServerSocket.recv(1024)
            response = raw_response.decode()
            print("The server response to your lookup: ")
            print(response)
            response_lines = response.split("\n")
            if re.search(r"200 OK", response_lines[0]):
                # From line 1 we have all the information we need
                peer_info_line = response_lines[1].split(" ")
                # Last item in the above list is the peer port number, second last item is the peer host
                peer_host = peer_info_line[-2]
                peer_port = int(peer_info_line[-1])
                get_message = format_get_message(rfc_number, peer_host)
                data = get_file(peer_host, peer_port, get_message)
                if data:
                    write_local_rfc(rfc_number, data)
                    # Sending ADD request to Server so that the server can keep his things updated
                    add_message = format_add_message(rfc_number, rfc_title, clientName, upload_port)
                    clientServerSocket.send(add_message.encode())
                    raw_response = clientServerSocket.recv(1024)
                    response = raw_response.decode()
                    print(response)
            else:
                print("There was an error, here is your error message")
                print(response)

        elif request_type == "CLOSE":
            clientServerSocket.close()
            break


def main():
    # Manually create a random port number for the upload socket connection
    upload_port = 50001 + random.randint(0, 1000)
    clientUploadSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    upload_thread = threading.Thread(target=upload_process, args=(clientUploadSocket, upload_port))

    clientServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_thread = threading.Thread(target=server_process, args=(clientServerSocket, upload_port))

    upload_thread.start()
    server_thread.start()


main()
