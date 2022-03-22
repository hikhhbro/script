source ${HIK_SCRIPT_TOP_DIR}/base.sh
# 输入
ARGS=$(getopt -o :hbrdpB:C: --long help,rerun:,build,rootfs,script:,download:,code:,rm: -n 'hikrun' -- "$@")
error_return=$?

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
    #下载重包或者使用cache
    -p)
      prebuilt="prebuilt"
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
    #   usage
      shift
    ;;
    # 可变参数
    --)
      error_return=0
      shift 
      break
    ;;
    # 不支持
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
script_arg=$@
self_arg=$@
#函数定义和注册
source ${HIK_SCRIPT_TOP_DIR}/function.sh
# 函数执行
exit_user=""
for func in ${run_func[*]}
do
  # echo $func
  if [ "$(type -t $func)" = "function" ] ; then
    $func
    exit_user="yes"
  fi
done
if [[ "${exit_user}" == "yes" ]];then exit 0;fi

if [ ! -f "${script_arg[0]}" ];then
    if [ ! -f "${HIK_SCRIPT_TOP_DIR}/script/${script_arg[0]}" ];then
        _func "${script_arg[0]} 不存在"
        exit 0
    fi
    script_arg[0]="${HIK_SCRIPT_TOP_DIR}/script/${script_arg[0]}"
fi
$(echo ". ""${script_arg[*]}")