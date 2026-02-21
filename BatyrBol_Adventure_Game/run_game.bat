@echo off
title Batyr Bol Adventure Game
color 0A

echo ========================================
echo        BATYR BOL ADVENTURE
echo ========================================
echo.
echo Запуск игры...
echo.

REM Проверяем наличие dotnet
dotnet --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: .NET не найден в системе!
    echo.
    echo Пожалуйста, установите .NET 6.0 или выше:
    echo https://dotnet.microsoft.com/download
    echo.
    echo После установки запустите этот файл снова.
    pause
    exit /b 1
)

echo .NET найден. Запуск игры...
echo.

REM Запускаем игру
dotnet run --project BatyrBolGame.csproj

if %errorlevel% neq 0 (
    echo.
    echo Произошла ошибка при запуске игры.
    pause
)

echo.
echo Спасибо за игру!
pause
