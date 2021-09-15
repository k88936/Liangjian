#!/bin/sh
java -cp /root/resource/hephaestus/hephaestus-rpc.jar com.geekplus.hephaestus.rpc.SimulatorServer 1>slog.log 2>elog.log &
sleep 10
mkdir -p /root/resource/algorithm
\cp -rf /tmp/user.jar /root/resource/algorithm/algorithm.jar
java -jar /root/resource/algorithm/algorithm.jar 1>rslog.log 2>relog.log &
sleep 10
cd /root/resource && python3 -um bundle.resource.serve.multi_robot.cli
