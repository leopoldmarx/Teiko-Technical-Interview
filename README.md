# Teiko Technical Interview

This is Leopold Marx's submission to a technical interview for Teiko that was assigned Saturday, May 31st, 2025. This repository contains a Streamlit-based web application developed for a technical interview project. It includes a database schema, statistical analysis, and visualizations.

To see the hosted version of the app, please visit (here)[https://teiko.lmarx.com/].

## Build locally:

To build this on your local machine, follow the steps below:

1. Prerequisites

Make sure you have the following tools installed:

- Docker
- Make

2. Clone or download the repository

```bash
git clone https://github.com/leopoldmarx/Teiko-Technical-Interview.git
cd Teiko-Technical-Interview
```

3. Build and run the app using Make (WSL or Unix Environment):

```bash
make run
```

4. Open your browser and visit [http://localhost:38080](http://localhost:38080)

## Steps to Deploy Streamlit App on [lmarx.com](lmarx.com):

1. Build docker image locally via `make run-and-push-image` command.

2. Confirm Docker image is up-to-date on [DockerHub](https://hub.docker.com/repository/docker/leopoldmarx/teiko-technical-interview).

3. Spin up container on my home server.

4. Website configuring like adding CNAME, NGINX proxy, and related settings.
