@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 포터블 단일 exe 빌드

echo [1/2] 빌드 도구 준비...
py -m pip install --quiet --upgrade nuitka ordered-set zstandard customtkinter
if errorlevel 1 goto :fail

echo [2/2] Nuitka 컴파일 - 수 분 걸립니다...
py -m nuitka ^
  --onefile ^
  --assume-yes-for-downloads ^
  --experimental=force-dependencies-pefile ^
  --lto=no ^
  --enable-plugin=tk-inter ^
  --windows-console-mode=disable ^
  --include-package=customtkinter ^
  --include-package-data=customtkinter ^
  --include-data-dir=guide=guide ^
  --include-data-dir=licenses=licenses ^
  --include-data-file=routine\camera_mute.rtn=routine\camera_mute.rtn ^
  --include-data-file=app.ico=app.ico ^
  --windows-icon-from-ico=app.ico ^
  --company-name="Choi Seunghoon" ^
  --product-name="Galaxy Camera Mute" ^
  --file-description="Galaxy Camera Mute" ^
  --file-version=1.0.1 ^
  --product-version=1.0.1 ^
  --copyright="Copyright (c) 2026 Choi Seunghoon - gwchoi.com" ^
  --nofollow-import-to=unittest ^
  --nofollow-import-to=pydoc ^
  --output-dir=build_portable ^
  --output-filename="GalaxyCameraMute.exe" ^
  --remove-output ^
  main.py
if errorlevel 1 goto :fail

echo.
echo 완료: build_portable\GalaxyCameraMute.exe
echo 이 파일 하나만 배포하면 됩니다. 라이선스 전문은 프로그램의 [정보] 창에 들어 있습니다.
pause
exit /b 0

:fail
echo.
echo 빌드에 실패했습니다. 위 메시지를 확인해주세요.
pause
exit /b 1
