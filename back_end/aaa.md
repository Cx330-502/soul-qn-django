@@ -1,549 +0,0 @@
# 后端规范说明

本文档中：

+ **表说明**已停止更新，详细信息详见代码 `Qn\models.py`
+ 所有需要登录的操作，一定要验证 `token` 验证过程绝大多数视图函数的开头就有
+ 后端接受数据全部采用 `json` 方式，即 `body = json.loads(request.body)` ，再从 `body` 中取数据
+ 后端与前端文件交互方式统一为：前端上传文件时发送 `base64` 编码，后端解析后暂存于 `temp` 文件夹并返回 `url` ，前端确认提交后返回 `url` 到后端，将 `temp` 文件夹下内容存到对应位置并存入数据库，然后删除对应 `temp` 下内容。（删除这点暂未实现）

## app说明

user_about 登录注册 组织

mainpage 主页面 查询问卷

edit_qn 编辑问卷

analyse_qn 分析问卷

answer_qn 回答问卷

Qn 模型存储 (所有表都存在Qn.models下)

## 表说明

### 一览

1. 用户(**id**，用户名，密码，邮箱)
2. 组织(**id**，组织名)
3. 问卷(**id**，问卷名，种类，问卷权限，问卷是否公开，收集数量，状态，发布时间，截止时间，限时开始，作答时间，问卷密码，标题，说明)
4. 组织2用户(*组织id*，*用户id*，状态)
5. 用户2创建问卷(*用户id*，*问卷id*)
6. 组织2创建问卷(*组织id*，*问卷id*，是否必答)
7. 题目(**id**，类型，描述，*问卷id*，是否必答，题面，宽度，顺序，是否换行，分数，内容1（选择题的选项），内容2（可以是阅读题的文本），视频，图片，答案1，答案2)
8. 回答(**回答id**，*问卷id*，*答卷者id*，回答时间(提交时间)，用时，分数，状态)
9. 答案(*回答id*，*题号id*，答案，答案2，答案3，答案4，答案5，得分)

| 编号 | 表名                                 | 表功能说明         |
| ---- | ------------------------------------ | ------------------ |
| 1    | Qn_user                              | 用户详细信息表     |
| 2    | Qn_organization                      | 组织详细信息表     |
| 3    | Qn_organization_2_user               | 用户组织关系表     |
| 4    | Qn_questionnaire                     | 问卷详细信息表     |
| 5    | Qn_question                          | 问卷题目详细信息表 |
| 6    | Qn_user_create_questionnaire         | 用户创建问卷关系表 |
| 7    | Qn_organization_create_questionnaire | 组织创建问卷关系表 |
| 8    | Qn_answer_sheet                      | 答卷详细信息表     |
| 9    | Qn_question_answer                   | 每题回答详细信息表 |

### 细览

#### 1. 用户：User

1. **id**

2. 用户名：username

   ```python
   CharField("用户名", max_length=100)
   ```

3. 密码：password

   ```python
   CharField("密码", max_length=20)
   ```

4. 邮箱：email

   ```python
   EmailField("邮箱")
   ```

#### 2. 组织：Organization

1. **id**

2. 组织名：name

   ```python
   CharField("组织名", max_length=100)
   ```

#### 3. 问卷：Questionnaire

1. **id**

2. 问卷名：name

   ```python
   CharField("问卷名", max_length=100)
   ```

3. 种类：type

   ```python
   # 问卷类型，0表示普通，1表示考试
   models.IntegerField("问卷类型")
   ```

4. 是否公开：public

   ```python
   # 问卷是否公开，false表示不公开，true表示公开
   models.BooleanField("问卷是否公开")
   ```

5. 问卷权限：permission

   ```python
   # 问卷权限 0表示不需要登录 1表示需要登录 2表示需要登录但匿名 3表示仅组织内可填写 4表示仅组织内可填写但匿名
   models.IntegerField("问卷权限")
   ```

6. 收集数量：collection_num

   ```python
   IntegerField("问卷收集人数")
   ```

7. 状态：state

   ```python
   IntegerField("问卷状态")
   # 0表示审核中,1表示已发布,-1表示发布失败,2表示尚未开始,-2表示已结束
   ```

8. 发布时间：release_time

   ```python
   DateTimeField("问卷发布时间")
   ```

9. 截止时间：finish_time

   ```python
   DateTimeField("问卷截止时间")
   ```

10. 限时开始：start_time

   ```python
   DateTimeField("问卷开始时间")
   ```

11. 作答时间：duration

    ```python
    IntegerField("问卷持续时间")  # 单位为秒
    ```

12. 问卷密码：password

    ```python
    CharField("问卷密码", max_length=20)
    ```

13. 标题：title

    ```python
    CharField("问卷标题", max_length=100)
    ```

14. 说明：description

    ```python
    CharField("问卷描述", max_length=100)
    ```

#### 4. 组织2用户：Organization_2_User

1. *组织id*：organization_id

   ```python
   ForeignKey(Organization, on_delete=models.CASCADE)
   ```

2. *用户id*：user_id

   ```python
   ForeignKey(User, on_delete=models.CASCADE)
   ```

3. 状态：state

   ```python
   IntegerField("用户在组织中的状态")  
   # 0表示审核中,1表示已通过,-1表示拒绝,2表示可发布一次问卷,3表示可发布多次问卷,4表示可审核且可发布多次问卷
   ```

#### 5. 用户2创建问卷：User_create_Questionnaire

1. *用户id*：user_id

   ```python
   ForeignKey(User, on_delete=models.CASCADE)
   ```

2. *问卷id*：questionnaire_id

   ```python
   ForeignKey(Questionnaire, on_delete=models.CASCADE)
   ```

#### 6. 组织2创建问卷：Organization_create_Questionnaire

1. *组织id*：organization_id

   ```python
   ForeignKey(Organization, on_delete=models.CASCADE)
   ```

2. *问卷id*：questionnaire_id

   ```python
   ForeignKey(Questionnaire, on_delete=models.CASCADE)
   ```

3. 是否必答：necessary

   ```python
   BooleanField("问卷是否必填")  # True表示必填,False表示非必填
   ```

#### 7. 题目：Question

1. **id**

2. 类型：type

   ```python
   # 1表示单选,2表示多选,3表示文本,4表示文件
   # 5表示图片单选,6表示图片多选,7表示图片文本,8表示图片文件
   # 9表示视频单选,10表示视频多选,11表示视频文本,12表示视频文件
   IntegerField("问题类型")
   ```

3. 描述：description

   ```python
   CharField("问题描述", max_length=200)
   ```

4. *问卷id*：questionnaire_id

   ```python
   ForeignKey(Questionnaire, on_delete=models.CASCADE)
   ```

5. 是否必答：necessary

   ```python
   BooleanField("问题是否必答")  # True表示必答,False表示非必答
   ```

6. 题面：surface

   ```python
   CharField("问题表面", max_length=200)
   ```

7. 宽度：width

   ```python
   IntegerField("问题宽度")
   ```

8. 顺序：order

   ```python
   IntegerField("问题顺序")
   ```

9. 是否换行：change_line

   ```python
   IntegerField("问题是否换行")  # 0表示不换行,1表示换行
   ```

10. 分数：score

    ```python
    IntegerField("问题分数")
    ```

11. 内容1：content1

    ```python
    CharField("问题内容1", max_length=400)  # 选择题选项 以 "===" 分割
    ```

12. 内容2：content2

    ```python
    TextField("问题内容2")  # 文本题阅读材料
    ```

13. 问题视频：video

    ```python
    FileField("问题视频")
    ```

14. 问题图片：image

    ```python
    ImageField("问题图片")
    ```

15. 问题答案1：answer1

    ```python
    CharField("问题答案1", max_length=200)  # 选择题答案 以 "===" 分割
    ```

16. 问题答案2：answer2

    ```python
    TextField("问题答案2")  # 文本题答案
    ```

#### 8. 答卷：Answer_sheet

1. **id**

2. *问卷id*：questionnaire_id

   ```python
   ForeignKey(Questionnaire, on_delete=models.CASCADE)
   ```

3. *答卷者id*：answerer_id

   ```python
   ForeignKey(User, on_delete=models.CASCADE)
   ```

4. 回答时间(提交时间)：submit_time

   ```python
   DateTimeField("问卷提交时间")
   ```

5. 用时：duration

   ```python
   IntegerField("问卷持续时间")  # 单位为秒
   ```

6. 分数：score

   ```python
   IntegerField("问卷分数")
   ```

7. 状态：state

   ```python
   IntegerField("问卷状态")  # 0表示未完成,1表示已完成,-1表示未提交
   ```

#### 9. 题目回答：Exercise_answer

1. *答卷id*：answer_sheet_id

   ```python
   ForeignKey(Answer_sheet, on_delete=models.CASCADE)
   ```

2. *题号id*：question_id

   ```python
   ForeignKey(Question, on_delete=models.CASCADE)
   ```

3. 答案：answer

   ```python
   CharField("回答", max_length=200)
   ```

4. 答案2：answer2

   ```python
   TextField("回答2")
   ```

5. 答案3：answer3

   ```python
   IntegerField("回答3")
   ```

6. 答案4：answer4

   ```python
   ImageField("回答4")
   ```

7. 答案5：answer5

   ```python
   FileField("回答5")
   ```

8. 得分：score

   ```python
   IntegerField("回答得分")
   ```

## 功能说明(后端)

### 登陆界面

1. 注册（邮箱发送验证码）
2. 登录

### 组织界面

1. 列出所在组织
2. 列出组织内联系人
3. 邀请：
   1. 通过链接
   2. 通过email搜索
   3. 通过username搜索
4. 组织管理：
   1. 通过加入申请
   2. 踢人
   3. 赋予权限
5. 搜索（前端或后端）

### 主界面（工作台）

1. 左侧菜单：

   1. 新建（前端）

   2. 列出个人发布问卷

   3. 列出组织列表

   4. 列出团体发布问卷

   5. 列出回答的问卷

   6. 列出回收站内的问卷

2. 右侧main主体：

   1. 编辑（列出问卷内容）
   2. 删除
   3. 搜索
   4. 排序
   5. 预览
   6. 复制
   7. 开启
   8. 关闭
   9. 导出
   10. 分享
   11. 统计

### 新建

1. 加载模板

### 编辑

1. 退出时提示保存
2. 若是编辑则需要加载之前的问卷

### 回答问卷

1. 退出时状态保存

### 分析问卷

1. 回收时间的图表
2. 具体每一份的预览、回答（判分分析）
3. 每题的统计
4. others

## 功能完成情况说明

|    模块    | 子模块       |              功能               |                             说明                             | 完成情况 |         测试情况         |
| :--------: | ------------ | :-----------------------------: | :----------------------------------------------------------: | :------: | :----------------------: |
|  登陆界面  |              |                                 |                                                              |    √     |                          |
|            |              |              注册               |      有一个发送验证码的过程，并由前端验证验证码是否正确      |  已完成  | 简单测试（不支持QQ邮箱） |
|            |              |              登录               |                      会返回token到前端                       |  已完成  |                          |
|  组织页面  |              |                                 |                                                              |          |                          |
|            |              |            新建组织             |                                                              |  已完成  |                          |
|            |              |          列出所在组织           |                                                              |  已完成  |                          |
|            |              |        列出组织内联系人         |                                                              |  已完成  |                          |
|            |              |           邀请(链接)            |                                                              |          |                          |
|            |              | 邀请(email、username、链接搜索) |                                                              |  已完成  |                          |
|            |              |          列出申请名单           |                                                              |  已完成  |                          |
|            |              |     组织管理(通过加入申请)      |                                                              |  已完成  |                          |
|            |              |              踢人               |                                                              |  已完成  |                          |
|            |              |            赋予权限             |                                                              |  已完成  |                          |
|            |              |              搜索               |                                                              |  已完成  |                          |
|            |              |            解散组织             |                                                              |  已完成  |                          |
|            | 消息页面     |                                 |                                                              |          |                          |
|            |              |          列出消息列表           |                                                              |  已完成  |                          |
|            |              |            删除消息             |                                                              |  已完成  |                          |
|            |              |         同意或拒绝邀请          |                                                              |  已完成  |                          |
|   主界面   |              |                                 |                                                              |          |                          |
|            | 左侧菜单     |                                 |                                                              |          |                          |
|            |              |          新建（前端）           | 新建然后出模板（如果信息中有organization_id则时组织创建问卷） |  已完成  |                          |
|            |              |        列出个人发布问卷         |                                                              |  已完成  |                          |
|            |              |          列出组织列表           |                                                              |  已完成  |                          |
|            |              |        列出团体发布问卷         |                                                              |  已完成  |                          |
|            |              |         列出回答的问卷          |                                                              |  已完成  |                          |
|            |              |       列出回收站内的问卷        |                                                              |  已完成  |                          |
|            | 右侧main主体 |                                 |                                                              |          |                          |
|            |              |      编辑（列出问卷内容）       |                                                              |  已完成  |                          |
|            |              |              删除               |                                                              |  已完成  |                          |
|            |              |              搜索               |                                                              |  已完成  |                          |
|            |              |              排序               |                                                              |  已完成  |                          |
|            |              |              预览               |                           前端完成                           |  已完成  |                          |
|            |              |              复制               |                                                              |  已完成  |                          |
|            |              |              开启               |                                                              |  已完成  |                          |
|            |              |              关闭               |                                                              |  已完成  |                          |
|            |              |              导出               |                    由分析问卷相关接口完成                    |          |                          |
|            |              |              分享               |                     链接和二维码两种方式                     |  已完成  |                          |
|            |              |              统计               |                      前端跳转到分析页面                      |          |                          |
|    新建    |              |                                 |                                                              |          |                          |
|            |              |            加载模板             |                                                              |  已完成  |                          |
|   *编辑*   |              |                                 |                                                              |          |                          |
|            |              |          文件上传接口           |                                                              |  已完成  |                          |
|            |              |         退出时提示保存          |                                                              |  已完成  |                          |
|            |              |  若是编辑则需要加载之前的问卷   |                                                              |  已完成  |                          |
| *回答问卷* |              |                                 |                                                              |          |                          |
|            |              |         回答时加载答案          |                           校验权限                           |  已完成  |                          |
|            |              |          文件提交接口           |                                                              |  已完成  |                          |
|            |              |         退出时状态保存          |                                                              |  已完成  |                          |
|            |              |            提交问卷             |       检查必答题是否回答了。如果是考试类型，则判断分数       |  已完成  |                          |
| *分析问卷* |              |                                 |                                                              |          |                          |
|            |              |   获得问卷相关所有信息给前端    |                                                              |  已完成  |                          |
|            |              |            更新分数             |                                                              |  已完成  |                          |
|            |              |          导出问卷数据           |                                                              |  已完成  |                          |
|            |              |             导出pdf             |                        回收时间的图表                        |          |                          |
|            |              |                                 |              具体每一份的预览、回答（判分分析）              |          |                          |
|            |              |                                 |                          每题的统计                          |          |                          |
|            |              |                                 |                            others                            |          |                          |
|            |              |                                 |                                                              |          |                          |
|            |              |                                 |                                                              |          |                          |
|            |              |                                 |                                                              |          |                          |
|            |              |                                 |                                                              |          |                          |