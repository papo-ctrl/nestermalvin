#!/bin/bash
pyarmor clean
pyarmor pack -e " --onefile" -x " --exclude tests" .
