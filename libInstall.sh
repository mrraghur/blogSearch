cat requirements.txt | while read LINE; do
    pip install $LINE
    done
