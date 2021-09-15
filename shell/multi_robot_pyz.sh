#!/bin/sh
java -cp /root/resource/hephaestus/hephaestus-rpc.jar com.geekplus.hephaestus.rpc.SimulatorServer 1>slog.log 2>elog.log &
sleep 10
mkdir -p /root/resource/algorithm
\cp -rf /tmp/user.pyz /root/resource/algorithm/algorithm.pyz
python3 /root/resource/algorithm/algorithm.pyz &
sleep 10
cd /root/resource/ && python3 -um bundle.resource.serve.multi_robot.cli
