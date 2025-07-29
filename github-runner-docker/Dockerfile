# github-runner-docker/Dockerfile
# Wir starten von einem aktuellen Ubuntu-Image, da der Runner gut damit funktioniert.
FROM ubuntu:latest

# Setze diese Variable für eine nicht-interaktive Installation der Pakete.
ENV DEBIAN_FRONTEND=noninteractive

# Installiere alle notwendigen Systempakete für den Runner und die Docker CLI.
# Docker CLI ist entscheidend, damit der Runner später 'docker-compose' Befehle ausführen kann.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gosu \                 
    curl \                
    git \                  
    jq \                   
    libicu-dev \
    libunwind8 \
    libssl-dev \
    apt-transport-https \
    ca-certificates \
    software-properties-common \
    gnupg2 && \
    rm -rf /var/lib/apt/lists/*

# Füge den offiziellen Docker GPG-Key hinzu und registriere das Docker Repository.
# Installiere anschließend die Docker CLI-Tools.
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
    apt-get update && \
    apt-get install -y docker-ce-cli

# Lade und installiere den GitHub Actions Runner.
# Wichtig: Überprüfe die URL für die NEUESTE VERSION auf
# https://github.com/actions/runner/releases
# Lade und installiere den GitHub Actions Runner
ENV RUNNER_VERSION="2.327.1"
ENV RUNNER_ARCH="x64"
ENV RUNNER_OS="linux"
ENV RUNNER_TEMP=/tmp/runner-temp

RUN mkdir /actions-runner && \
    cd /actions-runner && \
    curl -o actions-runner.tar.gz -L "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-${RUNNER_OS}-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz" && \
    tar xzf ./actions-runner.tar.gz && \
    rm actions-runner.tar.gz

# Erstelle einen Benutzer für den GitHub Actions Runner
RUN useradd -m github-runner && \
    chown -R github-runner:github-runner /actions-runner

# Setze Umgebungsvariablen für den Runner    
ARG DOCKER_GID=998

# Erstelle eine Gruppe im Container mit der gleichen GID wie die Docker-Gruppe auf dem Host
# und füge den GitHub Actions Runner-Benutzer zu dieser Gruppe hinzu.
# Der Benutzername 'github-runner' wird hier verwendet, da du ihn oben erstellt hast.
RUN GROUP_NAME=$(getent group $DOCKER_GID | cut -d: -f1); \
    if [ -z "$GROUP_NAME" ]; then \
        GROUP_NAME="docker_host"; \
        groupadd -g $DOCKER_GID $GROUP_NAME; \
    fi && \
    usermod -aG $GROUP_NAME github-runner

# Setze das Arbeitsverzeichnis im Container
WORKDIR /actions-runner

# Kopiere das Entrypoint-Skript und mache es ausführbar
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# BLEIBE HIER BEI ROOT FÜR DEN ENTRYPOINT
# ENTRYPOINT ["./entrypoint.sh"] <-- KEIN USER WECHSEL HIER
ENTRYPOINT ["./entrypoint.sh"]