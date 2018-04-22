#!/usr/bin/env bash
cd "$( dirname "${BASH_SOURCE[0]}" )"

sudo umount /var/www/html && rmdir /var/www/html

sudo mv /var/www/html.old /var/www/html