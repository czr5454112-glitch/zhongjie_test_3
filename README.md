# Continuous Conflict-Based Search (CCBS) 项目

本项目实现了连续空间下的冲突基搜索（Conflict-Based Search, CCBS）算法，并结合强化学习（PPO）来优化分支策略，用于多智能体路径规划（Multi-Agent Path Finding, MAPF）问题。

## 项目特点

- **连续空间路径规划**：支持智能体在连续空间中的路径规划，而非离散网格
- **SIPP算法**：使用安全间隔路径规划（Safe Interval Path Planning, SIPP）作为低层规划器
- **强化学习优化**：使用PPO（Proximal Policy Optimization）算法学习最优分支策略
- **多种优化策略**：支持cardinal冲突优先、不相交分割、走廊对称性、目标对称性等优化技术
- **完整可视化**：提供路径规划结果的可视化展示

## 目录结构

```
code_continuous_CBS/
├── continuous_CBS/          # 核心代码目录
│   ├── ccbs.py              # CCBS主算法实现
│   ├── sipp.py              # SIPP低层规划器
│   ├── map.py               # 地图加载和处理
│   ├── structs.py           # 数据结构定义
│   ├── config.py            # 配置类
│   ├── ccbsenv.py           # 强化学习环境
│   ├── heuristic.py         # 启发式函数
│   ├── Animation.py         # 可视化模块
│   ├── run.py               # 统一运行脚本（推荐使用）
│   ├── train_PPO.py         # PPO训练脚本
│   ├── instances/           # 测试实例目录
│   │   ├── roadmaps/        # 路网地图
│   │   ├── empty-16-16-random/
│   │   ├── room-64-64-8_random/
│   │   ├── den520d_random/
│   │   └── warehouse-10-20-random/
│   └── ppo_*.zip            # 训练好的PPO模型
├── requirements.txt         # Python依赖包
├── README.md               # 本文件
└── pyproject.toml          # 项目配置文件
```

## 环境要求

- **Python版本**: >= 3.9
- **操作系统**: Windows / Linux / macOS

## 安装依赖

### 方法1：使用pip安装（推荐）

```bash
# 安装所有依赖
pip install -r requirements.txt
```

### 方法2：手动安装

```bash
pip install numpy>=1.21.0
pip install networkx>=2.6.0
pip install matplotlib>=3.4.0
pip install stable-baselines3>=2.0.0
pip install gymnasium>=0.28.0
pip install pandas>=1.3.0
```

## 快速开始

### 1. 使用统一运行脚本（推荐）

项目提供了统一的运行脚本 `continuous_CBS/run.py`，支持多种运行模式。

#### 配置运行模式

编辑 `continuous_CBS/run.py` 文件，修改以下配置：

```python
# 运行模式：可选 "train", "solve", "evaluate", "batch_test"
RUN_MODE = "solve"

# CCBS算法配置
CCBS_CONFIG = {
    "use_rl": True,                    # 是否使用强化学习
    "rl_model_path": None,              # RL模型路径（None表示自动选择）
    "agent_size": 0.5,                 # 智能体尺寸
    "timelimit": 300,                  # 时间限制（秒）
    # ... 更多配置见文件
}

# 地图和任务配置
MAP_AND_TASK_CONFIG = {
    "map_path": "instances/roadmaps/sparse/map.xml",
    "task_path": "instances/roadmaps/sparse/test/10/1_task-10.xml",
    # ... 更多配置见文件
}
```

#### 运行脚本

```bash
# 进入项目目录
cd continuous_CBS

# 运行脚本
python run.py
```

### 2. 直接使用CCBS算法

```python
from ccbs import CCBS
from map import Map
from structs import Task, Agent

# 加载地图
map = Map("instances/roadmaps/sparse/map.xml")

# 创建CCBS求解器
ccbs = CCBS(map)

# 创建任务
task = Task()
task.agents.append(Agent(35, 85, 0))  # 智能体0：从节点35到节点85
task.agents.append(Agent(161, 113, 1))  # 智能体1：从节点161到节点113

# 求解
solution = ccbs.find_solution(task)

# 输出结果
print(f"找到解: {solution.found}")
print(f"总路径长度: {solution.flowtime}")
print(f"最大路径长度: {solution.makespan}")
```

### 3. 从文件加载任务

```python
from ccbs import CCBS
from map import Map
from structs import Task

# 加载地图和任务
map = Map("instances/roadmaps/sparse/map.xml")
task = Task()
task.load_from_file("instances/roadmaps/sparse/test/10/1_task-10.xml")

# 求解
ccbs = CCBS(map)
solution = ccbs.find_solution(task)

# 可视化结果
from Animation import GraphRender
animation = GraphRender(map, task, solution.paths)
animation.show()
```

## 运行模式说明

### 1. 训练模式 (train)

训练PPO模型来学习CCBS的分支策略。

```python
RUN_MODE = "train"
```

配置项：
- `PPO_TRAIN_CONFIG`: PPO训练参数（学习率、折扣因子等）
- `MAP_AND_TASK_CONFIG["train_task_dir"]`: 训练任务目录

### 2. 求解模式 (solve)

使用训练好的模型求解单个任务。

```python
RUN_MODE = "solve"
```

配置项：
- `MAP_AND_TASK_CONFIG["map_path"]`: 地图路径
- `MAP_AND_TASK_CONFIG["task_path"]`: 任务文件路径
- `SOLVE_CONFIG`: 求解配置（是否可视化、保存结果等）

### 3. 评估模式 (evaluate)

在测试集上评估模型性能。

```python
RUN_MODE = "evaluate"
```

配置项：
- `MAP_AND_TASK_CONFIG["test_task_dir"]`: 测试任务目录
- `MAP_AND_TASK_CONFIG["test_subdirs"]`: 测试子目录（可选）

### 4. 批量测试模式 (batch_test)

与评估模式相同，用于批量测试多个任务。

## 配置说明

### CCBS算法配置

在 `run.py` 中的 `CCBS_CONFIG` 字典中配置：

- `agent_size`: 智能体尺寸，范围 (0, 0.5]
- `hlh_type`: 高层启发式类型（0-无, 1-单纯形法, 2-贪婪选择）
- `precision`: 等待时间确定精度
- `timelimit`: 求解时间限制（秒）
- `use_precalculated_heuristic`: 是否使用预计算启发式（反向Dijkstra）
- `use_disjoint_splitting`: 是否使用不相交分割
- `use_cardinal`: 是否优先处理cardinal冲突
- `use_corridor_symmetry`: 是否使用走廊对称性
- `use_target_symmetry`: 是否使用目标对称性
- `use_rl`: 是否使用强化学习
- `rl_model_path`: RL模型路径（None表示自动选择）

### 强化学习环境配置

在 `run.py` 中的 `RL_ENV_CONFIG` 字典中配置：

- `max_step`: 最大搜索步数
- `reward_1`: 找到解的奖励
- `reward_2`: 分支数量权重
- `reward_3`: 违反约束的惩罚
- `cost_weight`: 目标函数权重

## 模型文件

项目包含预训练的PPO模型：

- `ppo_road-sparse.zip`: 用于sparse路网地图
- `ppo_empty-16-16-random.zip`: 用于empty-16-16-random地图

模型会自动根据地图路径选择，也可以手动指定。

## 输出结果

### Solution对象包含：

- `found`: 是否找到解
- `flowtime`: 总路径长度（所有智能体路径长度之和）
- `makespan`: 最大路径长度（所有智能体中路径最长的）
- `time`: 求解耗时（秒）
- `high_level_expanded`: 扩展的高层节点数
- `low_level_expansions`: 低层搜索次数
- `paths`: 所有智能体的路径列表

### 保存解决方案

```python
# 保存为XML格式
ccbs.write_to_log_path('solution.xml')
```

## 常见问题

### 1. 找不到RL模型

**问题**: `FileNotFoundError: RL model not found`

**解决**:
- 检查 `CCBS_CONFIG["rl_model_path"]` 是否正确
- 确保模型文件存在于 `continuous_CBS/` 目录下
- 如果使用自动选择，检查 `MAP_TO_MODEL_MAPPING` 中的映射关系

### 2. 地图文件加载失败

**问题**: 地图文件无法加载

**解决**:
- 确保地图文件路径正确（相对于 `continuous_CBS/` 目录）
- 检查地图文件格式是否为有效的GraphML格式

### 3. 可视化无法显示

**问题**: 在无GUI环境中无法显示图形

**解决**:
- 设置 `SOLVE_CONFIG["visualize"] = False`
- 或使用非交互式matplotlib后端

### 4. 训练速度慢

**问题**: PPO训练速度很慢

**解决**:
- 减少 `PPO_TRAIN_CONFIG["total_timesteps_per_env"]`
- 减少训练任务数量
- 使用GPU加速（如果可用）

## 依赖包详细说明

- **numpy**: 数值计算
- **networkx**: 图结构处理和地图加载
- **matplotlib**: 可视化
- **stable-baselines3**: 强化学习算法（PPO）
- **gymnasium**: 强化学习环境接口
- **pandas**: 数据处理和结果保存

## 引用

如果使用本项目，请引用相关论文：

- CCBS算法: [Continuous Conflict-Based Search](https://github.com/PathPlanning/Continuous-CBS)
- SIPP算法: Safe Interval Path Planning

## 许可证

请查看 LICENSE 文件了解许可证信息。

## 联系方式

如有问题或建议，请通过GitHub Issues联系。

## 更新日志

### v1.0.0
- 初始版本
- 实现CCBS算法
- 集成PPO强化学习
- 提供统一运行脚本
- 支持多种地图和任务格式
