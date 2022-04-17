#/bin/sh

OSTYPE=`uname`
suffix=""
if [ "$OSTYPE" == "Darwin" ]; then
    suffix="_macos"
    cd /usr/local/bin
else
    cd /usr/bin
fi

curl -L -O https://github.com/juanpisuribe13/sv-dlp/releases/latest/download/sv-dlp$suffix
mv "sv-dlp$suffix" "sv-dlp"
chmod +x "sv-dlp"
cd -;