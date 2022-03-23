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
opts="--help --rerun= --build --rootfs --download= --script --code --rm"
pre_opts="native adb gits"
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
    echo -e "\033[33mRunning$FUNCNAME => ($*): \033[0m"  
    $*
}
function _debug_task() {
    echo -e -n "\033[33mRunning$FUNCNAME => ($*): \033[0m"  
    read 
    $*
}
if [ -f "${HIK_SCRIPT_TOP_DIR}/company/companybase.sh" ];then
source ${HIK_SCRIPT_TOP_DIR}/company/companybase.sh
fi

#创建脚本
touch_script() {
  _func
  if [[ "$1" == "-c" ]];then
      if [ ! -f "${HIK_SCRIPT_TOP_DIR}/company/$3" ];then
        sed 's/template/'$3'/g' ${HIK_SCRIPT_TOP_DIR}/.template > ${HIK_SCRIPT_TOP_DIR}/company/$3
        chmod 755 ${HIK_SCRIPT_TOP_DIR}/company/$3
      fi
      code ${HIK_SCRIPT_TOP_DIR}/company/$3
      exit 0
  fi
  if [ -f "${HIK_SCRIPT_TOP_DIR}/$1" ];then
      code ${HIK_SCRIPT_TOP_DIR}/$1
      exit 0
  fi
  if [ ! -f "${HIK_SCRIPT_TOP_DIR}/script/$1" ];then
    sed 's/template/'$1'/g' ${HIK_SCRIPT_TOP_DIR}/.template > ${HIK_SCRIPT_TOP_DIR}/script/$1
    chmod 755 ${HIK_SCRIPT_TOP_DIR}/script/$1
  fi
  code ${HIK_SCRIPT_TOP_DIR}/script/$1
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