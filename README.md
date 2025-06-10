# Linux Optimization & Restoration System

시스템 성능을 자동으로 최적화하고 보안을 강화하며, 디스크 정리와 복원 설정까지 포함한 리눅스 최적화 프로젝트입니다.

---

## 프로젝트 구조

├── src/                  # 최적화, 복원, 설정 로직
│   ├── optimizer.py
│   ├── restore.py
│   └── gui/              # GUI 인터페이스 구성
│       ├── main_gui_redesign.py
│       └── sections/
├── config/               # 설정 JSON (optimizer_settings.json)
├── logs/                 # 실행 로그 기록
├── tests/                # 최적화 기능 테스트
└── README.md             # 설명 문서

---

## 주요 기능 요약

최적화 : CPU scheduler, I/O, 메모리 관리, 좀비 프로세스 제거, 불필요 서비스 제거

보안  : UFW 방화벽 설정, SSH 보안 설정 강화 (PermitRootLogin, MaxAuthTries 등)

디스크 : 디스크 조각 모음, 오래된 임시 파일 자동 삭제, 빈 디렉토리 정리

복원  : 사용자 정의 파일/디렉토리 백업 및 복원, Timeshift 기반 시스템 스냅샷

자동화 : 백업 자동화 스케줄 설정 (시간 간격 설정 가능), 설정 GUI 제공

---

## GUI 사용법

cd capstone-linux_Optimization-restoration-main/ # 기준

python3 src/gui/main_gui_redesign.py

#GUI는 좌측 사이드 네비게이션을 통해 세 가지 탭을 제공합니다:

최적화 : 항목별 최적화 실행 및 결과 확인 (✅ / ⚠️ / ❌ 상태 표시)

복원 : 사용자 정의 백업 복원, 삭제, Timeshift 스냅샷 관리

설정 : 백업 경로, 자동 백업 주기, 설정 구성파일 관리 등

---

## 가상환경 사용법 (Python 3.8+ 기준)

### 가상환경 생성 및 접속 및 해제

python3 -m venv venv

source venv/bin/activate  # Linux/macOS

deactivate

---

## 필수 패키지 설치

sudo apt install python3-pip

sudo apt install python3-tk

sudo apt install timeshift

sudo apt install openssh-server

sudo pip install -r requirements.txt

{

    psutil
    
    click>=8.1.3
    
    colorama>=0.4.6
    
    rich>=13.4.2
    
    jsonschema
    
    pytest>=7.4.0
    
}

## 최적화 진단 테스트
sudo PYTHONPATH=. python3 tests/test_optimizer.py

## Timeshift 관련 안내
### 왜 수동 복원이 필요한가?
Timeshift는 루트 권한과 시스템 파일을 다루기 때문에 GUI 상에서 자동화된 복원이 어렵습니다. 복원 중 부트로더, 시스템 라이브러리, 사용자 환경이 변경될 수 있어, 사용자 승인 하에 터미널에서 직접 복원하는 것이 안전합니다.

### Timeshift 스냅샷 생성 (GUI 지원)
복원 > Timeshift 스냅샷 생성 클릭

### Timeshift 수동 복원
sudo timeshift --restore

### Timeshift 수동 삭제
sudo timeshift --delete

## GitHub에 업로드
### 초기화 및 연결
git init

git remote add origin https://github.com/yourusername/your-repo.git

### 파일 스테이징 및 커밋
git add .

git commit -m "Initial commit"

### 업로드
git branch -M main

git push -u origin main

### GitHub에서 다운로드

git pull origin main

## 참고 사항
Linux 전용으로 설계되었습니다. Windows나 macOS에서는 동작이 보장되지 않습니다.
sudo 권한이 필요한 기능이 많으므로 GUI 및 스크립트 실행 시 sudo 사용을 권장합니다.