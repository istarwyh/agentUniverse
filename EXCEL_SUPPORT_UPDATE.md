# Excel文件读取支持更新

## 更新概述

本次更新为AgentUniverse框架添加了完整的Excel文件读取支持，现在框架可以处理以下Office文档格式：

- ✅ **Word文档** (.docx) - 已支持
- ✅ **PowerPoint文档** (.pptx) - 已支持  
- ✅ **Excel文档** (.xlsx) - **新增支持**
- ✅ **CSV文件** (.csv) - 已支持
- ✅ **PDF文档** (.pdf) - 已支持

## 新增功能

### 1. Excel读取器 (XlsxReader)

**文件位置**: `agentuniverse/agent/action/knowledge/reader/file/xlsx_reader.py`

**主要特性**:
- 支持读取Excel文件的所有工作表
- 自动处理不同数据类型（文本、数字、日期等）
- 为每个工作表生成独立的文档对象
- 包含丰富的元数据信息（工作表名、行列数等）
- 支持空单元格和空行的智能过滤

**使用方法**:
```python
from agentuniverse.agent.action.knowledge.reader.file.xlsx_reader import XlsxReader

# 直接使用Excel读取器
reader = XlsxReader()
documents = reader.load_data('example.xlsx')

# 或通过文件读取器自动识别
from agentuniverse.agent.action.knowledge.reader.file.file_reader import FileReader
file_reader = FileReader()
documents = file_reader.load_data(file_paths=[Path('example.xlsx')])
```

### 2. 配置文件

**文件位置**: `agentuniverse/agent/action/knowledge/reader/file/xlsx_reader.yaml`

包含Excel读取器的配置信息，支持框架的组件管理系统。

### 3. 自动文件类型识别

更新了 `FileReader` 类，现在可以自动识别并处理Excel文件：

```python
DEFAULT_FILE_READERS = {
    ".pdf": PdfReader,
    ".docx": DocxReader,
    ".pptx": PptxReader,
    ".xlsx": XlsxReader,  # 新增
}
```

### 4. 完整的测试覆盖

**文件位置**: `tests/test_agentuniverse/unit/agent/action/knowledge/reader/file/test_xlsx_reader.py`

包含全面的单元测试，覆盖：
- 基本读取功能
- 多工作表处理
- 错误处理
- 元数据验证
- 边界情况测试

### 5. 演示示例

**文件位置**: `examples/sample_apps/excel_reader_demo.py`

提供了完整的使用示例，展示如何：
- 创建示例Excel文件
- 使用Excel读取器读取数据
- 处理多工作表文档
- 查看文档元数据

## 依赖要求

使用Excel读取功能需要安装以下依赖：

```bash
pip install openpyxl
```

## 使用示例

### 基本用法

```python
from agentuniverse.agent.action.knowledge.reader.file.xlsx_reader import XlsxReader

# 创建读取器
reader = XlsxReader()

# 读取Excel文件
documents = reader.load_data('data.xlsx')

# 处理结果
for doc in documents:
    print(f"工作表: {doc.metadata['sheet_name']}")
    print(f"内容: {doc.text[:100]}...")
    print(f"行列数: {doc.metadata['max_row']} x {doc.metadata['max_col']}")
```

### 在知识库中使用

```python
from agentuniverse.agent.action.knowledge.knowledge import Knowledge

# 创建知识库实例
knowledge = Knowledge()

# 添加Excel文件到知识库
knowledge.add_docs(file_paths=['report.xlsx'])

# 查询知识库
results = knowledge.search('销售数据')
```

## 技术细节

### 数据格式

Excel数据在读取后会被转换为以下格式：
- 每行数据用 ` | ` 分隔
- 每行之间用换行符分隔
- 空行和空单元格会被自动过滤

### 元数据信息

每个文档包含以下元数据：
- `file_name`: 文件名
- `sheet_name`: 工作表名称
- `max_row`: 最大行数
- `max_col`: 最大列数
- 用户自定义的额外信息

### 错误处理

- 自动检测 `openpyxl` 依赖是否安装
- 优雅处理空工作表和空文件
- 提供详细的错误信息

## 兼容性

- Python 3.10+
- 支持所有标准Excel格式 (.xlsx)
- 与现有知识库系统完全兼容
- 支持所有存储后端（SQLite、Milvus、Chroma等）

## 未来计划

- [ ] 支持旧版Excel格式 (.xls)
- [ ] 添加Excel文件写入功能
- [ ] 支持Excel图表和图片提取
- [ ] 添加数据验证和清洗功能

---

**更新时间**: 2024年12月19日  
**版本**: v0.0.18+  
**贡献者**: Assistant
