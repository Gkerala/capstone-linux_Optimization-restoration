# Linux Optimization & Restoration System

시스템 성능을 자동으로 최적화하고 보안을 강화하며, 디스크 정리와 복원 설정까지 포함한 리눅스 최적화 프로젝트입니다.

---

## 프로젝트 구조

├── src/ # 최적화 로직

├── config/ # 설정 JSON 파일

├── logs/ # 로그 저장 위치

├── test/ # 진단 및 유닛 테스트

└── README.md # 설명 문서

---

## 가상환경 사용법

Python 3.8+ 기준

### 가상환경 생성 및 접속 및 해제

python3 -m venv venv

source venv/bin/activate  # Linux/macOS

deactivate

## 필수 패키지 설치

sudo apt install python3-pip

sudo apt install python3-tk

sudo pip install -r requirements.txt

{

    psutil
    
    click>=8.1.3
    
    colorama>=0.4.6
    
    rich>=13.4.2
    
    jsonschema
    
    pytest>=7.4.0

    openssh-server -y
    
}

## GitHub에 업로드
# 초기화 및 연결
git init

git remote add origin https://github.com/yourusername/your-repo.git

# 파일 스테이징 및 커밋
git add .

git commit -m "Initial commit"

# 업로드
git branch -M main

git push -u origin main

## 시스템 최적화 실행 방법
sudo PYTHONPATH=. python3 src/optimizer.py

## 최적화 기능 진단 실행
sudo PYTHONPATH=. python3 tests/test_optimizer.py


