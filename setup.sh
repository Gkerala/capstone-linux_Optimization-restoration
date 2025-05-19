#!/bin/bash

echo "🚀 [Linux Optimizer] 환경 설정 시작"

# 1. 시스템 패키지 설치 (Ubuntu/Debian 기준)
echo "🔧 시스템 패키지 설치 중..."
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-tk \
    python3-dev \
    build-essential \
    ufw \
    openssh-server

# 2. 가상환경 설정
echo "🐍 가상환경 생성 및 활성화 중..."
python3 -m venv .venv
source .venv/bin/activate

# 3. pip 최신화
echo "📦 pip 업그레이드..."
pip install --upgrade pip

# 4. Python 패키지 설치
echo "📚 Python 패키지 설치 (requirements.txt)..."
pip install -r requirements.txt

echo "✅ 모든 설정이 완료되었습니다!"
echo "ℹ️ 가상환경 활성화: source .venv/bin/activate"

