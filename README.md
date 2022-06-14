# script

linux脚本管理

## 功能
- [ ] 补全
- [ ] 功能拆分
- [ ] 安装 可自定义模块名,如./src/tools/install.sh hik
### todo

- [ ] 添加修改功能  用提示方式重新赋值到终端
- [X] add 添加词条
- [X] rm 删除  
    - [X]支持 1:4 区间 
    - [X]不连续 1 4 5 
    - [ ]时间  
- [ ] 补全
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
### cd
- [X] 绝对和相对路径
- [ ] 记录路径 
### 脚本管理
- [X] 快速打开readme
- [ ] 构建脚本
- [ ] 添加脚本
- [ ] 删除脚本
## bug

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