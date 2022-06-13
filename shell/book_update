#!/bin/bash
_describe() { echo "工作笔记本上传Calibre书籍数据到腾讯云"; }
if [[ "${describe}" == "describe" ]];then _describe;exit 0;fi

rsync -rvlt ~/private/win/Calibre/ hik-vps:/data/calibre/books/ 
