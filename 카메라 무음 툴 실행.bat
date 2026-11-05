@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 갤럭시 카메라 무음

set "PYW="

where pyw >nul 2>&1
if not errorlevel 1 set "PYW=pyw"

if not defined PYW (
    where pythonw >nul 2>&1
    if not errorlevel 1 set "PYW=pythonw"
)

if not defined PYW (
    where py >nul 2>&1
    if not errorlevel 1 set "PYW=py"
)

if not defined PYW (
    echo.
    echo  [오류] PC에서 Python을 찾을 수 없습니다.
    echo  https://www.python.org/downloads/ 에서 Python 3.10 이상을 설치한 뒤 다시 실행해주세요.
    echo  설치할 때 "Add python.exe to PATH" 항목을 꼭 체크하세요.
    echo.
    pause
    exit /b 1
)

rem PySide6가 없으면 한 번만 설치한다
%PYW% -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo.
    echo  처음 실행이라 필요한 구성요소 PySide6 를 설치합니다. 잠시만 기다려주세요...
    echo.
    py -m pip install --upgrade PySide6
    if errorlevel 1 (
        echo.
        echo  [오류] PySide6 설치에 실패했습니다. 인터넷 연결을 확인해주세요.
        pause
        exit /b 1
    )
)

start "" %PYW% "%~dp0main.py"
