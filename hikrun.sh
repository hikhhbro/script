source ${HIK_SCRIPT_TOP_DIR}/base.sh
probe="probe"
if [ ! -f ${HIK_SCRIPT_TOP_DIR}/.compile/.tmp_opt ] || [ ! -f ${HIK_SCRIPT_TOP_DIR}/.compile/.l_tmp_opt ] || [ ! -f ${HIK_SCRIPT_TOP_DIR}/.compile/.no_su_flag ] ;then
    echo > ${HIK_SCRIPT_TOP_DIR}/.compile/.tmp_opt
    echo > ${HIK_SCRIPT_TOP_DIR}/.compile/.l_tmp_opt
    echo > ${HIK_SCRIPT_TOP_DIR}/.compile/.no_su_flag
fi

t_opts=`cat ${HIK_SCRIPT_TOP_DIR}/.compile/.tmp_opt`
l_t_opts=`cat ${HIK_SCRIPT_TOP_DIR}/.compile/.l_tmp_opt`
#不支持的脚本打开
no_su=`cat ${HIK_SCRIPT_TOP_DIR}/.compile/.no_su_flag`
if [[ "${no_su}" != "" ]];then
  echo  > ${HIK_SCRIPT_TOP_DIR}/.compile/.no_su_flag
  cp ${no_su} "${no_su%/*}/.resycle/${no_su##*/}"
  cat ${HIK_SCRIPT_TOP_DIR}/.template > ${no_su}
  
  echo -e "\n<------修改------->" >> ${no_su}
  cat "${no_su%/*}/.resycle/${no_su##*/}" >> ${no_su}
  code ${no_su}
  exit 0
fi
in_opts=""
short_opts="${t_opts}hVr"
long_opts="${l_t_opts}help,rerun:,script:,code:,rm:"
# 输入
ARGS=$(getopt -o ${short_opts} --long ${long_opts} -n 'hikrun' -- "$@")
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
    -h)
      describe="describe"
      probe=""
      shift
    ;;
    #全部描述
    --help)
      describe="all_describe"
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
#函数定义和注册
source ${HIK_SCRIPT_TOP_DIR}/function.sh
# 函数执行
for func in ${run_func[*]}
do
  if [ "$(type -t $func)" = "function" ] ; then
    $func ${in_opts} ${@:2}
    unset $func
  fi
done

if [ "$(type -t ${script_arg[0]}_${probe})" = "function" ] ; then
    if [ "${rerun_j}" -gt 0 ];then
      for i in $(seq 1 $rerun_j)
      do
          echo  "第${i}次执行开始 === 剩余:$(expr $rerun_j - $i)次"
          ${script_arg[0]}_${probe} ${in_opts} ${@:2}
      done
    elif [ "${rerun_j}" -eq -1 ];then
      echo -n "进入无限循环"
      while true
      do
        let i++
        echo "第${i}次执行开始"
        ${script_arg[0]}_${probe} ${in_opts} ${@:2}
        sleep 10
      done
    fi
    
    else
        ${script_arg[0]}_${probe} ${in_opts} ${@:2}
    fi
  unset $func
fi
  
unset db

