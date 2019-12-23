# LanTalk

## Description
Configurable python3 scripts (server &amp; client) for real-time, encrypted messaging on a Local Area Network (and outside of it) using HTTP.

## Getting Started
- (1) Place all of the server files in one folder
- (2) Run the server with python3 (eg. `python3 server.py`)
- (3) Run the client with python3 (eg. `python3 client.py`)
- (4) With the default configuration, the server should be detected automatically on a LAN. If not, select `Add Server` to add its IP and port number
- (5) Log in as the admin user (Username: `admin`, Password: `admin_123`)
- (6) Add users in the settings menu. They should automatically be added to the configured file

## Project Roadmap
- [ ] (1) Complete first working version of the server:
  - [x] (1.1) Read and parse configuration
  - [ ] (1.2) Start server and listen for connections
  - [ ] (1.3) Optionally broacast the server on LAN
  - [ ] (1.4) Authenticate users + implement a messaging protocol
  - [ ] (1.5) Support secure end-to-end AES encryption
  - [ ] (1.6) Gracefully handle errors and disconnects
- [ ] (2) Complete first working version of the client:
  - [ ] (2.1) Working server list interface:
    - [ ] (2.1.1) Receive broadcasts and send own broadcasts
    - [ ] (2.1.2) List servers which repiled to a broadcast
    - [ ] (2.1.3) Allow adding a custom server
  - [ ] (2.2) Working authentication interface:
    - [ ] (2.2.1) Allow user to enter their credentials if required by server
    - [ ] (2.2.2) Securely log the user in
  - [ ] (2.3) Working chat interface:
    - [ ] (2.3.1) Implement the communication protocol
    - [ ] (2.3.2) Correctly display incoming/outgoing messages
  - [ ] (2.4) Working settings interface:
    - [ ] (2.4.1) Fetch available settings from server
    - [ ] (2.4.2) Save settings to server
  - [ ] (2.5) Support end-to-end encryption:
    - [ ] (2.5.1) Encrypt sent messages
    - [ ] (2.5.2) Decrypt received messages
- [ ] (3) Thoroughly test the software
- [ ] (4) Complete wiki

Complete: 0/25
