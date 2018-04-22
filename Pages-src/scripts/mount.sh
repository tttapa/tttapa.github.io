#!/usr/bin/env bash
cd "$( dirname "${BASH_SOURCE[0]}" )"

sudo mv /var/www/html /var/www/html.old 

mkdir -p /var/www/html && sudo mount --bind ../.. /var/www/html

sudo chown -R $USER /var/www/html
sudo chgrp -R www-data /var/www/html
sudo chmod -R 775 /var/www/html
