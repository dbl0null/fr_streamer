source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv -p python3 on_premise
workon on_premise
pip install -r requirements.txt
echo "Setup of on_premise python env is complete."