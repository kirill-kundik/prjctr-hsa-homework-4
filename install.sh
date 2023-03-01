#!/bin/bash

# Checking environment variables
if grep -q -e "<YOUR_GA_API_SECRET>" -e "<YOUR_GA_MEASUREMENT_ID>" -e "<YOUR_GA_CLIENT_ID>" main.py; then
    echo "Check your environment variables at the beginning of 'main.py' script."
    echo "You need to replace <YOUR_GA_API_SECRET> with your GA Measurement Protocol API secret."
    echo "You need to replace <YOUR_GA_MEASUREMENT_ID> with your GA Measurement ID."
    echo "You need to replace <YOUR_GA_CLIENT_ID> with your GA Client ID."
    echo "Check out detailed guide: https://developers.google.com/analytics/devguides/collection/protocol/ga4/sending-events?client_type=gtag"
    exit 1
fi


APP_DIR=/usr/local/etc/ga-uah-events-sender
mkdir -p $APP_DIR
cd $APP_DIR

echo "Setting up Python virtual environment"
# Set up a virtual environment
python3 -m venv venv
source venv/bin/activate

eho "Installing Python required libraries"
# Install required Python packages
pip install -r requirements.txt

echo "cd $APP_DIR && source venv/bin/activate && python main.py" >> start.sh

echo "Adding cronjob to run the script every hour"
# Add cron job to run the script every hour
(crontab -l 2>/dev/null; echo "0 * * * * /bin/bash $APP_DIR/start.sh") | crontab -

# Deactivate virtual environment
deactivate

echo "Script was successfully deployed"

exit 0
