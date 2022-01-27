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
script_arg=()
rerun_j=1
opts="--help --rerun= --build --rootfs --download= --script --code"
pre_opts="native adb"
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
if [ -f "${HIK_SCRIPT_TOP_DIR}/company/companybase.sh" ];then
source ${HIK_SCRIPT_TOP_DIR}/company/companybase.sh
fi