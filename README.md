# Vision-Based-Autonomous-Driving-on-Raspberry-Pi

## 1. Overview
카메라 기반 CNN 모델을 활용하여 도로의 차선을 인식하고,  
예측된 조향각을 통해 차량을 자율 주행시키는 시스템을 구현하였습니다.

본 프로젝트는 perception → control로 이어지는  
end-to-end 자율주행 파이프라인을 Raspberry Pi 환경에서 구현하는 것을 목표로 합니다.

### - Team Project

본 프로젝트는 팀 프로젝트로 수행되었으며,  
본 저장소는 해당 프로젝트에서 수행한 구현 내용을 정리한 것입니다.

### - My Contributions

- 자율주행 학습 데이터 직접 수집 (실제 주행 기반 이미지 데이터 구축)
- CNN / NVIDIA 기반 조향각 예측 모델 학습
- 이미지 전처리 및 threshold 기반 차선 인식을 위한 코드 개선
- 특정 예측값 패턴을 활용하여 횡단보도를 인식하고, 정지 후 재출발하는 제어 로직 적용
---

## 2. System Architecture

Camera → Frame Capture → CNN Inference → Steering Angle Prediction → Motor Control

- Input: 실시간 카메라 영상
- Output: 조향각 기반 모터 제어

---

## 3. Tech Stack

### Hardware
- Raspberry Pi (자율주행 차량 제어)
- Camera Module

### Software
- Python
- OpenCV (실시간 영상 처리 및 전처리)
- PyTorch (CNN 기반 조향각 예측 모델 학습)

### Environment
- Google Colab (GPU 기반 학습 환경)
- Raspberry Pi OS (실시간 추론 및 제어)
- Samba (PC ↔ 라즈베리파이 데이터 전송)

### Key Libraries
- NumPy
- Pandas
- Matplotlib

---

## 4. Key Features

- 실시간 영상 기반 자율 주행
- CNN 기반 조향각 예측
- Edge 환경(Raspberry Pi)에서 동작
- 횡단보도 인식 후 정지 기능 구현

---

## 5. Data Collection

- 직접 주행하며 데이터 수집 (약 4,000 ~ 24,000장)
- 다양한 트랙 사용:
  - D형 → 실패
  - O형 → 성공 (데이터 균형 확보)
  - 직각 코스 → 추가 학습

### 핵심 개선 사항
- 카메라 각도 조정 (시야 확장 및 왜곡 최소화)
- 데이터 불균형 문제 해결 (좌/우 균형 맞춤)
- 불필요한 직진 데이터 제거

---

## 6. Model

- CNN 기반 조향각 회귀 모델
- NVIDIA 모델과 비교 실험 수행

### 선택 이유
- 실시간 추론 가능
- 경량화된 구조

---

## 7. Problems & Solutions

### 1) 차량이 한 방향으로만 회전
- 원인: 데이터 불균형
- 해결: O형 트랙으로 좌/우 데이터 균형 확보

### 2) 차선을 인식하지 못함
- 원인: 카메라 시야 부족 및 노이즈
- 해결: 카메라 각도 조정 + 임계값 튜닝

### 3) 직각 코스 주행 실패
- 원인: 데이터 부족 및 과적합
- 해결: 직각 데이터 추가 수집

### 4) 주행 불안정
- 원인: 모델 출력값 해석 문제
- 해결: 조향각 범위 재설정

---

## 8. Result

- 직선 및 곡선 코스 안정적 주행
- 횡단보도 인식 후 10초 정지 기능 구현
- 실시간 환경에서 동작 가능한 수준 확보

---

## 9. Project Structure

```
Vision-Based-Autonomous-Driving-on-Raspberry-Pi/
├── 주행용/                 # 주행용 (실제 자율주행 실행)
│   ├── nvidia_run.py
│   └── worst_model.pth         # 횡단보도 인식 포함 모델
│
├── 학습용/                    # 주행 연습용 (기본 주행)
│   ├── cnn_run.py
│   └── best_model.pth          # 기본 주행 안정화 모델
│
└── cnn_make_model.ipynb    # 모델 학습 코드
```

---

## 10. Execution Flow

본 프로젝트는 **학습 → 배포 → 실행**의 구조로 동작합니다.

### 1) Model Training
- `cnn_make_model.ipynb`
- 주행 데이터를 기반으로 CNN / NVIDIA 모델 학습

### 2) Model Deployment
- 학습된 `.pth` 모델을 Raspberry Pi로 이동

### 3) Real-time Inference & Control
- `nvidia_run.py` / `cnn_run.py`
- 카메라 입력 → 모델 추론 → 모터 제어

---

## 11. Model Usage

### CNN Model (기본 주행)
- 파일: `cnn_run.py`
- 모델: `best_model.pth`
- 역할:
  - 직선 및 곡선 주행 안정화
  - 기본 자율주행 테스트

---

### NVIDIA Model (고도화 주행)
- 파일: `nvidia_run.py`
- 모델: `worst_model.pth`
- 역할:
  - 더 정교한 조향 제어
  - 횡단보도 인식 후 정지 기능 포함

---

### Note
- `.pth` 파일은 학습된 모델 가중치이며,
  `run` 코드에서 로드되어 실시간 추론에 사용됩니다.
