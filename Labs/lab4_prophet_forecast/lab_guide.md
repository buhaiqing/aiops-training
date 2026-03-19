# Lab 4: Prophet 时序预测与异常检测 - 详细指导

## 📖 实验背景

在 AIOps 场景中，很多监控指标（如 CPU 使用率、内存占用、网络流量等）都具有明显的时序特征。Facebook 开源的 Prophet 是一个强大的时序预测工具，能够自动捕捉趋势、季节性和节假日效应。本实验将学习如何使用 Prophet 进行时序建模和基于预测残差的异常检测。

---

## 🎯 学习目标

1. **理解 Prophet 模型原理**
   - 加法模型架构
   - 趋势项建模方法
   - 季节性成分分解
   
2. **掌握 Prophet 实战技能**
   - 数据格式要求
   - 模型参数调优
   - 置信区间设置
   
3. **学会异常检测方法**
   - 基于预测区间的异常判定
   - Z-Score 标准化残差分析
   - 动态阈值调整策略

4. **对比分析方法**
   - Prophet vs LSTM
   - Prophet vs 3-Sigma
   - 不同场景下的选择建议

---

## 📚 前置知识

- Python 编程基础
- Pandas 数据处理
- 基本的统计学知识（均值、标准差、正态分布）
- 了解时序数据的基本概念

---

## 🔬 实验原理

### 1. Prophet 模型架构

Prophet 使用加法模型：

```
y(t) = g(t) + s(t) + h(t) + ε(t)
```

其中：
- **g(t)**: 趋势项（Trend），可以是线性或逻辑增长
- **s(t)**: 季节性项（Seasonality），包括周、月、年周期
- **h(t)**: 节假日项（Holidays），处理特殊日期影响
- **ε(t)**: 误差项（Error），随机噪声

### 2. 异常检测机制

#### 方法一：置信区间法
```python
# 如果实际值超出 95% 置信区间，则判定为异常
if y_actual > yhat_upper or y_actual < yhat_lower:
    is_anomaly = True
```

#### 方法二：Z-Score 法
```python
# 计算标准化残差
residual = y_actual - yhat
z_score = residual / std(residuals)

# 如果 |z_score| > threshold，则为异常
if abs(z_score) > 2.5:
    is_anomaly = True
```

---

## 💻 实验步骤

### Step 1: 环境准备

```bash
cd lab4_prophet_forecast

# 创建虚拟环境
make venv

# 激活环境（macOS/Linux）
source .venv/bin/activate

# 安装依赖
make deps
```

**依赖说明**:
- `prophet`: Facebook 时序预测库
- `pandas`: 数据处理
- `matplotlib`: 可视化
- `scikit-learn`: 评估指标

---

### Step 2: 生成模拟数据

```bash
make data
```

**数据特点**:
- 时间跨度：365 天
- 包含成分：
  - 线性增长趋势（+0.05/天）
  - 周季节性（7 天周期）
  - 年季节性（365 天周期）
  - 周末效应（流量下降）
  - 节假日效应（春节、国庆等）
  - 随机噪声
  - 注入异常点（15 个）

**代码解析** (`generate_data.py`):
```python
# 趋势成分
trend = 50 + 0.05 * t

# 周季节性
weekly_seasonality = 5 * np.sin(2 * np.pi * t / 7) + 3 * np.cos(2 * np.pi * t / 7)

# 年季节性
yearly_seasonality = 8 * np.sin(2 * np.pi * t / 365) + 4 * np.cos(2 * np.pi * t / 365)

# 节假日效应
if date.weekday() >= 5:  # 周末
    holidays_effect[i] = -8

# 组合所有成分
cpu_usage = trend + weekly_seasonality + yearly_seasonality + holidays_effect + noise
```

---

### Step 3: 训练 Prophet 模型

运行主程序会自动训练模型：

```bash
make run
```

**关键参数**:
```python
model = Prophet(
    daily_seasonality=False,      # 关闭日季节性（我们是日粒度数据）
    weekly_seasonality=True,       # 启用周季节性
    yearly_seasonality=True,       # 启用年季节性
    changepoint_prior_scale=0.05,  # 趋势变化点调节（越大越灵活）
    interval_width=0.95            # 95% 置信区间
)
```

**参数调优建议**:
- `changepoint_prior_scale`: 
  - 趋势稳定 → 0.01-0.05
  - 趋势多变 → 0.1-0.5
- `interval_width`:
  - 严格检测 → 0.90
  - 宽松检测 → 0.99

---

### Step 4: 执行预测

模型训练完成后，会自动进行未来 30 天的预测：

```python
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)
```

**输出内容**:
- `ds`: 日期
- `yhat`: 预测值
- `yhat_upper`: 置信区间上界
- `yhat_lower`: 置信区间下界
- `trend`: 趋势成分
- `weekly`: 周季节性成分
- `yearly`: 年季节性成分

---

### Step 5: 异常检测

核心检测逻辑：

```python
# 1. 计算残差
residuals = actual_values - predicted_values

# 2. 计算 Z-Score
z_scores = residuals / np.std(residuals)

# 3. 综合判定
is_anomaly = (np.abs(z_scores) > 2.5) | \
             (actual_values > yhat_upper) | \
             (actual_values < yhat_lower)
```

**阈值选择**:
- `threshold_multiplier = 2.0`: 敏感检测（检出率高，误报率高）
- `threshold_multiplier = 2.5`: 平衡模式（推荐）
- `threshold_multiplier = 3.0`: 保守检测（检出率低，准确率高）

---

### Step 6: 模型评估

评估指标：

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error

mae = mean_absolute_error(actual, predicted)
rmse = np.sqrt(mean_squared_error(actual, predicted))
mape = np.mean(np.abs((actual - predicted) / actual)) * 100
```

**评价标准**:
- MAE < 5: 优秀
- RMSE < 8: 良好
- MAPE < 10%: 可接受

---

### Step 7: 结果可视化

生成的图表包含 6 个子图：

1. **Prophet 组件分解图**: 展示趋势、季节性、节假日成分
2. **实际值 vs 预测值**: 对比真实数据和预测结果
3. **残差分析**: 显示预测误差分布
4. **异常分数分布**: 每个时间点的 Z-Score
5. **异常点时空分布**: 高亮标记异常区域
6. **长期预测趋势**: 未来 30 天的预测

---

## 📊 结果解读

### 示例输出

```
============================================================
模型性能评估
============================================================
✓ 平均绝对误差 (MAE):  3.2145
✓ 均方根误差 (RMSE):   4.1234
✓ 平均绝对百分比误差 (MAPE): 6.78%

============================================================
异常检测
============================================================
✓ 检测方法：基于预测残差 + 置信区间
✓ 阈值倍数：2.5
✓ 检测到的异常点数量：12
✓ 检出率：3.29%

共发现 12 个异常点

Top 5 严重异常点:
------------------------------------------------------------
#1: 时间=2025-12-15, 值=92.34%, 异常分数=4.2156
#2: 时间=2025-11-28, 值=15.67%, 异常分数=3.8923
...
```

### 如何分析结果

1. **检查模型拟合度**
   - 查看 MAE/RMSE 是否在合理范围
   - 观察预测曲线是否贴合实际值

2. **分析异常点**
   - 真阳性：确实是故障点
   - 假阳性：正常波动被误判
   - 假阴性：漏掉的故障点

3. **调整参数优化**
   - 增加/减少 `changepoint_prior_scale`
   - 调整 `threshold_multiplier`
   - 添加更多节假日信息

---

## 🔍 扩展练习

### 练习 1: 对比不同阈值的效果

修改 `main.py` 中的 `threshold_multiplier` 参数：

```python
anomaly_scores, is_anomaly = detect_anomalies(
    forecast,
    actual_test_values,
    threshold_multiplier=2.0  # 改为 2.0, 2.5, 3.0 分别测试
)
```

记录并对比：
- 检出的异常点数量
- 精确率和召回率
- 误报率

---

### 练习 2: 添加自定义节假日

在 `generate_data.py` 中添加更多节假日：

```python
holiday_dates = [
    start_date + timedelta(days=30),    # 春节
    start_date + timedelta(days=90),    # 清明
    start_date + timedelta(days=180),   # 年中促销
    start_date + timedelta(days=270),   # 中秋
    start_date + timedelta(days=300),   # 国庆
    start_date + timedelta(days=330),   # 双 11
]
```

观察对预测效果的影响。

---

### 练习 3: 多步预测

修改预测期数：

```python
forecast = make_predictions(model, test_data, forecast_periods=90)
```

分析：
- 短期预测（7 天）vs 中期预测（30 天）vs 长期预测（90 天）
- 预测不确定性随时间的变化

---

### 练习 4: 对比实验

对比不同模型的效果：

| 模型 | MAE | RMSE | MAPE | 适用场景 |
|------|-----|------|------|---------|
| 3-Sigma | ? | ? | ? | 稳定指标 |
| Isolation Forest | ? | ? | ? | 多维联合 |
| LSTM Autoencoder | ? | ? | ? | 复杂时序 |
| Prophet | ? | ? | ? | 趋势 + 季节性 |

---

## ⚠️ 注意事项

1. **数据质量要求**
   - 至少需要 2-3 个完整周期的历史数据
   - 缺失值不能太多（建议 < 10%）
   - 异常值比例不宜过高（建议 < 5%）

2. **计算资源**
   - Prophet 训练速度较慢（相比统计方法）
   - 大数据集建议降采样或分段训练

3. **参数敏感性**
   - 需要多次调参才能获得最佳效果
   - 建议使用网格搜索或贝叶斯优化

---

## 📈 实际应用场景

### 场景 1: 网站流量预测与异常检测

- **数据**: 每日 PV/UV
- **特点**: 明显的周季节性（工作日 vs 周末）
- **价值**: 提前发现流量异常，预防服务器过载

### 场景 2: 业务指标监控

- **数据**: 订单量、交易额、转化率
- **特点**: 受促销活动、节假日影响大
- **价值**: 识别业务异常波动

### 场景 3: 资源容量规划

- **数据**: CPU、内存、磁盘使用率
- **特点**: 长期增长趋势 + 周期性波动
- **价值**: 预测资源耗尽时间，提前扩容

---

## 🤔 思考题

1. Prophet 在处理突发事件（如疫情、政策变化）时有什么局限？如何改进？

2. 如何结合业务先验知识来优化 Prophet 的参数？

3. Prophet 和 LSTM 各有哪些优缺点？在什么场景下应该选择哪种方法？

4. 如果要实现实时异常检测，Prophet 方案需要做哪些改造？

---

## 📚 参考资料

- [Prophet 官方文档](https://facebook.github.io/prophet/)
- [Prophet 论文](https://peerj.com/preprints/3190/)
- [时序分析经典教程](https://robjhyndman.com/uwafiles/fpp-notes.pdf)

---

## ✅ 总结

通过本实验，你掌握了：
- ✅ Prophet 时序预测模型的原理和使用
- ✅ 基于预测残差的异常检测方法
- ✅ 时序数据的趋势和季节性分析
- ✅ 模型评估和参数调优技巧

这为你后续学习更复杂的深度学习方法（如 Lab 3 的 LSTM）和 LLM 应用打下了坚实基础！

---

**Happy Coding! 🚀**
