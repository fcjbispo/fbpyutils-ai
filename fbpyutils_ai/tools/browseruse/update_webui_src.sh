wget https://github.com/browser-use/web-ui/archive/refs/heads/main.zip
unzip main.zip -d temp_zip
rm -rf src/
mv temp_zip/web-ui-main/src .
rm -rf temp_zip
rm main.zip