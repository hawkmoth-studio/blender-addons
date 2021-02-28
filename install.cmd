ECHO OFF

set BLENDER_VERSION=2.83
set BLENDER_ADDONS_DIR=%APPDATA%\Blender^ Foundation\Blender\%BLENDER_VERSION%\scripts\addons


CALL :addon_install hms_compositing
CALL :addon_install hms_rendering
CALL :addon_install hms_rigging
goto :eof


:addon_install
SETLOCAL
set addon_name=%1
set addon_source_dir=%addon_name%
set addon_target_dir=%BLENDER_ADDONS_DIR%\%addon_name%

echo Uninstalling '%addon_name%'...
rmdir "%addon_target_dir%" /S /Q
echo Installing '%addon_name%'...
mkdir "%addon_target_dir%"
robocopy "%addon_source_dir%" "%addon_target_dir%" /S /NP
echo Addon '%addon_name%' successfully installed to '%addon_target_dir%'.
ENDLOCAL & SET _result=0


:eof
