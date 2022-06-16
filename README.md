# script

linux脚本管理
## 使用说明
### 安装
1. 进入下载或解压目录,如 cd /home/hik/private/script
2. ./src/tools/install.sh
3. 输入密码
4. 输入自定义工具名,回车默认为hikrun
5. 输入工具安装路径,回车默认为当前下载或者解压目录
6. source ~/.bashrc

**例子**
```
hik@hik:~/private/script$ ./src/tools/install.sh 
已安装过/home/hik/private/script 正在卸载 .... 
Running_task => (sudo rm /usr/local/bin/hikrun): 
[sudo] password for hik: 
Running_task => (sudo rm /etc/bash_completion.d/hikrun_prompt): 
请输入工具名称[hikrun]: 
请输入工具安装路径[/home/hik/private/script]: 
正在安装
Running_task => (source /home/hik/.bashrc): 
Running_task => (sudo mv /home/hik/private/script/hikrun /usr/local/bin/hikrun): 
Running_task => (sudo chmod 755 /usr/local/bin/hikrun): 
Running_task => (sudo mv hikrun_prompt /etc/bash_completion.d/hikrun_prompt): 
Running_task => (sudo chmod 755 /etc/bash_completion.d/hikrun_prompt): 
Running_task => (source /home/hik/.bashrc): 
---安装完成---输入任意键结束------
```
### 卸载
${SCRIPT_TOP_DIR}/src/tools/uninstall.sh 

**例子**
```
hik@hik:~/private/script$ ${SCRIPT_TOP_DIR}/src/tools/uninstall.sh
Running_task => (sudo rm /usr/local/bin/hikrun): 
Running_task => (sudo rm /etc/bash_completion.d/hikrun_prompt): 
```

## 功能
- [X] 补全
- [X] 功能拆分
- [X] 安装时工具源码目录和data目录做区分,如hikrun/data 和hikrun/src
- [X] 安装 可自定义模块名,如./src/tools/install.sh hik
### todo

- [ ] 添加修改功能  用提示方式重新赋值到终端
- [X] add 添加词条
- [X] rm 删除  
    - [X]支持 1:4 区间 
    - [X]不连续 1 4 5 
    - [ ]时间  
- [X] 补全
### adb
- [X] ls 
- [X] pwd
- [X] cd
- [X] mv
- [X] code
- [X] ls  补全
- [X] cd 补全
- [X] mv 补全
- [X] code 补全
- [X] 关闭和打开屏幕
### cd
- [X] 绝对和相对路径
- [ ] 记录路径 
### 脚本管理
- [X] 快速打开readme
- [ ] 构建脚本
- [ ] 添加脚本
- [ ] 删除脚本
- [ ] 公司仓库初始化
## 安装和卸载
- [X] 自定义工具名
## bug

- [ ] cd 不能补全当前目录
- [ ] 同级别命令出现两次不报错
- [ ] hikrun adb 不能进shell
## 设计
### 编译

### 补全
#### 优先级: 
模板 > 代码
#### 模板
1. 添加接口  --completion-add ,  --completion-add={opt} , --completion-add={opt:help}
  * --completion-add 添加当前选项  如 hikrun todo  show --completion-add   则为todo 添加show
  * --completion-add={opt}  例 hikrun todo --completion-add={show,rm}  为todo 添加show 和rm
  * --completion-add={opt:help}  例 hikrun todo --completion-add={show:显示,rm:删除}  为todo 添加show 和rm, show 帮助信息为 显示 , hikrun todo show -h   -> 显示
2. 模板文件 .complete.json
  * 格式 使用前缀树来存储,用嵌套字典实现
  ```
{
  "deny": [
    {},
    "held"
  ]
}
  ```
#### 源码
1. 私有接口 __hikrun_xxx_subcommand(opt:list) 实现源码中补全
2. 公有接口 __hikrun(opt:list) 优先查找模板并返回,若没有则调用源码接口