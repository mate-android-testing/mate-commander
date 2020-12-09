#!/bin/bash

for file in apps/*; do
	if [[ -d $file ]]; then
		if [[ -d $file/traces ]]; then
			rm -rf $file/traces/*
		fi
	fi
done
