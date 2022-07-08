#!/bin/bash

for file in apps/*; do
	if [[ -d $file ]]; then
		if [[ -d $file/test-cases ]]; then
			rm -rf $file/test-cases/*
		fi
	fi
done
