# 示例

一键运行仓库根目录的 **`example.bat`**（Windows）或 **`example.sh`**（Linux / macOS）。

## 输入

| 文件 | 说明 |
| --- | --- |
| `sat.smt2` | 整数线性约束，结果为 `sat` |
| `unsat.smt2` | 矛盾约束，结果为 `unsat` |
| `bv.smt2` | 8 位向量赋值 |
| `model.txt.j2` | Jinja2 文本模板 |

## 输出

运行后在 `output/` 生成：

| 文件 | 说明 |
| --- | --- |
| `unsat.json` | `unsat` 的 JSON 结果 |
| `sat.yaml` | `sat` 的 YAML 结果 |
| `from_template.txt` | 模板渲染文本 |

`sat` 的 JSON 直接打印到控制台。
