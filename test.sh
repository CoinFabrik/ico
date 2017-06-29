#!/bin/bash

(testrpc -p 20487 --account="0xb3a7675a3ca6976d0c29fd8eeb04e8c68c0ced322b96671b04c51d54162fff81,0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF" --account="0x0156f5d7ef74552352abbde8db173f69336d5623e7dd4a9dc7b524feb2d4826f,0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF") > /dev/null &
pid_testrpc=$!
truffle test --network testrpc
kill -n 2 $pid_testrpc