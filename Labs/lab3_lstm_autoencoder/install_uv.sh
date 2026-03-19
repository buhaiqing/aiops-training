#!/bin/bash
# Lab 1: 快速安装 uv 工具

echo "========================================"
echo "安装 uv - 超快的 Python 包管理工具"
echo "========================================"
echo ""

# 检查是否已安装
if command -v uv &> /dev/null; then
    echo "✓ uv 已安装，版本信息:"
    uv --version
    exit 0
fi

echo "开始安装 uv..."
echo ""

# 方法 1: 使用 pip 安装（推荐）
if command -v pip3 &> /dev/null; then
    echo "使用 pip3 安装 uv..."
    pip3 install uv
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ uv 安装成功!"
        echo ""
        echo "验证安装:"
        uv --version
        echo ""
        echo "下一步操作:"
        echo "  cd lab1_3sigma_anomaly_detection"
        echo "  make all"
        exit 0
    fi
fi

# 方法 2: 使用官方安装脚本
echo "尝试使用官方安装脚本..."
curl -LsSf https://astral.sh/uv/install.sh | sh

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ uv 安装成功!"
    echo ""
    echo "请运行以下命令重新加载 shell 配置:"
    echo "  source \$HOME/.local/bin/env"
    echo ""
    echo "然后重新运行:"
    echo "  make all"
    exit 0
fi

echo ""
echo "❌ 安装失败，请手动安装:"
echo ""
echo "方法 1 (推荐):"
echo "  pip install uv"
echo ""
echo "方法 2:"
echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
echo ""
echo "方法 3:"
echo "  访问 https://github.com/astral-sh/uv 获取更多信息"
echo ""

exit 1
