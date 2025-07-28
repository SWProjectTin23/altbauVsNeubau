#!/bin/bash

# github-runner-docker/entrypoint.sh

# ERSTELLE DEN BENUTZER, FALLS ER NICHT EXISTIERT (oder wenn im Dockerfile schon gemacht)
if ! id "github-runner" &>/dev/null; then
    echo "Creating user github-runner..."
    useradd -m github-runner
    chown -R github-runner:github-runner /actions-runner
fi

# Stellen Sie sicher, dass alle notwendigen Umgebungsvariablen gesetzt sind.
# BEACHTE: Hier prüfen wir nur auf REPO_URL, RUNNER_NAME. ACCESS_TOKEN (das PAT) ist für später.
# Das REGISTRATION_TOKEN ist das entscheidende für config.sh.
if [ -z "$REPO_URL" ] || [ -z "$RUNNER_NAME" ] || [ -z "$REGISTRATION_TOKEN" ]; then
    echo "Error: REPO_URL, RUNNER_NAME, and REGISTRATION_TOKEN must be set as environment variables."
    echo "REGISTRATION_TOKEN ist das kurzlebige Token von GitHub, nicht dein PAT (ACCESS_TOKEN)."
    exit 1
fi

# Setzen Sie Standard-Labels, falls keine angegeben wurden.
if [ -z "$RUNNER_LABELS" ]; then
    RUNNER_LABELS="self-hosted,linux"
fi

# Konfigurieren Sie den Runner bei GitHub als der 'github-runner' Benutzer
echo "Configuring GitHub Actions runner..."
# Konfiguration direkt als github-runner ausführen mit gosu
# WICHTIG: Hier verwenden wir REGISTRATION_TOKEN für die Registrierung.
gosu github-runner ./config.sh \
    --url "$REPO_URL" \
    --token "$REGISTRATION_TOKEN" \ # <--- HIER MUSS DAS KURZLEBIGE TOKEN REIN!
    --name "$RUNNER_NAME" \
    --labels "$RUNNER_LABELS" \
    --unattended \
    --replace

# Jetzt, da der Runner konfiguriert ist, wird das PERSÖNLICHE ZUGRIFFS-TOKEN (PAT) für run.sh benötigt.
# Stelle sicher, dass ACCESS_TOKEN (dein PAT) auch vorhanden ist.
if [ -z "$ACCESS_TOKEN" ]; then
    echo "Error: ACCESS_TOKEN (Personal Access Token) must be set for the runner to function after configuration."
    exit 1
fi


# Starte den Runner als der 'github-runner' Benutzer
echo "Starting GitHub Actions runner..."
# run.sh verwendet dann automatisch das in config.sh konfigurierte Token,
# oder dein PAT, wenn es für bestimmte Aktionen benötigt wird.
exec gosu github-runner ./run.sh