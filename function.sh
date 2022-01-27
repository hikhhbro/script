if [ -f "${HIK_SCRIPT_TOP_DIR}/company/companyfunc.sh" ];then
source ${HIK_SCRIPT_TOP_DIR}/company/companyfunc.sh
else
_task "没有companyfunc.sh"
fi

run_func=(
  ${machine}_${project}_${download}
  ${machine}_${project}_${prebuilt}
  ${machine}_${project}_${build}
  ${machine}_${project}_${rootfs}
  ${rerun}_${script}
  ${run_adb}
)
run_adb_func() {
  _func
  _task adb root
  _task adb remount
  _task adb disable-verity
  _task adb shell
}
#执行外部脚本
rerun_script() {
  if [ ! -f "${script_arg[0]}" ];then
    if [ ! -f "${HIK_SCRIPT_TOP_DIR}/script/${script_arg[0]}" ];then
        _func "${script_arg[0]} 不存在"
        exit 0
    fi
    script_arg[0]="${HIK_SCRIPT_TOP_DIR}/script/${script_arg[0]}"
  fi
  for i in $(seq 1 $rerun_j)
  do
    _func ". ""${script_arg[*]}"  "第${i}次执行开始 === 剩余:$(expr $rerun_j - $i)次"
    $(echo ". ""${script_arg[*]}")
  done
}

