# kanmoecounter

这是一个基于python3的爬虫计票器。

由于规则的不同，以及非官方性，本计票器可能会出现**记错**现象，所以不要依赖计票器。

为了~~几乎没有的~~严谨性，只有匹配了所有字符的评论会被计入。

# 依赖库：

requests，bs4

Windows用户通过python官网安装的请使用pip install requests bs4来安装。

若是使用anaconda或者其他包管理器请自行搜索安装依赖库方法。



# 使用方法：

## 0、安装python3并按上文安装依赖库（推荐）或者运行~~问题很多的~~releases中的exe文件

**把exe文件和本仓库中的其他文件放在同一目录！！！**

**把exe文件和本仓库中的其他文件放在同一目录！！！**

**把exe文件和本仓库中的其他文件放在同一目录！！！**

## 1、将整个仓库克隆或者下载为zip然后解压

## 2、运行ngacreeper.py

## 3、关于Cookie：使用了游客的Cookie，使用版主的可能可以抓到匿名用户的信息。

## 4、关于计票命令：

**save:** 把未完成的计票工作以文件形式保存在工作目录下，当程序重启时会自动检测上次的进度文件。不可添加参数。

**addig:** 添加一条忽略规则，可以是正则表达式或者是普通的字符串。添加得不严谨的话可能会造成漏票。使用格式为 *addig 类型 查找字符或表达式*

例子：addig n awsl

例子：addig re \\\\(.\*?\\\\).\*?

**addtr:** 添加一条转义规则，可以是正则表达式或者是普通的字符串。添加得不严谨的话可能会造成串票，所以请不要添加*替换前字串*过短的转义规则。使用格式为 *addig 类型 需要替换的字符或表达式 替换后的字符串*

例子：addtr n 海妈 海伦娜

**ld:** 重载规则字典，注意没有运行ld前是无法正常自动记票的，包括pass、manu、auto指令的运行。不可添加参数。

**pass:** 人工处理当前最近一条无法自动处理的投票评论，执行后提供二级选项但是不会影响目前的规则。不可添加参数。

**manu:** 调试用指令，输出最近一条无法自动处理的投票评论匹配规则后剩余的字符串。对于修改规则有帮助。不可添加参数。

**auto:** 使用现有的规则进行计票。不可添加参数。

**ato:** 输出剩余无法自动处理的投票评论楼层数。不可添加参数。

**show:** 输出最近几条（默认5条）无法处理的楼层内容，可以指定参数以自定义要输出的楼层数。

例子：show 11

**score:** 输出目前参赛舰娘的得票数。

**dig:** 删除掉一条忽略规则，格式与addig相似，但是只支持下标。请配合ld使用。

例子：dig n 1

*删掉忽略字典通常模式的第二条规则（下标从0开始）*

**dtr:** 与dig类似，删除转义字典的规则。

**brute:** 用于快速估票或调试的一条命令，暴力计数所剩的所有评论发言，忽略未匹配的部分。

## 退出请直接CTRL+C或者红叉叉。

# 什么？你跟我说你想手机用？

# 如果你能忍受目前阶段的巨量BUG的话，请访问[Tenpu](http://tenpu.cf) 体验
