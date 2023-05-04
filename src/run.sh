#!/bin/bash
nasm -felf64 main.asm && ld main.o && ./a.out; echo Exited with $?
rm -f main.o a.out
