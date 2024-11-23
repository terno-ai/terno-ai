@echo off

:: Define paths relative to the current script location
SET ROOT_DIR=%~dp0
SET FRONTEND_DIR=%ROOT_DIR%frontend
SET TEMPLATES_DIR=%ROOT_DIR%terno\frontend\templates\frontend
SET STATIC_DIR=%ROOT_DIR%terno\frontend\static

:: Step 1: Run npm build inside frontend directory
echo Step 1: Running npm build...
call npm --prefix "%FRONTEND_DIR%" run build
if %ERRORLEVEL% neq 0 (
    echo ERROR: npm build failed.
    pause
    exit /b 1
)

:: Step 2: Copy index.html to Django templates directory
echo Step 2: Copying index.html to Django templates directory...
if exist "%FRONTEND_DIR%\dist\index.html" (
    copy /y "%FRONTEND_DIR%\dist\index.html" "%TEMPLATES_DIR%\index.html"
    echo Step 2 completed successfully.
) else (
    echo ERROR: index.html not found. Ensure npm build succeeded.
    pause
    exit /b 1
)

:: Step 3: Remove all files in Django static directory
echo Step 3: Removing all files in Django static directory...
if exist "%STATIC_DIR%" (
    rmdir /s /q "%STATIC_DIR%"
    mkdir "%STATIC_DIR%"
    echo Step 3 completed successfully.
) else (
    echo ERROR: STATIC_DIR not found. Creating it...
    mkdir "%STATIC_DIR%"
)

:: Step 4: Copy assets to Django static directory
echo Step 4: Copying assets to Django static directory...
if exist "%FRONTEND_DIR%\dist\assets" (
    xcopy /e /i "%FRONTEND_DIR%\dist\assets" "%STATIC_DIR%\"
    echo Step 4 completed successfully.
) else (
    echo ERROR: Assets directory not found. Ensure npm build succeeded.
    pause
    exit /b 1
)

echo Build process completed successfully!
pause
