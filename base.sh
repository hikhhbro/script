#所支持的工程
project_type=()
#机型
machine_type=()
project=()
build=""
rootfs=""
download=""
machine=""
prebuilt=""
dev=""
rerun="rerun"
script_func=""
run_adb=""
run_gits=""
script_arg=()
self_arg=()
rerun_j=1
opts="--help --rerun= --script --code --rm"
db="_task"
describe=""
#公共选项提示
pub_opt=" -h -V"
function _func() {
  echo -en "\033[33mCurrent$FUNCNAME => (${FUNCNAME[1]}): \033[0m"
  for i in "$*"      #在"$*"中遍历参数，此时"$*"被扩展为包含所有位置参数的单个字符串，只遍历一次
  do
    echo $i
  done
}
function _task() {
  # if [ "$(type -t $1)" = "builtin" ] || [ "$(type -t $1)" = "file" ]; then
    echo -e "\033[33mRunning$FUNCNAME => ($*): \033[0m"  
    $*
  # fi
}
function _debug_task() {
  # if [ "$(type -t $1)" = "builtin" ] || [ "$(type -t $1)" = "file" ]; then
    echo -e -n "\033[33mRunning$FUNCNAME => ($*): \033[0m"  
    read 
    $*
  # fi
}
if [ -f "${HIK_SCRIPT_TOP_DIR}/company/companybase.sh" ];then
source ${HIK_SCRIPT_TOP_DIR}/company/companybase.sh
fi

#创建脚本
touch_script() {
  _func
  if [[ "$1" == "-c" ]];then
      if [ ! -f "${HIK_SCRIPT_TOP_DIR}/company/$3" ];then
        cp ${HIK_SCRIPT_TOP_DIR}/.template > ${HIK_SCRIPT_TOP_DIR}/company/$3
        chmod 755 ${HIK_SCRIPT_TOP_DIR}/company/$3
      fi
      code ${HIK_SCRIPT_TOP_DIR}/company/$3
      exit 0
  else
    if [ -f "${HIK_SCRIPT_TOP_DIR}/company/$1" ];then
      code ${HIK_SCRIPT_TOP_DIR}/company/$1
    elif [ -f "${HIK_SCRIPT_TOP_DIR}/script/$1" ];then
      code ${HIK_SCRIPT_TOP_DIR}/script/$1
    elif [ -f "${HIK_SCRIPT_TOP_DIR}/$1" ];then
      code ${HIK_SCRIPT_TOP_DIR}/$1
    else
      cp ${HIK_SCRIPT_TOP_DIR}/.template > ${HIK_SCRIPT_TOP_DIR}/script/$1
      chmod 755 ${HIK_SCRIPT_TOP_DIR}/script/$1
      code ${HIK_SCRIPT_TOP_DIR}/script/$1
    fi
  fi
}

#删除脚本
rm_script() {
    _func
  if [[ "$1" == "-c" ]];then
      mv ${HIK_SCRIPT_TOP_DIR}/company/$3 ${HIK_SCRIPT_TOP_DIR}/company/.resycle/$3
  else
    if [ -f "${HIK_SCRIPT_TOP_DIR}/script/$1" ];then
        mv "${HIK_SCRIPT_TOP_DIR}/script/$1" ${HIK_SCRIPT_TOP_DIR}/.resycle/$1
    else
        mv ${HIK_SCRIPT_TOP_DIR}/company/$1 ${HIK_SCRIPT_TOP_DIR}/company/.resycle/$1
    fi
  fi
}
# 帮助
usage() {
  echo -e "Usage: ./$(basename $0) [-t value] [-t value] [-h] [value]\n"
  echo "-h           help"
}
my_compile() {
  local tem_line=""
  local line_nub=0
  local flag_read="begin"
  local func_read=""
  local prefix_=$1
  local prefix_=${prefix_##*/}

  echo 0 > ${HIK_SCRIPT_TOP_DIR}/.compile/.tmp
  echo '#!/bin/bash' > ${HIK_SCRIPT_TOP_DIR}/.compile/$1
  while read -r line || [[ -n ${line} ]]
  do
    head_=(${line})
    case "${flag_read}" in
      begin)
        if [[ "${head_[0]}" == "<_describe>" ]] ;then
          func_read=${head_[0]:1:-1}
          flag_read=${head_[1]}
          if [[ "${flag_read}" == "begin" ]] ;then
            echo "${prefix_}${func_read}() {" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
          else
            echo "}" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
          fi
        elif [[ "${head_[0]}" == "<_get_options>" ]] ;then  
          func_read=${head_[0]:1:-1}
          flag_read=${head_[1]}
          echo "${prefix_}${func_read}() {" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
          echo "echo \"\$(${prefix_}_s${func_read}) \$(${prefix_}_l${func_read}) \$(${prefix_}_o${func_read})\"" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
          echo "}" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
        elif [[ "${func_read}" == "_describe" ]] ;then
          echo "echo \"${line} \"" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
        elif [[ "${func_read}" == "_get_options" ]] ;then
          if [[ "${line%:*}" == "短选项(-*)" ]];then
            echo "${prefix_}_s${func_read}() {" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
            echo "echo \"${line##*:}\"" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
            echo "}" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
          elif [[ "${line%:*}" == "长选项(--*)" ]];then
            echo "${prefix_}_l${func_read}() {" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
            echo "echo \"${line##*:}\"" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
            echo "}" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
          elif [[ "${line%:*}" == "其他选项" ]];then
            echo "${prefix_}_o${func_read}() {" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
            echo "echo \"${line##*:}\"" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
            echo "}" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
          # options_tmp=${line:3}
          # echo "echo \"${line:3} \"" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
          fi
        fi
        ;;
      end)
        if [[ "${head_[0]}" == "<_describe>" ]] ;then
          func_read=${head_[0]:1:-1}
          flag_read=${head_[1]}
          # echo ${func_read}
        elif [[ "${head_[0]}" == "<_get_options>" ]] ;then  
          func_read=${head_[0]:1:-1}
          flag_read=${head_[1]}
        elif [[ "${head_[0]}" == "#<user_func>" ]] ;then  
          func_read=${head_[0]}
        elif [[ "${head_[0]}" == "#<main>" ]] ;then  
            flag_read="probe"
            func_read="_probe"
            echo "${prefix_}${func_read}() {" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
        else
          if [[ "${func_read}" == "#<user_func>" ]] ;then 
            if [[ "$(type -t ${head_[0]})" == "builtin" ||  "$(type -t ${head_[0]})" == "file" ]] ; then
              line='${db}'" $line" 
            fi
            echo $line >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
          fi
        fi
      ;;
      probe)
        if [[ "$(type -t ${head_[0]})" == "builtin" ||  "$(type -t ${head_[0]})" == "file" ]] ; then
          line='${db}'" $line" 
          echo 1 > ${HIK_SCRIPT_TOP_DIR}/.compile/.tmp
        fi
         echo $line >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
      ;;
    esac
  done < "${HIK_SCRIPT_TOP_DIR}/$1"
  # if [[ cat ${HIK_SCRIPT_TOP_DIR}/$1" == "" ]];then
  if [ `cat ${HIK_SCRIPT_TOP_DIR}/.compile/.tmp` -eq 0 ];then
    echo "echo -e \"\033[33m${prefix_}未实现\033[0m\"" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
    echo 0 > ${HIK_SCRIPT_TOP_DIR}/.compile/.tmp
  fi
  echo "}" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
}