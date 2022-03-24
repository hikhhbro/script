. base.sh
if [ -f "/usr/local/bin/hikrun" ];then
echo "卸载"
. uninstall.sh
echo "卸载完成"
fi
if [ -f "/etc/bash_completion.d/hikrun_prompt" ];then
echo "卸载"
. uninstall.sh
echo "卸载完成"
fi
echo "正在安装"
if [ ! -d company/ ];then
    _task mkdir company
    _task  touch company/companybase.sh
    _task  touch company/companyfunc.sh
fi
if [ ! -d company/.resycle/ ];then
    _task mkdir company/.resycle
fi
if [ ! -d script/ ];then
_task mkdir script
fi
if [ ! -d .resycle/ ];then
_task mkdir .resycle
fi

_task sed -i '/HIK_SCRIPT_TOP_DIR/d'  ~/.bashrc
echo "export HIK_SCRIPT_TOP_DIR=`pwd`" >> ~/.bashrc
_task source ~/.bashrc

echo ". `pwd`/hikrun.sh \$*" >  hikrun
_task sudo mv hikrun /usr/local/bin/hikrun
_task sudo chmod 755 /usr/local/bin/hikrun

echo ". `pwd`/hik_run_complete.sh \$*" >  hikrun_prompt
_task sudo mv hikrun_prompt /etc/bash_completion.d/hikrun_prompt
_task sudo chmod 755 /etc/bash_completion.d/hikrun_prompt
_task source ~/.bashrc
echo -n "---安装完成---输入任意键结束------"
read 
exit 0