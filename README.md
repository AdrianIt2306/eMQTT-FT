# File transfer over MQTT for eMQTT Suite

eMQTT FT is a script that was developed to test the file transfer between devices using MQTT protocol. It was tested with images, text files and csv.

## Features

- Run in multiple OS 
- File configuration with .env file
- Good transfer rate for big files
- Support multi transfer at same time 

## Scripts

The repository includes the next files that need to be take in place in server or client side

- rx.py - The script for reception files, it needs to be installed on broker MQTT
- tx.py - The script for transmission files, it works like client to send the request to the broker, it receive the location of the file that we want to transfer
- .env - The configuration file used by the client or server side, it contains user, password, location and client id

## Test case
Below some examples of how you can use the script in different ways

For transfer files

```sh
tx.py <full_path_of_file_name>
```

For reception files

```sh
rx.py 
```
