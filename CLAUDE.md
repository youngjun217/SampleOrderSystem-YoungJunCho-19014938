# CLAUDE.md — SampleOrderSystem

S Semi의 반도체 시료 생산주문관리 시스템.
**콘솔(CLI)** 과 **PyQt6 GUI** 두 가지 인터페이스를 모두 제공하며,
PoC 4개(consoleMVC, DataPersistence, DataMonitor, DummyDataGenerator)를 통합한 메인 프로젝트다.

---

## 시스템 개요

- **CLI**: 담당자가 콘솔에서 직접 명령을 입력하여 조작한다.
- **GUI**: PyQt6 기반 다크 테마 데스크톱 애플리케이션 (`app_gui.py`).
- 생산라인은 **주문이 들어온 시료에 대해서만** 가동한다 (수요 기반 생산).
- 하나의 생산라인은 **시료를 하나씩 순차 생산**하며, 동시에 하나의 주문만 처리한다.
- 주문 승인 시 재고가 충분하면 즉시 출고(`CONFIRMED`), 부족하면 유휴 생산라인 배정(`PRODUCING`).

---

## 기술 스택

| 항목 | 내용 |
|------|------|
| 언어 | Python 3.10+ |
| 데이터 저장 | JSON 파일 (`data/*.json`) |
| CLI 외부 의존성 | 표준 라이브러리만 사용 |
| GUI 외부 의존성 | PyQt6 (`pip install PyQt6`) |
| 아키텍처 | MVC + Repository 패턴 |

---

## 프로젝트 구조

```
SampleOrderSystem/
├── model/
│   ├── sample.py             # Sample (시료ID·이름·평균생산시간·수율·재고)
│   ├── order.py              # Order, OrderStatus
│   ├── production_line.py    # ProductionLine, LineStatus
│   └── production.py         # Production (부족분·실생산량·총시간·FIFO큐)
├── repository/
│   ├── base_repository.py
│   ├── sample_repository.py
│   ├── order_repository.py
│   ├── production_line_repository.py
│   └── production_repository.py
├── controller/
│   ├── sample_controller.py
│   ├── order_controller.py
│   └── production_controller.py
├── view/                     # CLI 뷰 (ANSI 컬러 + 박스 드로잉)
│   ├── theme.py              # 색상·박스·섹션 헬퍼
│   ├── utils.py              # display-width 정렬 헬퍼
│   ├── main_view.py
│   ├── sample_view.py
│   ├── order_view.py
│   ├── monitor_view.py
│   ├── release_view.py
│   └── production_line_view.py
├── gui/                      # PyQt6 GUI
│   ├── style.py              # QSS 다크 테마
│   ├── widgets.py            # 공용 위젯 (상태뱃지·수율게이지·카드)
│   ├── main_window.py        # 메인 윈도우 + 사이드바
│   └── panels/
│       ├── sample_panel.py
│       ├── order_panel.py
│       ├── monitor_panel.py
│       ├── production_panel.py
│       └── release_panel.py
├── tools/
│   └── dummy_generator.py    # 더미 데이터 생성 (--reset, --list, --summary)
├── data/
│   ├── samples.json
│   ├── orders.json
│   ├── production_lines.json
│   └── productions.json
├── main.py                   # CLI 진입점
└── app_gui.py                # GUI 진입점
```

---

## 실행 방법

```bash
# CLI 실행
python -X utf8 main.py

# GUI 실행
python -X utf8 app_gui.py

# 더미 데이터 생성
python -X utf8 tools/dummy_generator.py --reset --samples 5 --orders 15

# 더미 데이터 DB 요약
python -X utf8 tools/dummy_generator.py --summary
```

> Windows에서 `-X utf8` 플래그로 실행하거나, 환경변수 `PYTHONUTF8=1`을 설정한다.

---

## 코딩 규칙

- 모든 소스 파일은 `UTF-8`로 저장한다.
- Model은 순수 데이터 클래스(`@dataclass`)만 포함하며, 비즈니스 로직을 갖지 않는다.
- Repository는 JSON 파일 I/O만 담당한다. DB 교체 시 Repository만 수정한다.
- Controller가 Model과 Repository를 조합하여 비즈니스 로직을 처리한다.
- CLI View는 `input()`과 `print()`만 사용하며, 로직을 갖지 않는다.
- GUI Panel은 `QWidget` 기반이며 Controller를 직접 호출한다.
- 상태값은 모두 Enum으로 정의한다.
- 한글 출력은 display-width(`view/utils.py`)로 정렬한다.

---

## 사용자 역할

| 역할 | 시스템 접근 | 주요 행동 |
|------|------------|----------|
| 고객 | 외부 (이메일만) | 시료 종류·수량·납기를 이메일로 요청. 시스템 직접 접근 없음. |
| 주문담당자 | CLI / GUI | 이메일 기반으로 주문서 작성 및 현황 조회 |
| 생산담당자 | CLI / GUI | 시료 등록, 주문 승인/거절, 생산라인 배정·완료 처리 |

---

## 주문 상태 (OrderStatus)

| 상태 | 코드 | 설명 |
|------|------|------|
| 주문접수 | `RESERVED` | 주문담당자가 주문을 등록한 초기 상태 |
| 주문거절 | `REJECTED` | 생산담당자가 주문을 거절한 상태 (사유 포함) |
| 생산중 | `PRODUCING` | 주문 승인 완료, 재고 부족으로 생산라인 가동 중 |
| 출고대기 | `CONFIRMED` | 주문 승인 완료, 재고 확보되어 출고 대기 중 |
| 출고완료 | `RELEASE` | 시료가 고객에게 출고된 최종 상태 |

```
RESERVED
  ├─ 거절 ──────────────────────────────▶ REJECTED
  ├─ 승인 + 재고 부족 ──▶ PRODUCING ──▶ CONFIRMED ──▶ RELEASE
  └─ 승인 + 재고 충분 ──────────────▶ CONFIRMED ──▶ RELEASE
```

---

## 생산량 계산 공식

```
부족분        = 주문수량 - 현재재고
실 생산량     = ceil(부족분 / (수율 × 0.9))
총 생산시간   = 평균생산시간(h) × 실 생산량
```

- `수율 × 0.9` : 수율에 10% 오차 마진 적용
- 생산 완료 시: `재고 += 부족분`, `재고 -= 주문수량` (순 재고 변동)
- 대기 큐 스케줄링: **FIFO** (`queued_at` 기준 오름차순)

---

## 도메인 개념

| 용어 | 설명 |
|------|------|
| 시료 (Sample) | S Semi가 생산·납품하는 반도체 시료. ID·이름·평균생산시간·수율·재고로 구성. |
| 주문 (Order) | 주문담당자가 고객 이메일을 기반으로 등록하는 주문 단위. |
| 생산라인 (ProductionLine) | 웨이퍼 공정 설비 단위. 시료를 하나씩 순차 생산, 동시 1개 주문만 처리. |
| 생산 이력 (Production) | 생산라인 배정 시 생성. 부족분·실생산량·총시간 포함. |
| 재고 분기 | 승인 시 재고 충분 → `CONFIRMED`, 부족 → 생산라인 배정 후 `PRODUCING`. |
| 수요 기반 생산 | 주문 없으면 생산하지 않음. 사전 생산 불가. |
| FIFO 큐 | 유휴 라인 없을 시 대기. `queued_at` 순으로 자동 배정. |

---

## 관련 PoC 저장소

| PoC | 저장소 | 역할 |
|-----|--------|------|
| consoleMVC | ConsoleMVC-YoungJunCho-19014938 | MVC 구조 참조 |
| DataPersistence | DataPersistence-YoungJunCho-19014938 | Repository 패턴 참조 |
| DataMonitor | DataMonitor-YoungJunCho-19014938 | 대시보드 참조 |
| DummyDataGenerator | DummyDataGenerator-YoungJunCho-19014938 | 더미 데이터 참조 |

---

## 참고 문서

- `PRD.md` — 제품 요구사항 정의서
