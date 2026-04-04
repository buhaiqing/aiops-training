#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 4: Prophet 时序预测与异常检测
学习目标：
1. 掌握 Prophet 模型的基本原理（趋势+季节性+节假日分解）
2. 学会使用 Prophet 进行时序预测和置信区间估计
3. 理解基于预测残差的异常检测方法
4. 能够评估预测模型性能（MAE、RMSE、MAPE）
5. 掌握时序数据的可视化分析方法
主程序：使用 Prophet 进行时序分解和异常检测
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def load_and_prepare_data(data_file='prophet_timeseries.csv'):
    """加载并准备数据"""
    df = pd.read_csv(data_file)
    df['ds'] = pd.to_datetime(df['ds'])
    
    # 分离训练集（去除最后几天用于验证）
    train_size = len(df) - 7
    train_data = df.iloc[:train_size].copy()
    test_data = df.iloc[train_size:].copy()
    
    print("=" * 60)
    print("数据加载完成")
    print("=" * 60)
    print(f"✓ 总样本数：{len(df)}")
    print(f"✓ 训练集大小：{len(train_data)}")
    print(f"✓ 测试集大小：{len(test_data)}")
    print(f"✓ 时间范围：{df['ds'].min()} 至 {df['ds'].max()}")
    print(f"✓ 真实异常点数量：{df['is_anomaly'].sum()}")
    print("")
    
    return df, train_data, test_data


def train_prophet_model(train_data, weekly_seasonality=True, yearly_seasonality=True):
    """
    训练 Prophet 模型
    
    参数:
        train_data: 训练数据
        weekly_seasonality: 是否启用周季节性
        yearly_seasonality: 是否启用年季节性
    
    返回:
        model: 训练好的 Prophet 模型
    """
    print("=" * 60)
    print("训练 Prophet 模型")
    print("=" * 60)
    
    # 创建模型
    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=weekly_seasonality,
        yearly_seasonality=yearly_seasonality,
        changepoint_prior_scale=0.05,  # 趋势变化点调节参数
        interval_width=0.95  # 预测区间宽度
    )
    
    print("✓ 模型配置:")
    print(f"  - 周季节性：{weekly_seasonality}")
    print(f"  - 年季节性：{yearly_seasonality}")
    print(f"  - 变点先验尺度：0.05")
    print(f"  - 预测区间宽度：95%")
    print("")
    
    # 训练模型
    print("开始训练...")
    model.fit(train_data)
    print("✓ 模型训练完成!")
    print("")
    
    return model


def make_predictions(model, test_data, forecast_periods=30):
    """
    使用模型进行预测
    
    参数:
        model: 训练好的模型
        test_data: 测试数据
        forecast_periods: 预测期数
    
    返回:
        forecast: 预测结果 DataFrame
    """
    print("=" * 60)
    print("执行预测")
    print("=" * 60)
    
    # 创建未来数据框
    future = model.make_future_dataframe(periods=forecast_periods)
    
    # 进行预测
    forecast = model.predict(future)
    
    print(f"✓ 预测期数：{forecast_periods} 天")
    print(f"✓ 预测结果形状：{forecast.shape}")
    print("")
    
    return forecast


def detect_anomalies(forecast, actual_values, threshold_multiplier=2.5):
    """
    基于预测残差检测异常
    
    参数:
        forecast: 预测结果
        actual_values: 实际值
        threshold_multiplier: 阈值倍数（标准差的倍数）
    
    返回:
        anomaly_scores: 异常分数数组
        is_anomaly: 布尔数组，标记是否为异常
    """
    print("=" * 60)
    print("异常检测")
    print("=" * 60)
    
    # 只取与实际值对应的部分
    y_pred = forecast['yhat'].values[-len(actual_values):]
    y_upper = forecast['yhat_upper'].values[-len(actual_values):]
    y_lower = forecast['yhat_lower'].values[-len(actual_values):]
    
    # 计算残差
    residuals = actual_values - y_pred
    
    # 计算标准化残差
    residual_std = np.std(residuals)
    z_scores = residuals / residual_std
    
    # 动态阈值
    dynamic_threshold = threshold_multiplier * residual_std
    
    # 标记异常点
    is_anomaly = (np.abs(z_scores) > threshold_multiplier) | \
                 (actual_values > y_upper) | \
                 (actual_values < y_lower)
    
    # 异常分数（绝对值越大越异常）
    anomaly_scores = np.abs(z_scores)
    
    n_detected = np.sum(is_anomaly)
    detection_rate = n_detected / len(actual_values) * 100
    
    print(f"✓ 检测方法：基于预测残差 + 置信区间")
    print(f"✓ 阈值倍数：{threshold_multiplier}")
    print(f"✓ 检测到的异常点数量：{n_detected}")
    print(f"✓ 检出率：{detection_rate:.2f}%")
    print("")
    
    return anomaly_scores, is_anomaly


def evaluate_model_performance(actual_values, predicted_values):
    """评估模型性能"""
    mae = mean_absolute_error(actual_values, predicted_values)
    rmse = np.sqrt(mean_squared_error(actual_values, predicted_values))
    mape = np.mean(np.abs((actual_values - predicted_values) / actual_values)) * 100
    
    print("=" * 60)
    print("模型性能评估")
    print("=" * 60)
    print(f"✓ 平均绝对误差 (MAE):  {mae:.4f}")
    print(f"✓ 均方根误差 (RMSE):   {rmse:.4f}")
    print(f"✓ 平均绝对百分比误差 (MAPE): {mape:.2f}%")
    print("")
    
    return {'mae': mae, 'rmse': rmse, 'mape': mape}


def visualize_results(model, forecast, actual_data, anomaly_scores, is_anomaly):
    """可视化检测结果"""
    
    fig = plt.figure(figsize=(20, 12))
    
    # 子图 1: Prophet 组件分解
    ax1 = plt.subplot(3, 2, 1)
    try:
        model.plot_components(forecast)
        plt.suptitle('Prophet 模型组件分解', fontsize=14, fontweight='bold')
    except Exception as e:
        print(f"⚠️  无法使用 plot_components，手动绘制组件：{e}")
        ax1.plot(forecast['ds'], forecast['trend'], label='趋势', linewidth=2)
        if 'weekly' in forecast.columns:
            ax1.plot(forecast['ds'], forecast['weekly'], label='周季节性', linestyle='--')
        if 'yearly' in forecast.columns:
            ax1.plot(forecast['ds'], forecast['yearly'], label='年季节性', linestyle=':')
        ax1.set_title('Prophet 模型组件分解', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    
    # 子图 2: 实际值 vs 预测值
    ax2 = plt.subplot(3, 2, 2)
    actual_dates = actual_data['ds'].values
    actual_values = actual_data['y'].values
    
    # 取预测结果中与实际值对应的部分
    forecast_actual = forecast.iloc[-len(actual_values):]
    pred_values = forecast_actual['yhat'].values
    upper = forecast_actual['yhat_upper'].values
    lower = forecast_actual['yhat_lower'].values
    
    ax2.plot(actual_dates, actual_values, linewidth=2, label='实际值', color='steelblue')
    ax2.plot(actual_dates, pred_values, linewidth=2, label='预测值', color='coral', linestyle='--')
    ax2.fill_between(actual_dates.flatten(), lower.flatten(), upper.flatten(), 
                     alpha=0.3, color='gray', label='95% 置信区间')
    
    # 标记异常点
    ax2.scatter(actual_dates[is_anomaly], actual_values[is_anomaly],
                c='red', s=100, marker='x', label='异常点', zorder=5, linewidth=3)
    
    ax2.set_xlabel('日期')
    ax2.set_ylabel('CPU 使用率 (%)')
    ax2.set_title('实际值 vs 预测值对比', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    # 子图 3: 残差分析
    ax3 = plt.subplot(3, 2, 3)
    residuals = actual_values - pred_values
    ax3.plot(actual_dates, residuals, linewidth=2, color='green')
    ax3.axhline(y=0, color='black', linestyle='--', linewidth=1)
    ax3.axhline(y=2*np.std(residuals), color='red', linestyle='--', linewidth=1.5, label='±2σ')
    ax3.axhline(y=-2*np.std(residuals), color='red', linestyle='--', linewidth=1.5)
    ax3.fill_between(actual_dates.flatten(), -2*np.std(residuals), 2*np.std(residuals), 
                     alpha=0.2, color='red')
    ax3.set_xlabel('日期')
    ax3.set_ylabel('残差')
    ax3.set_title('预测残差分析', fontsize=12, fontweight='bold')
    ax3.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    # 子图 4: 异常分数分布
    ax4 = plt.subplot(3, 2, 4)
    ax4.bar(range(len(anomaly_scores)), anomaly_scores, color='steelblue', alpha=0.7)
    ax4.axhline(y=2.5, color='red', linestyle='--', linewidth=2, label='异常阈值')
    ax4.set_xlabel('时间索引')
    ax4.set_ylabel('异常分数 (Z-Score)')
    ax4.set_title('异常分数分布', fontsize=12, fontweight='bold')
    ax4.legend(loc='upper right')
    ax4.grid(True, alpha=0.3)
    
    # 子图 5: 异常点详细标记
    ax5 = plt.subplot(3, 2, 5)
    ax5.plot(actual_dates, actual_values, linewidth=2, label='实际值', color='steelblue', alpha=0.5)
    
    # 高亮显示异常区域
    for i in range(len(is_anomaly)):
        if is_anomaly[i]:
            ax5.axvspan(actual_dates[max(0, i-1)],
                       actual_dates[min(i+1, len(is_anomaly)-1)],
                       alpha=0.3, color='red')
    
    ax5.scatter(actual_dates[is_anomaly], actual_values[is_anomaly],
                c='red', s=150, marker='o', label='异常点', zorder=5, edgecolors='black')
    
    ax5.set_xlabel('日期')
    ax5.set_ylabel('CPU 使用率 (%)')
    ax5.set_title('异常点时空分布', fontsize=12, fontweight='bold')
    ax5.legend(loc='upper right')
    ax5.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    # 子图 6: 预测趋势
    ax6 = plt.subplot(3, 2, 6)
    try:
        model.plot(forecast, ax=ax6)
    except Exception:
        ax6.plot(forecast['ds'], forecast['yhat'], label='预测值', linewidth=2)
        ax6.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'],
                        alpha=0.3, color='gray')
    ax6.scatter(actual_dates[is_anomaly], actual_values[is_anomaly],
                c='red', s=100, marker='x', label='异常点', zorder=5, linewidth=3)
    ax6.legend(loc='upper right')
    ax6.set_title('Prophet 长期预测趋势', fontsize=12, fontweight='bold')
    ax6.set_xlabel('日期')
    ax6.set_ylabel('CPU 使用率 (%)')
    
    plt.tight_layout()
    plt.savefig('prophet_anomaly_detection_results.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ 可视化结果已保存到：prophet_anomaly_detection_results.png")
    plt.show()


def generate_anomaly_report(actual_data, anomaly_scores, is_anomaly, top_n=5):
    """生成异常详情报告"""
    
    print("=" * 60)
    print("异常详情报告")
    print("=" * 60)
    
    anomaly_indices = np.where(is_anomaly)[0]
    
    if len(anomaly_indices) == 0:
        print("未检测到异常")
        return
    
    print(f"\n共发现 {len(anomaly_indices)} 个异常点\n")
    print(f"Top {top_n} 严重异常点:")
    print("-" * 60)
    
    # 按异常分数排序
    sorted_indices = np.argsort(anomaly_scores[is_anomaly])[::-1][:top_n]
    
    for rank, idx in enumerate(sorted_indices, 1):
        actual_idx = anomaly_indices[idx]
        timestamp = actual_data.iloc[actual_idx]['ds']
        value = actual_data.iloc[actual_idx]['y']
        score = anomaly_scores[actual_idx]
        
        print(f"#{rank}: 时间={timestamp.strftime('%Y-%m-%d')}, "
              f"值={value:.2f}%, 异常分数={score:.4f}")


def main():
    """主函数"""
    print("=" * 60)
    print("Lab 4: Prophet 时序预测与异常检测")
    print("=" * 60)
    print("")
    
    # 1. 加载数据
    df, train_data, test_data = load_and_prepare_data()
    
    # 2. 训练模型
    model = train_prophet_model(train_data, weekly_seasonality=True, yearly_seasonality=True)
    
    # 3. 执行预测
    forecast = make_predictions(model, test_data, forecast_periods=30)
    
    # 4. 评估模型性能
    actual_test_values = test_data['y'].values
    predicted_test_values = forecast['yhat'].values[-len(actual_test_values):]
    metrics = evaluate_model_performance(actual_test_values, predicted_test_values)
    
    # 5. 异常检测
    anomaly_scores, is_anomaly = detect_anomalies(forecast, actual_test_values, threshold_multiplier=2.5)
    
    # 6. 生成异常报告
    generate_anomaly_report(test_data, anomaly_scores, is_anomaly, top_n=5)
    
    # 7. 可视化
    visualize_results(model, forecast, test_data, anomaly_scores, is_anomaly)
    
    print("=" * 60)
    print("实验完成！")
    print("=" * 60)
    print("")
    print("输出文件:")
    print("  - prophet_anomaly_detection_results.png: 检测结果可视化")
    print("  - prophet_forecast_full.csv: 完整预测结果")
    print("")
    print("下一步:")
    print("  1. 分析可视化结果图表")
    print("  2. 调整 threshold_multiplier 优化检测效果")
    print("  3. 对比 LSTM 等其他方法")
    print("")
    
    # 保存完整预测结果
    forecast.to_csv('prophet_forecast_full.csv', index=False)
    print("✓ 完整预测结果已保存到：prophet_forecast_full.csv")


if __name__ == '__main__':
    main()
