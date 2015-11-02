# You should run this file from the command line to start the program

# Prerequisites: Python installed; Caffe installed with Python wrapper; php5, php5-gd, php5-cgi packages installed
# (PHP is necessary as we are creating the CAPTCHA images with a PHP script.)
# Adjust $caffe variable in src/iterate.sh to point to your correct caffe foler

chmod +x iterate.sh
./iterate.sh > /dev/null 2>&1 & echo $! > /dev/null
echo "The program was started in the background. All logs and outputs are written to the files results/<test_name>/log.txt and log2.txt"