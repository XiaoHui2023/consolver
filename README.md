# consolver

`consolver` 是一个 Python 本地命令行工具。它读取 SMT-LIB `.smt2` 文件，调用 Z3 求解，并把 `sat`、`unsat`、`unknown` 写成稳定的 JSON、YAML 或文本结果。

默认输出 JSON，便于后续脚本继续处理；指定模板时，统一模型会交给 Jinja2 渲染为目标文本。

## 项目结构

```text
src/
  __main__.py              # CLI 入口（python src）
  input.py                 # 读取输入文件
  solve.py                 # 调用 Z3
  model.py                 # 统一模型表示
  output.py                # JSON、YAML、文本输出
  template.py              # 文本模板渲染
tests/
  test_main.py
example/
  sat.smt2 / unsat.smt2 / bv.smt2
  model.txt.j2
  __main__.py              # 线性演示入口
```

## 命令行参数

入口命令：

```bash
python src solve input.smt2 -o model.json
python src solve --input-text "(check-sat)"
```

| 长参数 | 短参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `input` | | 文件路径 | | | `.smt2` 输入文件；与 `--input-text` 二选一 |
| `--input-text` | | 字符串 | | | SMT-LIB 输入文本；与 `input` 二选一 |
| `--output` | `-o` | 文件路径 | | | 写入结果文件 |
| `--format` | | `json` / `yaml` / `text` | | `json` | 未指定模板时使用 |
| `--timeout-ms` | | 整数 | | | Z3 求解超时 |
| `--template` | | 文件路径 | | | Jinja2 文本模板 |
| `--help` | `-h` | | | | 显示帮助并退出 |

未指定输出文件时，结果打印到控制台。指定输出文件时，控制台只打印求解状态和输出路径。

## 输出格式

`sat` 输出包含模型：

```json
{
  "status": "sat",
  "model": {
    "a": 7,
    "b": 5
  }
}
```

`unsat` 输出空模型：

```json
{
  "status": "unsat",
  "model": {}
}
```

`unknown` 输出保留原因：

```json
{
  "status": "unknown",
  "reason": "timeout",
  "model": {}
}
```

位向量值保留整数值、十六进制文本和位宽：

```json
{
  "value": 15,
  "hex": "0x0f",
  "width": 8
}
```

## 演示

仓库根目录执行 **`example.bat`** 或 **`example.sh`**，按顺序演示 `sat` / `unsat`、位向量、YAML 与 Jinja2 模板输出。样例文件与生成物说明见 **`example/README.md`**。

## 依赖

核心依赖：

- `z3-solver`

可选依赖：

- `PyYAML`：输出 YAML。
- `Jinja2`：按模板生成目标文件。

## 打包

仓库根执行 **`tools\pack.bat`**（Windows）或 **`./tools/pack.sh`**（Linux / Git Bash），生成：

- `dist/consolver` 或 `dist/consolver.exe`：单文件可执行体
- `dist/consolver-<version>-<platform>.zip` 或 `.tar.gz`：含 README 的发布压缩包

推送到 `main` 后，GitHub Actions **Release** workflow 会自动构建并更新同名 Release 附件（滚动发版，版本号见 `pyproject.toml`）。
