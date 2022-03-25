source ${HIK_SCRIPT_TOP_DIR}/base.sh
probe="probe"
t_opts=`cat ${HIK_SCRIPT_TOP_DIR}/.compile/.tmp_opt`
l_t_opts=`cat ${HIK_SCRIPT_TOP_DIR}/.compile/.l_tmp_opt`
in_opts=""
# 输入
ARGS=$(getopt -o ${t_opts}hVbrdpB:C: --long ${l_t_opts}help,rerun:,build,rootfs,script:,download:,code:,rm: -n 'hikrun' -- "$@")
error_return=$?
#状态决策
if [ ${error_return} != 0 ]; then
  echo "please use '  hikrun -h ' to view details "
  exit 0
fi
eval set -- "${ARGS}"
while true; do
  case "$1" in
    #创建
    --code)
      case "$2" in
        *)
          touch_script ${@:2}
          exit 0
        ;;
      esac
    ;;
    #删除
    --rm)
      case "$2" in
        *)
          rm_script ${@:2}
          exit 0
        ;;
      esac
    ;;
    #调试选项
    -V)
      db="_debug_task"
      shift
    ;;
    --rerun)
      case "$2" in
        *)
          rerun_j=$2
          shift 2
        ;;
      esac
    ;;
    #执行其他脚本
    --script)
      case "$2" in
        *)
          script="script"
          script_arg=(${script_arg[*]} $2)
          shift 2
        ;;
      esac
    ;;
    #帮助
    -h | --help)
      describe="describe"
      probe=""
      shift
    ;;
    # 可变参数
    --)
      shift 
      break
    ;;
    -*)
      in_opts="$1 ${in_opts}"
      shift
    ;;
    # 不支持
    *)
      shift
    break;;
  esac
done
#剩余参数
script_arg=($@)
self_arg=($@)
# echo  ${@:2} 从第二个开始
#函数定义和注册
source ${HIK_SCRIPT_TOP_DIR}/function.sh
# 函数执行
for func in ${run_func[*]}
do
  # echo $func ${@:1}
  if [ "$(type -t $func)" = "function" ] ; then
    # echo $func ${@:1}
    $func ${in_opts} ${@:2}
    unset $func
  fi
done
unset db
