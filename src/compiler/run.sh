#!/bin/bash
nasm -felf64 main.asm && ld main.o && ./a.out; echo $?
rm -f main.o a.out
