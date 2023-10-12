@echo off
set WEB_ROOT=https://files.minecraftforge.net
set DOWNLOAD_ROOT=https://maven.minecraftforge.net
set STATIC_DIR=file://%cd:\=/%/static/
set ARGS=./python/page_generator.py --webout "./out/" --metaout "./out" --config "./config/global_overrides.json" --webroot "%WEB_ROOT%" --downloadroot "%DOWNLOAD_ROOT%" --static "%STATIC_DIR%" --folder "./maven" --templates "./templates/" --local-data
python %ARGS% promote net.minecraftforge:forge 1.16.5-36.1.0 recommended
python %ARGS% promote net.minecraftforge:forge 1.16.5-36.1.2 latest
python %ARGS% promote net.minecraftforge:forge 1.18.1-39.1.0 recommended
python %ARGS% promote net.minecraftforge:forge 1.18.1-39.1.2 latest
python %ARGS% promote net.minecraftforge:forge 1.18.2-40.0.8 latest
python %ARGS% promote net.minecraftforge:froge 23w13a_or_b-april.2023.13.b.8 latest
python %ARGS% promote net.minecraftforge:froge 23w17a-2023.17.a.8 latest
python %ARGS% promote net.minecraftforge:froge 1.20.1-pre1-46.0.8 latest
python %ARGS% promote net.minecraftforge:froge 1.19.4-45.0.8 latest
python %ARGS% promote net.minecraftforge:froge 1.20-rc1-46.1.8 latest