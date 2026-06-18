#!/usr/bin/env bash
# 统一打包：使用仓库根 .venv，先 PyInstaller（主入口 spec）；Linux 默认 staticx，PACK_LINUX_SKIP_STATICX=1 时跳过。
# 每次 pip 对项目与打包工具 --force-reinstall，避免 .venv 残留旧依赖。
# Windows 仅 PyInstaller（无 staticx）。
#
# 用法（仓库根）：
#   ./tools/pack.sh [src]     Linux / macOS / Git Bash
#   bash tools/pack.sh [src]  同上
# 产物：dist/consolver（Linux）或 dist/consolver.exe（Windows）；
#       另有 dist/consolver-<version>-<platform>.tar.gz 或 .zip（README 见 tools/bundle_release.py）。
# Linux staticx 另需 patchelf；PACK_LINUX_SKIP_STATICX=1 时跳过 staticx。
# 本地 pack 的 Linux ABI 取决于本机 glibc；需在旧系统运行时请在对应环境内打包。
# Windows 批处理见 tools/pack.bat。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TARGET="${1:-src}"

ensure_venv() {
  if [[ -f "$ROOT/.venv/bin/python" ]]; then
    PYTHON_CMD=("$ROOT/.venv/bin/python")
  elif [[ -f "$ROOT/.venv/Scripts/python.exe" ]]; then
    PYTHON_CMD=("$ROOT/.venv/Scripts/python.exe")
  else
    echo "未找到 .venv，正在创建 ..."
    case "$(uname -s 2>/dev/null || true)" in
      MINGW*|MSYS*|CYGWIN*|Windows_NT)
        if command -v py >/dev/null 2>&1; then
          py -3 -m venv "$ROOT/.venv"
        else
          python -m venv "$ROOT/.venv"
        fi
        PYTHON_CMD=("$ROOT/.venv/Scripts/python.exe")
        ;;
      *)
        if ! command -v python3 >/dev/null 2>&1; then
          echo "错误: 需要 python3 以创建 .venv。" >&2
          exit 1
        fi
        python3 -m venv "$ROOT/.venv"
        PYTHON_CMD=("$ROOT/.venv/bin/python")
        ;;
    esac
  fi
  echo "==> 使用虚拟环境: ${PYTHON_CMD[*]} ($("${PYTHON_CMD[@]}" -V 2>/dev/null || true))"
}

apply_staticx_linux() {
  local dist_name="$1"
  local pyi_out="$ROOT/dist/${dist_name}"
  if [[ ! -f "$pyi_out" ]]; then
    return 0
  fi
  if ! command -v patchelf >/dev/null 2>&1; then
    echo "错误: Linux 下 staticx 需要系统命令 patchelf（例如: sudo apt install patchelf）。" >&2
    exit 1
  fi
  "${PYTHON_CMD[@]}" -m pip install -q --upgrade --force-reinstall staticx
  local staticx="$ROOT/.venv/bin/staticx"
  if [[ ! -x "$staticx" ]]; then
    echo "错误: 未找到可执行的 .venv/bin/staticx。" >&2
    exit 1
  fi
  local tmp_out="$ROOT/dist/.${dist_name}-staticx.tmp"
  rm -f "$tmp_out"
  echo "==> staticx: $pyi_out -> $dist_name"
  if ! "$staticx" "$pyi_out" "$tmp_out"; then
    rm -f "$tmp_out"
    echo "==> staticx 失败，重试 staticx --no-compress"
    if ! "$staticx" --no-compress "$pyi_out" "$tmp_out"; then
      echo "错误: staticx 与 staticx --no-compress 均失败；不得跳过 staticx，请检查 patchelf、依赖库与构建日志。" >&2
      exit 1
    fi
  fi
  mv -f "$tmp_out" "$pyi_out"
  chmod +x "$pyi_out"
  echo "完成: $pyi_out（staticx 自解压包；请在目标机实测）"
}

build_cli() {
  local spec="$ROOT/consolver-cli.spec"
  if [[ ! -f "$spec" ]]; then
    echo "错误: 未找到 $spec" >&2
    exit 1
  fi
  echo "==> PyInstaller: $spec"
  "${PYTHON_CMD[@]}" -m PyInstaller --clean --noconfirm "$spec"
  local dist_name="consolver"
  if [[ -f "$ROOT/dist/${dist_name}.exe" ]]; then
    echo "完成: $ROOT/dist/${dist_name}.exe（Windows：无 staticx 步骤）"
    return 0
  fi
  if [[ ! -f "$ROOT/dist/${dist_name}" ]]; then
    echo "错误: 未在 dist 找到 ${dist_name} 或 ${dist_name}.exe。" >&2
    exit 1
  fi
  case "$(uname -s 2>/dev/null || true)" in
    Linux)
      if [[ "${PACK_LINUX_SKIP_STATICX:-}" == "1" ]]; then
        echo "完成: $ROOT/dist/${dist_name}（PACK_LINUX_SKIP_STATICX=1，已显式跳过 staticx）"
      else
        apply_staticx_linux "$dist_name"
      fi
      ;;
    *) echo "完成: $ROOT/dist/${dist_name}（非 Linux，跳过 staticx）" ;;
  esac
}

ensure_venv

"${PYTHON_CMD[@]}" -m pip install -q -U pip setuptools wheel
"${PYTHON_CMD[@]}" -m pip install -q --upgrade --force-reinstall --only-binary=z3-solver -e ".[dev]"
"${PYTHON_CMD[@]}" -m pip install -q --upgrade --force-reinstall "pyinstaller>=6.0"

rm -rf "$ROOT/build" "$ROOT/dist"

case "$TARGET" in
  src|"")
    build_cli
    echo "==> 组装发布压缩包"
    "${PYTHON_CMD[@]}" "$ROOT/tools/bundle_release.py"
    ;;
  *)
    echo "用法: ./tools/pack.sh [src]" >&2
    exit 1
    ;;
esac

echo "PyInstaller 输出目录: $ROOT/dist"
