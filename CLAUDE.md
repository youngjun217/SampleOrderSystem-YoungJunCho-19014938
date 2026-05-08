# CLAUDE.md — SampleOrderSystem

S Semi의 반도체 시료 생산주문관리 시스템.
콘솔 기반 Python MVC 애플리케이션으로, PoC 4개(consoleMVC, DataPersistence, DataMonitor, DummyDataGenerator)를 통합한 메인 프로젝트다.

---

## 기술 스택

- **언어**: Python 3.10+
- **데이터 저장**: JSON 파일 (`data/*.json`)
- **외부 라이브러리**: 표준 라이브러리만 사용
- **아키텍처**: MVC + Repository 패턴

---

## 프로젝트 구조 (목표)

```
SampleOrderSystem/
├── model/
│   ├── order.py          # Order, OrderStatus
│   ├── sample.py         # Sample (재고)
│   └── process.py        # Process (공정)
├── repository/
│   ├── order_repository.py
│   ├── sample_repository.py
│   └── process_repository.py
├── controller/
│   ├── order_controller.py      # 주문담당자: 주문 생성·조회
│   ├── production_controller.py # 생산담당자: 승인/거절, 공정·재고 관리
│   └── process_controller.py
├── view/
│   ├── order_view.py
│   ├── production_view.py
│   └── process_view.py
├── monitor/
│   └── dashboard.py      # DataMonitor 역할
├── tools/
│   └── dummy_generator.py  # DummyDataGenerator 역할
├── data/
│   ├── orders.json
│   ├── samples.json
│   └── processes.json
└── main.py
```

---

## 실행 방법

```bash
# 메인 시스템 실행
python -X utf8 main.py

# 더미 데이터 생성
python -X utf8 tools/dummy_generator.py -n 20 --reset

# 모니터링 대시보드
python -X utf8 monitor/dashboard.py
```

> Windows에서 `-X utf8` 플래그로 실행하거나, 환경변수 `PYTHONUTF8=1`을 설정한다.

---

## 코딩 규칙

- 모든 소스 파일은 `UTF-8`로 저장한다.
- Model은 순수 데이터 클래스(`@dataclass`)만 포함하며, 비즈니스 로직을 갖지 않는다.
- Repository는 JSON 파일 I/O만 담당한다. DB 교체 시 Repository만 수정한다.
- Controller가 Model과 Repository를 조합하여 비즈니스 로직을 처리한다.
- View는 `input()`과 `print()`만 사용하며, 로직을 갖지 않는다.
- 상태값은 모두 Enum으로 정의한다.

---

## 사용자 역할

| 역할 | 시스템 접근 | 주요 행동 |
|------|------------|----------|
| 고객 | 외부 (이메일만) | 시료 종류·수량·납기를 이메일로 요청. 시스템 직접 접근 없음. |
| 주문담당자 | 직접 사용 | 이메일 기반으로 주문서 작성 및 현황 조회 |
| 생산담당자 | 직접 사용 | 개발시료 등록, 주문 승인/거절, 공정·재고 관리 |

---

## 도메인 개념

| 용어 | 설명 |
|------|------|
| 시료 (Sample) | S Semi가 생산·납품하는 반도체 시료. 종류별로 재고를 관리한다. |
| 주문 (Order) | 주문담당자가 고객 이메일을 기반으로 시스템에 등록하는 주문 단위. |
| 승인/거절 | 생산담당자가 주문을 검토하여 처리 가능 여부를 결정하는 단계. |
| 공정 (Process) | 시료를 제작하기 위한 웨이퍼 공정 작업. 재고 부족 시 착수한다. |
| 재고 분기 로직 | 주문 승인 시 재고가 충분하면 즉시 출고, 부족하면 공정을 예약한다. |

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
