# Jenkins 构建提交人信息获取指南

## 功能概述

本功能可以获取 Jenkins 构建的代码提交人信息，包括提交人姓名和邮箱地址。支持两种获取方式：

1. **Jenkins API 方式**：通过 Jenkins REST API 获取变更集信息
2. **日志解析方式**：从 Jenkins 控制台日志中解析提交人信息

## 获取方式详解

### 1. Jenkins API 方式（推荐）

**API 端点**：
```
GET {JENKINS_URL}/job/{job_name}/{build_number}/api/json?tree=changeSets[*[*[*]]]
```

**返回数据结构**：
```json
{
  "changeSets": [
    {
      "items": [
        {
          "author": {
            "fullName": "张三",
            "email": "zhangsan@example.com"
          },
          "msg": "feat: 新增功能"
        }
      ]
    }
  ]
}
```

**优点**：
- 数据准确，直接从 Jenkins 内部获取
- 包含完整的提交人信息（姓名、邮箱）
- 性能较好

**缺点**：
- 需要 Jenkins 配置了版本控制系统（如 Git）
- 某些 Jenkins 配置可能不返回完整信息

### 2. 日志解析方式（备用）

**解析的日志格式**：
```
Author: 张三 <zhangsan@example.com>
commit abc123 Author: 李四 <lisi@example.com>
作者: 王五 <wangwu@example.com>
```

**支持的正则表达式**：
- `Author:\s*([^<\n]+?)\s*<([^>\n]+)>` - 标准格式
- `Author:\s*([^<\n]+)` - 只有姓名
- `commit\s+\w+\s+Author:\s*([^<\n]+?)\s*<([^>\n]+)>` - 带 commit hash
- `作者:\s*([^<\n]+?)\s*<([^>\n]+)>` - 中文格式

**优点**：
- 兼容性好，适用于各种 Jenkins 配置
- 可以解析多种日志格式

**缺点**：
- 依赖日志格式，可能解析失败
- 需要下载完整的控制台日志

## 使用方法

### 在代码中调用

```python
from ui.components.ui_jenkins_builder import get_commit_author

# 获取提交人信息
authors = get_commit_author("project-name", 123)

# 处理结果
if authors:
    for author in authors:
        print(f"提交人: {author['name']}")
        if author['email']:
            print(f"邮箱: {author['email']}")
else:
    print("未获取到提交人信息")
```

### 测试脚本

运行测试脚本验证功能：

```bash
python test/test_commit_author.py
```

**注意**：请先修改测试脚本中的项目名和构建号。

## 企业微信通知格式

获取到提交人信息后，会在企业微信通知中显示：

```markdown
🟢成功项目：
- [项目A]
    - 提交人：张三, 李四
    - 代码提交说明：feat: 新增功能
    - 代码提交说明：fix: 修复bug
```

## 配置要求

### Jenkins 配置

1. **版本控制系统**：确保 Jenkins 项目配置了 Git 等版本控制系统
2. **权限设置**：确保 API Token 有读取项目信息的权限
3. **插件安装**：确保安装了 Git 插件

### 代码配置

确保以下配置正确：

```python
JENKINS_URL = 'http://your-jenkins-url/'
JENKINS_USER = 'your-username'
JENKINS_TOKEN = 'your-api-token'
```

## 故障排除

### 1. API 获取失败

**可能原因**：
- Jenkins 未配置版本控制系统
- API Token 权限不足
- 项目未关联 Git 仓库

**解决方案**：
- 检查 Jenkins 项目配置
- 验证 API Token 权限
- 查看 Jenkins 日志

### 2. 日志解析失败

**可能原因**：
- 日志格式不匹配
- 控制台日志为空
- 网络连接问题

**解决方案**：
- 检查 Jenkins 控制台日志格式
- 手动查看日志内容
- 检查网络连接

### 3. 获取不到提交人信息

**可能原因**：
- 构建未触发代码变更
- 提交信息为空
- Jenkins 配置问题

**解决方案**：
- 确认构建包含代码变更
- 检查 Git 提交信息
- 查看 Jenkins 构建详情

## 扩展功能

### 1. 支持更多版本控制系统

可以扩展支持 SVN、Mercurial 等其他版本控制系统：

```python
def get_commit_author_svn(job_name, build_number):
    # SVN 特定的获取逻辑
    pass

def get_commit_author_hg(job_name, build_number):
    # Mercurial 特定的获取逻辑
    pass
```

### 2. 缓存机制

对于频繁查询的项目，可以添加缓存机制：

```python
import functools

@functools.lru_cache(maxsize=100)
def get_commit_author_cached(job_name, build_number):
    return get_commit_author(job_name, build_number)
```

### 3. 批量获取

对于多个构建，可以批量获取提交人信息：

```python
def get_commit_authors_batch(builds):
    """批量获取多个构建的提交人信息"""
    results = {}
    for job_name, build_number in builds:
        results[(job_name, build_number)] = get_commit_author(job_name, build_number)
    return results
```

## 注意事项

1. **性能考虑**：日志解析方式需要下载完整日志，对于大型项目可能较慢
2. **数据准确性**：API 方式更准确，建议优先使用
3. **错误处理**：代码中已包含完善的错误处理机制
4. **权限要求**：确保 API Token 有足够的权限读取项目信息

## 更新日志

- **v1.0**：初始版本，支持基本的提交人信息获取
- **v1.1**：添加日志解析作为备用方案
- **v1.2**：优化错误处理和性能
- **v1.3**：添加企业微信通知集成 