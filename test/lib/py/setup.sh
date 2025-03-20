#!/bin/bash

make

poetry run python -m msgpact_test

