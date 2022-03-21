#!/bin/bash
_describe() { echo "工作机端口转发到自己笔记本"; }
if [[ "${describe}" == "describe" ]];then _describe;exit 0;fi

_task ssh -f -N  -L 3022:192.168.1.12:3022 hik@$1