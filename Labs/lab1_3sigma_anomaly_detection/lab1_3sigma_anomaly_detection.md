# Lab 1: 3-Sigma 原则检测 CPU/内存异常

## 实验目标
- 理解 3-Sigma 原则的基本原理
- 掌握使用统计方法进行异常检测
- 能够识别 CPU 和内存使用率中的异常点

## 实验环境
```bash
pip install pandas numpy matplotlib seaborn
```

## 数据准备

### 1. 生成模拟数据

```python
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 设置随机种子以保证结果可复现
np.random.seed(42)

# 生成 7 天（1008 个时间点，每 10 分钟一个点）的 CPU 使用率数据
n_points = 1008
start_time = datetime.now() - timedelta(days=7)

# 正常 CPU 使用率：均值 45%，标准差 10%
cpu_normal = np.random.normal(loc=45, scale=10, size=n_points)

# 添加一些异常点（模拟故障）
anomaly_indices = np.random.choice(n_points, size=20, replace=False)
cpu_anomalies = np.random.uniform(low=85, high=98, size=20)
cpu_usage = cpu_normal.copy()
cpu_usage[anomaly_indices] = cpu_anomalies

# 确保 CPU 使用率在 0-100 之间
cpu_usage = np.clip(cpu_usage, 0, 100)

# 生成时间戳
timestamps = [start_time + timedelta(minutes=10*i) for i in range(n_points)]

# 创建 DataFrame
df_cpu = pd.DataFrame({
    'timestamp': timestamps,
    'cpu_usage_percent': cpu_usage
})

# 同样方法生成内存使用率数据
mem_normal = np.random.normal(loc=60, scale=8, size=n_points)
mem_anomaly_indices = np.random.choice(n_points, size=15, replace=False)
mem_anomalies = np.random.uniform(low=90, high=99, size=15)
mem_usage = mem_normal.copy()
mem_usage[mem_anomaly_indices] = mem_anomalies
mem_usage = np.clip(mem_usage, 0, 100)

df_mem = pd.DataFrame({
    'timestamp': timestamps,
    'memory_usage_percent': mem_usage
})

# 合并数据
df = pd.merge(df_cpu, df_mem, on='timestamp')

# 保存为 CSV
df.to_csv('cpu_memory_data.csv', index=False)
print(f"数据已生成并保存到 cpu_memory_data.csv")
print(f"数据形状：{df.shape}")
print(f"\n前 5 行数据:")
print(df.head())
```

## 2. 3-Sigma 异常检测实现

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
df = pd.read_csv('cpu_memory_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

# 3-Sigma 原则检测函数
def detect_anomalies_3sigma(data, column_name):
    """
    使用 3-Sigma 原则检测异常
    
    参数:
        data: 输入 DataFrame
        column_name: 要检测的列名
    
    返回:
        anomalies: 异常点 DataFrame
        lower_bound: 下界
        upper_bound: 上界
    """
    # 计算均值和标准差
    mean = data[column_name].mean()
    std = data[column_name].std()
    
    # 计算 3-Sigma 边界
    lower_bound = mean - 3 * std
    upper_bound = mean + 3 * std
    
    # 检测异常点
    anomalies = data[(data[column_name] < lower_bound) | 
                     (data[column_name] > upper_bound)].copy()
    anomalies['anomaly_type'] = np.where(
        anomalies[column_name] < lower_bound, 
        '低于下界', 
        '高于上界'
    )
    
    return anomalies, lower_bound, upper_bound, mean, std

# 检测 CPU 异常
cpu_anomalies, cpu_lower, cpu_upper, cpu_mean, cpu_std = detect_anomalies_3sigma(
    df, 'cpu_usage_percent'
)

# 检测内存异常
mem_anomalies, mem_lower, mem_upper, mem_mean, mem_std = detect_anomalies_3sigma(
    df, 'memory_usage_percent'
)

print("=" * 60)
print("CPU 使用率 3-Sigma 检测结果")
print("=" * 60)
print(f"均值：{cpu_mean:.2f}%")
print(f"标准差：{cpu_std:.2f}%")
print(f"正常范围：[{cpu_lower:.2f}%, {cpu_upper:.2f}%]")
print(f"检测到的异常点数量：{len(cpu_anomalies)}")
print(f"异常率：{len(cpu_anomalies)/len(df)*100:.2f}%")

print("\n" + "=" * 60)
print("内存使用率 3-Sigma 检测结果")
print("=" * 60)
print(f"均值：{mem_mean:.2f}%")
print(f"标准差：{mem_std:.2f}%")
print(f"正常范围：[{mem_lower:.2f}%, {mem_upper:.2f}%]")
print(f"检测到的异常点数量：{len(mem_anomalies)}")
print(f"异常率：{len(mem_anomalies)/len(df)*100:.2f}%")
```

## 3. 可视化结果

```python
# 创建可视化图表
fig, axes = plt.subplots(2, 1, figsize=(16, 10))

# CPU 使用率图
axes[0].plot(df['timestamp'], df['cpu_usage_percent'], 
             alpha=0.6, label='CPU 使用率', linewidth=1)
axes[0].axhline(y=cpu_mean, color='green', linestyle='--', 
                label=f'均值 ({cpu_mean:.2f}%)', linewidth=2)
axes[0].axhline(y=cpu_upper, color='red', linestyle='--', 
                label=f'上界 ({cpu_upper:.2f}%)', linewidth=2)
axes[0].axhline(y=cpu_lower, color='orange', linestyle='--', 
                label=f'下界 ({cpu_lower:.2f}%)', linewidth=2)

# 标记异常点
axes[0].scatter(cpu_anomalies['timestamp'], 
                cpu_anomalies['cpu_usage_percent'],
                c='red', s=100, marker='o', 
                label=f'异常点 ({len(cpu_anomalies)}个)', 
                zorder=5, edgecolors='black')

# 填充正常区域
axes[0].fill_between(df['timestamp'], 
                      cpu_lower, cpu_upper, 
                      alpha=0.2, color='green',
                      label='正常范围')

axes[0].set_title('CPU 使用率 3-Sigma 异常检测', fontsize=14, fontweight='bold')
axes[0].set_xlabel('时间')
axes[0].set_ylabel('CPU 使用率 (%)')
axes[0].legend(loc='upper right', fontsize=10)
axes[0].grid(True, alpha=0.3)

# 内存使用率图
axes[1].plot(df['timestamp'], df['memory_usage_percent'], 
             alpha=0.6, label='内存使用率', linewidth=1, color='orange')
axes[1].axhline(y=mem_mean, color='green', linestyle='--', 
                label=f'均值 ({mem_mean:.2f}%)', linewidth=2)
axes[1].axhline(y=mem_upper, color='red', linestyle='--', 
                label=f'上界 ({mem_upper:.2f}%)', linewidth=2)
axes[1].axhline(y=mem_lower, color='darkorange', linestyle='--', 
                label=f'下界 ({mem_lower:.2f}%)', linewidth=2)

# 标记异常点
axes[1].scatter(mem_anomalies['timestamp'], 
                mem_anomalies['memory_usage_percent'],
                c='red', s=100, marker='^', 
                label=f'异常点 ({len(mem_anomalies)}个)', 
                zorder=5, edgecolors='black')

# 填充正常区域
axes[1].fill_between(df['timestamp'], 
                      mem_lower, mem_upper, 
                      alpha=0.2, color='green',
                      label='正常范围')

axes[1].set_title('内存使用率 3-Sigma 异常检测', fontsize=14, fontweight='bold')
axes[1].set_xlabel('时间')
axes[1].set_ylabel('内存使用率 (%)')
axes[1].legend(loc='upper right', fontsize=10)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('3sigma_detection_result.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n可视化结果已保存到：3sigma_detection_result.png")
```

## 4. 异常详情报告

```python
# 生成异常详情报告
def generate_anomaly_report(anomalies, metric_name):
    """生成异常详情报告"""
    print(f"\n{'='*60}")
    print(f"{metric_name}异常详情报告")
    print(f"{'='*60}")
    
    if len(anomalies) == 0:
        print("未检测到异常")
        return
    
    print(f"\n共发现 {len(anomalies)} 个异常点:\n")
    
    for idx, row in anomalies.iterrows():
        anomaly_type = row.get('anomaly_type', '未知')
        if 'cpu' in metric_name.lower():
            value = row['cpu_usage_percent']
        else:
            value = row['memory_usage_percent']
        
        print(f"时间：{row['timestamp']}, "
              f"值：{value:.2f}%, "
              f"类型：{anomaly_type}")

# 生成报告
generate_anomaly_report(cpu_anomalies, 'CPU')
generate_anomaly_report(mem_anomalies, '内存')
```

## 5. 扩展练习

### 练习 1: 调整 Sigma 阈值

```python
# 尝试不同的 Sigma 阈值（2-Sigma, 2.5-Sigma, 3-Sigma）
def compare_sigma_thresholds(data, column_name, sigma_values=[2, 2.5, 3]):
    """比较不同 Sigma 阈值的检测效果"""
    mean = data[column_name].mean()
    std = data[column_name].std()
    
    results = []
    for sigma in sigma_values:
        lower = mean - sigma * std
        upper = mean + sigma * std
        anomaly_count = len(data[(data[column_name] < lower) | 
                                  (data[column_name] > upper)])
        anomaly_rate = anomaly_count / len(data) * 100
        
        results.append({
            'Sigma': sigma,
            '下界': lower,
            '上界': upper,
            '异常数量': anomaly_count,
            '异常率 (%)': anomaly_rate
        })
    
    return pd.DataFrame(results)

# 比较 CPU 检测效果
print("CPU 使用率 - 不同 Sigma 阈值对比:")
cpu_comparison = compare_sigma_thresholds(df, 'cpu_usage_percent')
print(cpu_comparison.to_string(index=False))

# 比较内存检测效果
print("\n内存使用率 - 不同 Sigma 阈值对比:")
mem_comparison = compare_sigma_thresholds(df, 'memory_usage_percent')
print(mem_comparison.to_string(index=False))
```

### 练习 2: 滑动窗口 3-Sigma 检测

```python
def sliding_window_3sigma(data, column_name, window_size=60):
    """
    使用滑动窗口进行 3-Sigma 检测
    更适合检测局部异常
    
    参数:
        data: 输入 DataFrame
        column_name: 要检测的列名
        window_size: 滑动窗口大小（默认 60 个时间点）
    """
    data_copy = data.copy()
    data_copy['rolling_mean'] = data[column_name].rolling(window=window_size).mean()
    data_copy['rolling_std'] = data[column_name].rolling(window=window_size).std()
    
    # 动态上下界
    data_copy['upper_bound'] = data_copy['rolling_mean'] + 3 * data_copy['rolling_std']
    data_copy['lower_bound'] = data_copy['rolling_mean'] - 3 * data_copy['rolling_std']
    
    # 检测异常
    data_copy['is_anomaly'] = (
        (data[column_name] < data_copy['lower_bound']) | 
        (data[column_name] > data_copy['upper_bound'])
    )
    
    return data_copy

# 应用滑动窗口检测
df_sliding = sliding_window_3sigma(df, 'cpu_usage_percent', window_size=60)

# 统计滑动窗口检测结果
sliding_anomalies = df_sliding[df_sliding['is_anomaly']]
print(f"\n滑动窗口 3-Sigma 检测到的 CPU 异常数量：{len(sliding_anomalies)}")
print(f"异常率：{len(sliding_anomalies)/len(df_sliding)*100:.2f}%")
```

## 6. 实验总结

### 关键要点
1. **3-Sigma 原则**：基于正态分布假设，超过±3σ 的点视为异常
2. **适用场景**：适用于相对稳定的指标，如 CPU、内存使用率
3. **优点**：简单快速，无需训练
4. **局限**：对非平稳序列效果不佳，需要数据近似正态分布

### 调优建议
- 根据实际业务调整 Sigma 阈值（2.5-3.5 之间）
- 对于有明显趋势的数据，使用滑动窗口方法
- 结合多个指标综合判断（如 CPU+ 内存 + 磁盘）
- 定期重新计算均值和标准差以适应数据变化

### 下一步
- 尝试其他统计方法（如移动平均线、分位数）
- 对比机器学习方法（Isolation Forest、One-Class SVM）
- 将检测结果接入告警系统
