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
  - [x] (1.2) Start server and listen for connections
  - [ ] (1.3) Optionally broacast the server on LAN
  - [ ] (1.4) Authenticate users + implement a messaging protocol
  - [ ] (1.5) Support secure, optional, TLS encryption
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
  - [ ] (2.5) Support optional encryption
- [ ] (3) Add a web panel for admin and client access (optional):
  - [ ] (3.1) Support (and recognise) connections from regular browsers
  - [ ] (3.2) Serve a dynamic, single-page website:
    - [ ] (3.2.1) Add website location to config
    - [ ] (3.2.2) Use color scheme from the config
    - [ ] (3.2.3) Show a secure login page
  - [ ] (3.3) Allow changes to the configuration from the website:
    - [ ] (3.3.1) Use the pre-existing API in the JavaScript on the website
    - [ ] (3.3.2) Ensure security of this system
  - [ ] (3.4) Allow messaging from the website
- [ ] (4) Thoroughly test the software
- [ ] (5) Complete wiki

