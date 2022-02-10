#!/bin/bash
fileid="1UxIlQPR5z2tEd7IAy4BwUzp4Vkf9PECB"
filename="images.zip"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o ${filename}
