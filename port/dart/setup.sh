#!/bin/bash

npx rollup -c rollup.crc32.config.js
npx rollup -c rollup.msgpackr.config.js

cp node_modules/uapi/dist/index.iife.js lib/js/uapi.js
cp dist/crc32.iife.js lib/js/crc32.js
cp dist/msgpackr.iife.js lib/js/msgpackr.js
