#!/bin/bash

# Get the directory of the install script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Copy the application, .desktop file, and icon to the appropriate directories
cp "$DIR/login.sh" /opt/my_application/
cp "$DIR/desktop-application.png" /opt/my_application/
cp "$DIR/Login.desktop" /usr/share/applications/

# Update the paths in the .desktop file
sed -i "s|Exec=.*|Exec=/opt/my_application/run_login.sh|" /usr/share/applications/Login.desktop
sed -i "s|Icon=.*|Icon=/opt/my_application/desktop-application.png|" /usr/share/applications/Login.desktop