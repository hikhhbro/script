#!/bin/bash
_describe() { echo "查找repo中最近提交的仓库"; }
if [[ "${describe}" == "describe" ]];then _describe;exit 0;fi

if [ $1 = 't' ];
then
repo forall -c 'committime=`git log --after "'$2' 07:00"   -1 --pretty=format:"%cd"`;
if [ "$committime" != "" ]; then
  echo -e "\033[33m$(pwd)\033[0m" 
  git log -1
  echo ""
fi
'
elif [ $1 = 'an' ];
then
    repo forall -c 'committime=`git log  -1 --author="'$2'"`;
                    if [ "$committime" != "" ]; then
                      echo -e "\033[33m$(pwd)\033[0m" 
                      git log -1
                      echo ""
                    fi
                    '
else
  echo "输入时间或者邮箱
        例如:
        t  2021-12-01
        an  wangyingdong"
fi