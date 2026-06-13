# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 规格：主入口（src）onefile 单可执行文件。

构建入口：仓库根执行 ./tools/pack.sh 或 tools\\pack.bat（内部用 .venv 跑 PyInstaller；Linux 上再跑 staticx）。
"""
from __future__ import annotations

from pathlib import Path

from PyInstaller.building.api import EXE, PYZ
from PyInstaller.building.build_main import Analysis

block_cipher = None


def _repo_root_from_spec() -> Path:
    """SPECPATH 常为相对路径；从 spec 所在目录与 cwd 双向向上找含 pyproject.toml 的仓库根。"""
    spec = Path(SPECPATH).resolve()
    seeds = [spec.parent]
    try:
        seeds.append(Path.cwd().resolve())
    except OSError:
        pass
    for seed in seeds:
        for base in [seed, *seed.parents]:
            if (base / "pyproject.toml").is_file() and (base / "src" / "__main__.py").is_file():
                return base
    return spec.parent


repo_root = _repo_root_from_spec()
entry = repo_root / "src" / "__main__.py"

import z3 as _z3_pkg

_z3_lib_dir = Path(_z3_pkg.__file__).resolve().parent / "lib"
_z3_binaries = [
    (str(path), "z3/lib")
    for path in sorted(_z3_lib_dir.iterdir())
    if path.is_file() and path.suffix in {".dll", ".so", ".dylib"}
]

a = Analysis(
    [str(entry)],
    pathex=[str(repo_root / "src")],
    binaries=_z3_binaries,
    datas=[],
    hiddenimports=[
        "z3",
        "yaml",
        "jinja2",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(repo_root / "tools" / "pyi_rth_z3.py")],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="consolver",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
