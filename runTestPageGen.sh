#!/bin/sh
python3 ./python/page_generator.py --webout "./test/out/" --metaout "./test/out" --config "./test/global_overrides.json" --webroot "https://files.minecraftforge.net" --downloadroot "https://maven.minecraftforge.net" --static "file://$(pwd)/test/static/" --folder "./test/maven" --templates "./templates/" --local-data promote net.minecraftforge:forge 1.16.5-36.1.0 recommended
python3 ./python/page_generator.py --webout "./test/out/" --metaout "./test/out" --config "./test/global_overrides.json" --webroot "https://files.minecraftforge.net" --downloadroot "https://maven.minecraftforge.net" --static "file://$(pwd)/test/static/" --folder "./test/maven" --templates "./templates/" --local-data promote net.minecraftforge:forge 1.16.5-36.1.2 latest
python3 ./python/page_generator.py --webout "./test/out/" --metaout "./test/out" --config "./test/global_overrides.json" --webroot "https://files.minecraftforge.net" --downloadroot "https://maven.minecraftforge.net" --static "file://$(pwd)/test/static/" --folder "./test/maven" --templates "./templates/" --local-data promote net.minecraftforge:forge 1.18.1-39.1.0 recommended
python3 ./python/page_generator.py --webout "./test/out/" --metaout "./test/out" --config "./test/global_overrides.json" --webroot "https://files.minecraftforge.net" --downloadroot "https://maven.minecraftforge.net" --static "file://$(pwd)/test/static/" --folder "./test/maven" --templates "./templates/" --local-data promote net.minecraftforge:forge 1.18.1-39.1.2 latest
python3 ./python/page_generator.py --webout "./test/out/" --metaout "./test/out" --config "./test/global_overrides.json" --webroot "https://files.minecraftforge.net" --downloadroot "https://maven.minecraftforge.net" --static "file://$(pwd)/test/static/" --folder "./test/maven" --templates "./templates/" --local-data promote net.minecraftforge:forge 1.18.2-40.0.8 latest