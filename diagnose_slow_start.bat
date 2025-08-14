@echo off
echo ============================================================
echo QUICK DIAGNOSIS: Why is startup slow?
echo ============================================================
echo.

echo Checking model cache locations...
python check_model_cache.py

echo.
echo ============================================================
echo SOLUTIONS:
echo ============================================================
echo.
echo 1. If models NOT cached:
echo    python download_models_now.py
echo.
echo 2. If models ARE cached but still slow:
echo    The HAK_GAL_SUITE/shared_models.py loads them fresh each time
echo    This is a known issue with the legacy integration
echo.
echo 3. IMMEDIATE FIX - Set Windows Environment Variables:
echo    setx TRANSFORMERS_CACHE "%USERPROFILE%\.cache\huggingface"
echo    setx SENTENCE_TRANSFORMERS_HOME "%USERPROFILE%\.cache\torch\sentence_transformers"
echo    Then restart the command prompt
echo.
echo 4. Or use start_fast.bat which sets these automatically
echo ============================================================
pause
