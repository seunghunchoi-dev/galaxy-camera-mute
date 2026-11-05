# 제3자 구성요소 고지

저작자 코드와 문서는 저작자에게 모든 권리가 있습니다(LICENSE 파일, 수정·재배포 금지).
아래 구성요소는 각자의 라이선스를 따르며, **모두 소스 공개 의무가 없는 허용형 라이선스**입니다.

라이선스 전문은 프로그램의 **[정보] → [라이선스 전문 보기]** 에 들어 있고,
이 저장소의 `licenses/` 폴더에도 같은 파일이 있습니다.

| 구성요소 | 라이선스 | 용도 |
|---|---|---|
| [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | MIT | GUI 툴킷 |
| [Pillow](https://python-pillow.org) | MIT-CMU (HPND) | 안내 이미지 표시 |
| [darkdetect](https://github.com/albertosottile/darkdetect) | BSD 3-Clause | 윈도우 테마 감지 |
| Python / Tcl-Tk | PSF · Tcl-Tk | 실행 환경, 기본 GUI |
| [Zstandard (zstd)](https://github.com/facebook/zstd) | BSD 3-Clause | 단일 exe 압축 해제 (Nuitka가 포함) |
| [Nuitka](https://nuitka.net) 런타임 | AGPLv3 + Nuitka Runtime Library Exception | 빌드 도구 (아래 4번) |
| [Android SDK Platform-Tools (adb)](https://developer.android.com/tools/releases/platform-tools) | Apache 2.0 | 휴대폰 통신 (**동봉하지 않음**) |

모두 수정 없이 그대로 사용합니다.

사용설명서를 만드는 데만 쓰는 [pptxgenjs](https://github.com/gitbrent/PptxGenJS)(MIT)와
JSZip(MIT)은 `npm install` 로 받으며 저장소와 exe에 들어 있지 않습니다.

---

## 1. MIT · BSD 구성요소 (CustomTkinter, Pillow, darkdetect)

이들 라이선스는 배포물에 **저작권 고지와 라이선스 전문을 포함**할 것을 요구합니다.
파일 하나로 배포하기 위해 전문을 **exe 안에 넣고 [정보] 창에서 볼 수 있게** 했습니다.
따라서 exe 하나만 올려도 고지 의무가 충족됩니다.

별도 파일로 같이 올리고 싶다면 `licenses/` 폴더를 함께 배포하면 됩니다.

> 참고: 초기 버전은 PySide6(Qt)를 썼으나, **LGPL**이라 단일 exe로 배포하려면
> 애플리케이션 소스를 함께 공개해야 했습니다. 소스를 비공개로 두면서 단일 파일로
> 배포하기 위해 GUI를 MIT 라이선스인 CustomTkinter로 교체했습니다.

---

## 2. Android SDK Platform-Tools (adb)

**배포물에 동봉하지 않습니다.** adb가 없으면 프로그램이 사용자에게 묻고,
사용자가 동의하면 **Google 공식 서버에서 직접** 내려받습니다.
즉 배포자가 재배포하는 행위 자체가 없으므로 Android SDK 약관과 무관합니다.

굳이 동봉하려는 경우를 위해 정리해 두면, Android SDK License Agreement 3.4는 재배포를
금지하지만 **"Except to the extent required by applicable third party licenses"** 라는
단서가 있고 3.5가 다음과 같이 규정합니다.

> **3.5** Use, reproduction and distribution of components of the SDK licensed under an
> open source software license are governed solely by the terms of that open source
> software license and not the License Agreement.

platform-tools의 내용물은 AOSP 코드이며 패키지에 포함된 `NOTICE.txt`(약 1.1MB)가
Apache 2.0 등을 고지합니다. 동봉한다면 그 폴더를 **NOTICE.txt 를 포함해 통째로** 넣고
파일을 수정하거나 저작권 표시를 제거하지 마세요(약관 3.8).

---

## 3. 휴대폰 화면 이미지 (`guide/`, `manual/`, `docs/images/`)

`guide/01`~`07`과 사용설명서·README의 휴대폰 화면은 삼성 Galaxy A17(One UI 8.5)의
스크린샷으로, 사용 방법을 설명하기 위한 목적으로만 포함했습니다.
화면의 UI 디자인과 상표는 **삼성전자**의 자산이며, 앱 목록 화면에 보이는 다른 앱 아이콘
(Gemini, 카카오톡 등)의 상표는 각 소유자에게 있습니다.
`08_allow_popup.png`는 실제 캡처가 아니라 같은 모양으로 그린 **예시 이미지**입니다.

"Galaxy", "갤럭시", "Bixby", "One UI"는 삼성전자의 상표이고, "Android"는 Google LLC의
상표입니다. 이 프로그램 이름의 '갤럭시'는 대상 기기를 설명하기 위한 것입니다.
본 소프트웨어는 삼성전자 및 Google과 아무런 제휴 관계가 없습니다.

---

## 4. Nuitka 런타임

exe는 [Nuitka](https://nuitka.net)로 컴파일했습니다. Nuitka 4.x는 AGPLv3이지만
**Nuitka Runtime Library Exception**이 붙어 있어, Nuitka로 컴파일한 결과물(exe)은
AGPL 의무 없이 원하는 라이선스로 배포할 수 있습니다. 이 exe는 저작자 라이선스(LICENSE)로 배포합니다.

---

## 5. 사용설명서

사용설명서(`manual/`)의 글과 구성은 저작자 저작물로 LICENSE를 따릅니다.
PDF에는 Windows 기본 글꼴 '맑은 고딕'(Microsoft)이 일부 포함되어 있으며,
이 글꼴은 문서 포함(embedding)이 허용된 글꼴입니다.
