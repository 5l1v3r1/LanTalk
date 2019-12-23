# LanTalkServer

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
- (1) Complete first working version of the server (Not Done):
  - (1.1) Read and parse configuration (Not Done)
  - (1.2) Start server and listen for connections (Not Done)
  - (1.3) Optionally broacast the server on LAN (Not Done)
  - (1.4) Authenticate users + implement a messaging protocol (Not Done)
  - (1.5) Support secure end-to-end AES encryption (Not Done)
  - (1.6) Gracefully handle errors and disconnects (Not Done)
- (2) Complete first working version of the client (Not Done):
  - (2.1) Working server list interface (Not Done):
    - (2.1.1) Receive broadcasts and send own broadcasts (Not Done)
    - (2.1.2) List servers which repiled to a broadcast (Not Done)
    - (2.1.3) Allow adding a custom server (Not Done)
  - (2.2) Working authentication interface (Not Done):
    - (2.2.1) Allow user to enter their credentials if required by server (Not Done)
    - (2.2.2) Securely log the user in (Not Done)
  - (2.3) Working chat interface (Not Done):
    - (2.3.1) Implement the communication protocol (Not Done)
    - (2.3.2) Correctly display incoming/outgoing messages (Not Done)
  - (2.4) Working settings interface (Not Done):
    - (2.4.1) Fetch available settings from server (Not Done)
    - (2.4.2) Save settings to server (Not Done)
  -(2.5) Support end-to-end encryption (Not Done):
    - (2.5.1) Encrypt sent messages (Not Done)
    - (2.5.2) Decrypt received messages (Not Done)
- (3) Thoroughly test the software (Not Done)
- (4) Complete wiki
