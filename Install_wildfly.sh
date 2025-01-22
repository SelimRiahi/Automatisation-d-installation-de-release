#!/bin/bash

WILDFLY_VERSION="26.1.3.Final"
WILDFLY_USER="wildfly"
WILDFLY_INSTALL_DIR="/opt/wildfly"
WILDFLY_DOWNLOAD_URL="https://github.com/wildfly/wildfly/releases/download/${WILDFLY_VERSION}/wildfly-${WILDFLY_VERSION}.zip"
WILDFLY_SERVICE_FILE="/etc/systemd/system/wildfly.service"

echo "Creating WildFly user if not exists..."
getent passwd ${WILDFLY_USER} > /dev/null
if [ $? -eq 0 ]; then
    echo "User ${WILDFLY_USER} already exists."
else
    echo "Creating user ${WILDFLY_USER}..."
    useradd -r ${WILDFLY_USER}
fi

echo "Downloading WildFly ${WILDFLY_VERSION}..."
sudo -u ${WILDFLY_USER} wget ${WILDFLY_DOWNLOAD_URL} -O /tmp/wildfly-${WILDFLY_VERSION}.zip

echo "Creating Installation Directory..."
mkdir -p ${WILDFLY_INSTALL_DIR}
chown ${WILDFLY_USER}:${WILDFLY_USER} ${WILDFLY_INSTALL_DIR}

echo "Extracting WildFly..."
sudo -u ${WILDFLY_USER} unzip -oq /tmp/wildfly-${WILDFLY_VERSION}.zip -d ${WILDFLY_INSTALL_DIR}
chown -R ${WILDFLY_USER}:${WILDFLY_USER} ${WILDFLY_INSTALL_DIR}/wildfly-${WILDFLY_VERSION}

echo 'WILDFLY_HOME="'${WILDFLY_INSTALL_DIR}'/wildfly-'${WILDFLY_VERSION}'"' | tee -a /etc/environment

echo "Creating WildFly Systemd Service File..."
cat <<EOF > ${WILDFLY_SERVICE_FILE}
[Unit]
Description=WildFly Application Server
After=network.target

[Service]
User=${WILDFLY_USER}
Group=${WILDFLY_USER}
ExecStart=${WILDFLY_INSTALL_DIR}/wildfly-${WILDFLY_VERSION}/bin/standalone.sh -b=0.0.0.0
ExecStop=${WILDFLY_INSTALL_DIR}/wildfly-${WILDFLY_VERSION}/bin/jboss-cli.sh --connect command=:shutdown
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading Systemd Daemon if available..."
if command -v systemctl > /dev/null; then
    systemctl daemon-reload
    echo "Starting and enabling WildFly service..."
    systemctl start wildfly
    systemctl enable wildfly
else
    echo "Systemd is not available, unable to start WildFly service."
    # You might need to start the service using a different method depending on your init system
fi

echo "WildFly installation and configuration completed."
