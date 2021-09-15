#### 模拟器启动命令

```
# 在模拟器目录（hephaestus）内执行
java -cp hephaestus-rpc.jar com.geekplus.hephaestus.rpc.SimulatorServer
```

#### GUI 程序启动命令

```
# 在 bundle 目录内执行

# 机器人路径规划GUI启动命令
python multi_robot.py

# 机器人空负截路径规划GUI启动命令
python multi_robot_load.py

# 密集存储GUI启动命令
python dense_storge.py

# 货到人GUI启动命令
python multi_task.py
```

#### 无界面验证程序启动命令

```
# 在根目录内执行

# 机器人路径规划无界面启动命令
python -m bundle.resource.serve.multi_robot.cli

# 机器人空负载路径规划无界面启动命令
python -m bundle.resource.serve.multi_robot_load.cli

# 密集存储无界面启动命令
python -m bundle.resource.serve.dense_storge.cli

# 货到人无界面启动命令
python -m bundle.resource.serve.multi_task.cli

```

#### 算法 demo 启动命令

```
# 在对应算法目录下执行
python __main__.py
```

#### 算法开发流程：

1. 在 bundle 目录下，直接运行对应项目的 Python 文件，如 multi_task.py。可直接启动模拟器及界面
2. 启动算法 demo
3. 开始调试

#### 目录说明：

| 目录       | 子目录    | 说明                                               |
| ---------- | --------- | -------------------------------------------------- |
| hephaestus |           | java 模拟器目录                                    |
| resource   |           | 模拟器中间层及赛题代码                             |
|            | gui       | 赛题 GUI 代码                                      |
|            | proto     | 赛题 proto 定义文件                                |
|            | Simulator | 赛题中间层逻辑代码（包含 task,参数设置，赛题验证） |
| algorithm  |           | 算法代码                                           |
| Test       |           | 线上验证代码（docer file,shell 脚本,赛题信息）     |

#### 生成 proto 相关文件命令

```
python -m grpc_tools.protoc -I./ --python_out=./ --grpc_python_out=./ hephaestus.proto
```

#### python 打包成 pyz 命令

```
python -m zipapp [目录名]

or

python -m zipapp [目录名] -o [文件名].pyz -m "[入口文件]:[文件方法]"
```

#### 单元格类型枚举

| 类型编号 | 类型 code             | 说明                             |
| -------- | --------------------- | -------------------------------- |
| 0        | NULL                  | 未分配功能的单元格               |
| 1        | SHELF_CELL            | 放置货架的单元格                 |
| 2        | E2W_PATH_CELL         | 东向西过道的单元格               |
| 3        | W2E_PATH_CELL         | 西向东过道的单元格               |
| 4        | S2N_PATH_CELL         | 南向北过道的单元格               |
| 5        | N2S_PATH_CELL         | 北向南过道的单元格               |
| 6        | E2W_S2N_PATH_CELL     | 东向西过道与南向北过道交叉单元格 |
| 7        | E2W_N2S_PATH_CELL     | 东向西过道与北向南过道交叉单元格 |
| 8        | W2E_S2N_PATH_CELL     | 西向东过道与南向北过道交叉单元格 |
| 9        | W2E_N2S_PATH_CELL     | 西向东过道与北向南过道交叉单元格 |
| 10       | E2W_W2E_PATH_CELL     | 可向东西两个方向走的单元格       |
| 11       | N2S_S2N_PATH_CELL     | 可向南北两个方向走的单元格       |
| 12       | E2W_W2E_N2S_PATH_CELL | 可向东西南三个方向走的单元格     |
| 13       | E2W_W2E_S2N_PATH_CELL | 可向东西北三个方向走的单元格     |
| 14       | N2S_S2N_E2W_PATH_CELL | 可向南北西三个方向走的单元格     |
| 15       | N2S_S2N_W2E_PATH_CELL | 可向南北东三个方向走的单元格     |
| 16       | OMNI_DIR_CELL         | 可以向四个方向行走的单元格       |
| 17       | PICKSTATION_PICK_CELL | 拣货站拣货的位置                 |
| 18       | PICKSTATION_TURN_CELL | 拣货站转向的位置                 |
| 19       | PICKSTATION_PATH_CELL | 拣货站排队路径                   |
| 20       | CHARGER_CELL          | 充电桩位置                       |
| 21       | CHARGER_PI_CELL       | 充电桩电源接口位置               |
| 22       | BLOCKED_CELL          | 阻塞的单元格                     |
| 23       | ENTRY                 | 入口                             |
| 24       | EXIT                  | 出口                             |
