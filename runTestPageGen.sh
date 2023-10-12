#!/bin/sh
ARGS="./python/page_generator.py --webout ./out/ --metaout ./out --config ./config/global_overrides.json --webroot https://files.minecraftforge.net --downloadroot https://maven.minecraftforge.net --static file://$(pwd)/static/ --folder ./maven --templates ./templates/ --local-data"
python3 $ARGS promote net.minecraftforge:forge 1.16.5-36.1.0 recommended
python3 $ARGS promote net.minecraftforge:forge 1.16.5-36.1.2 latest
python3 $ARGS promote net.minecraftforge:forge 1.18.1-39.1.0 recommended
python3 $ARGS promote net.minecraftforge:forge 1.18.1-39.1.2 latest
python3 $ARGS promote net.minecraftforge:forge 1.18.2-40.0.8 latest
python3 $ARGS promote net.minecraftforge:froge 23w13a_or_b-april.2023.13.b.8 latest
python3 $ARGS promote net.minecraftforge:froge 23w17a-2023.17.a.8 latest
python3 $ARGS promote net.minecraftforge:froge 1.20.1-pre1-46.0.8 latest
python3 $ARGS promote net.minecraftforge:froge 1.19.4-45.0.0 latest