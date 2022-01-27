source ${HIK_SCRIPT_TOP_DIR}/base.sh
usage() {
  echo -e "Usage: ./$(basename $0) [-t value] [-t value] [-h] [value]\n"
  echo "-h           help"
}
#创建脚本
touch_script() {
  _func
  if [ -f "${HIK_SCRIPT_TOP_DIR}/$1" ];then
      code ${HIK_SCRIPT_TOP_DIR}/$1
      exit 0
  fi
  if [ ! -f "${HIK_SCRIPT_TOP_DIR}/script/$1" ];then
    echo "#!/bin/bash" >> ${HIK_SCRIPT_TOP_DIR}/script/$1
    echo ". ${HIK_SCRIPT_TOP_DIR}/base.sh" >> ${HIK_SCRIPT_TOP_DIR}/script/$1
    chmod 755 ${HIK_SCRIPT_TOP_DIR}/script/$1
  fi
  code ${HIK_SCRIPT_TOP_DIR}/script/$1
}

# 输入
ARGS=$(getopt -o hbrdpB:C: --long help,rerun:,build,rootfs,script:,download:,code: -n 'hikrun' -- "$@")
if [ $? != 0 ]; then
  echo "please use '  hikrun -h ' to view details "
fi
eval set -- "${ARGS}"
while true; do
  case "$1" in
    #重复运行
    --code)
      case "$2" in
        *)
          touch_script $2
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
      usage
      shift
    exit 1 ;;
    # 可变参数
    --)
      shift 1
      for i in $*  #"$*" 不能判断
      do
        if [[ ${project_type[@]/$i/} != ${project_type[@]} ]];then
          project=(${project[*]} $i)
          machine=${machine_type[0]}
          if [[  ${#project[@]} > 1 ]];then
            echo "不支持多个工程: ${project[*]}"
            exit 1
          fi
        else
          if [[ "$build" != "" ]];then
            out_target=(${out_target[*]} $i)
          fi
          if [[  ${#script_arg[@]} == 1 ]];then
            script_arg=(${script_arg[*]} $i)
          fi
          if [[ "$i" == "adb" ]];then
            run_adb="run_"$i"_func"
          fi
        fi
      done
    ;;
    # 不支持
    *)
      shift
    break;;
  esac
done


#函数定义和注册
source ${HIK_SCRIPT_TOP_DIR}/function.sh
# 函数执行
for func in ${run_func[*]}
do
  # echo $func
  if [ "$(type -t $func)" = "function" ] ; then
    $func
  fi
done

