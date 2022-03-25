source ${HIK_SCRIPT_TOP_DIR}/base.sh
probe="probe"
# 输入
_optss=""
ARGS=$(getopt -o :hVbrdpB:C: --long help,rerun:,build,rootfs,script:,download:,code:,rm: -n 'hikrun' -- "$@")
error_return=$?

eval set -- "${ARGS}"
while true; do
    echo $1
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
    #下载重包或者使用cache
    -p)
      prebuilt="prebuilt"
      shift
    ;;
    #调试选项
    -V)
      db="_debug_task"
      shift
    ;;
    #base 选项
    -B)
      project=(${project_type[0]})
      case "$2" in
        *)
          if [[ ${machine_type[@]/$2/} != ${machine_type[@]} ]];then
            machine=$2
          else
            echo "暂不支持:$2" "===>${machine_type[*]}"
            exit 1
          fi
          shift 2
        ;;
      esac
    ;;
    #core 选项
    -C)
      project=(${project_type[0]})
      case "$2" in
        *)
          if [[ ${machine_type[@]/$2/} != ${machine_type[@]} ]];then
            machine=$2
          else
            echo "暂不支持:$machine" "===>${machine_type[*]}"
            exit 1
          fi
          shift 2
        ;;
      esac
    ;;
    #打包
    -r | --rootfs)
      rootfs="rootfs"
      shift
    ;;
    #重复运行
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
    #构建
    -b | --build)
      build="build"
      shift
    ;;
    #下载
    --download)
      download="download"
      case "$2" in
        *)
          dev="-b $2"
          shift 2
        ;;
    esac ;;
    -d)
      download="download"
      shift
    ;;
    #帮助
    -h | --help)
      describe="describe"
      probe=""
      shift
    ;;
    # 可变参数
    --)
      error_return=0
      shift 
      break
    ;;
    # 不支持
    -*)
      _optss=(${_optss[*]} $1)
      shift
    break;;
    *)
      shift
    break;;
  esac
done
#状态决策
if [ ${error_return} != 0 ]; then
  echo "please use '  hikrun -h ' to view details "
  exit 0
fi
#剩余参数
script_arg=($@)
self_arg=($@)
# echo  ${@:2} 从第二个开始
echo ${script_arg[*]} " " ${_optss[*]}

#函数定义和注册
source ${HIK_SCRIPT_TOP_DIR}/function.sh
# 函数执行
for func in ${run_func[*]}
do
  # echo $func ${@:1}
  if [ "$(type -t $func)" = "function" ] ; then
    # echo $func ${@:1}
    $func ${@:2} ${_optss[*]}
    unset $func
  fi
done
unset db
