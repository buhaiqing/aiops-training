#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 2: Isolation Forest 检测多维指标异常
主程序：使用 Isolation Forest 进行多维异常检测
集成 MLflow 进行实验追踪和模型管理
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report, confusion_matrix
import mlflow
import mlflow.sklearn
from mlflow_config import MLflowConfig

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def load_and_prepare_data(data_file='multidim_monitoring_data.csv'):
    """加载并准备数据"""
    df = pd.read_csv(data_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 特征列
    feature_cols = [
        'cpu_usage_percent',
        'memory_usage_percent',
        'disk_io_percent',
        'network_traffic_mbps',
        'response_time_ms'
    ]
    
    X = df[feature_cols].values
    timestamps = df['timestamp'].values
    
    return df, X, timestamps, feature_cols


def train_isolation_forest(X, contamination=0.025):
    """
    训练 Isolation Forest 模型
    
    参数:
        X: 特征矩阵
        contamination: 异常点比例估计值（默认 2.5%）
    
    返回:
        model: 训练好的模型
    """
    print("=" * 60)
    print("训练 Isolation Forest 模型")
    print("=" * 60)
    
    # 数据标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 创建并训练 Isolation Forest 模型
    model = IsolationForest(
        n_estimators=100,        # 树的数量
        max_samples='auto',      # 每棵树使用的样本数
        contamination=contamination,  # 异常点比例
        random_state=42,
        n_jobs=-1               # 使用所有 CPU 核心
    )
    
    model.fit(X_scaled)
    
    print(f"✓ 模型训练完成")
    print(f"  - 树的数量：{model.n_estimators}")
    print(f"  - 异常点比例估计：{contamination*100}%")
    print("")
    
    return model, scaler, X_scaled


def detect_anomalies(model, X_scaled, timestamps):
    """
    使用训练好的模型检测异常
    
    返回:
        predictions: 预测结果 (1=正常，-1=异常)
        scores: 异常分数（越负越异常）
    """
    # 预测
    predictions = model.predict(X_scaled)
    
    # 计算异常分数
    scores = model.decision_function(X_scaled)
    
    # 统计结果
    n_total = len(predictions)
    n_anomalies = np.sum(predictions == -1)
    anomaly_rate = n_anomalies / n_total * 100
    
    print("=" * 60)
    print("Isolation Forest 异常检测结果")
    print("=" * 60)
    print(f"总样本数：{n_total}")
    print(f"检测到的异常点数：{n_anomalies}")
    print(f"异常率：{anomaly_rate:.2f}%")
    print(f"平均异常分数：{scores.mean():.4f}")
    print(f"最小异常分数：{scores.min():.4f}")
    print(f"最大异常分数：{scores.max():.4f}")
    print("")
    
    return predictions, scores


def visualize_results(df, X_scaled, predictions, scores, timestamps, feature_cols):
    """可视化检测结果"""
    
    # 创建图形
    fig = plt.figure(figsize=(20, 12))
    
    # 子图 1: 异常分数分布
    ax1 = plt.subplot(2, 3, 1)
    plt.hist(scores, bins=50, alpha=0.7, color='steelblue', edgecolor='black')
    plt.axvline(x=0, color='red', linestyle='--', linewidth=2, label='异常阈值')
    plt.xlabel('异常分数')
    plt.ylabel('频数')
    plt.title('异常分数分布直方图')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 子图 2: 异常点时间分布
    ax2 = plt.subplot(2, 3, 2)
    anomaly_mask = predictions == -1
    plt.scatter(timestamps[~anomaly_mask], scores[~anomaly_mask], 
                s=10, alpha=0.3, label='正常', color='green')
    plt.scatter(timestamps[anomaly_mask], scores[anomaly_mask], 
                s=30, alpha=0.8, label='异常', color='red', marker='x')
    plt.axhline(y=0, color='red', linestyle='--', linewidth=2)
    plt.xlabel('时间')
    plt.ylabel('异常分数')
    plt.title('异常点时间分布')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    # 子图 3: PCA 降维可视化
    ax3 = plt.subplot(3, 3, 3)
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    ax3.scatter(X_pca[~anomaly_mask, 0], X_pca[~anomaly_mask, 1], 
                s=10, alpha=0.3, label='正常', color='green')
    ax3.scatter(X_pca[anomaly_mask, 0], X_pca[anomaly_mask, 1], 
                s=30, alpha=0.8, label='异常', color='red', marker='x')
    ax3.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
    ax3.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
    ax3.set_title('PCA 降维后的异常分布')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 子图 4-8: 各指标的异常点分布 (3x3 网格)
    for i, col in enumerate(feature_cols):
        ax = plt.subplot(3, 3, i+4)
        values = df[col].values
        
        ax.plot(timestamps, values, alpha=0.6, linewidth=1, label='正常值', color='steelblue')
        ax.scatter(timestamps[anomaly_mask], values[anomaly_mask], 
                    s=50, alpha=0.8, label='异常点', color='red', marker='o', zorder=5)
        
        ax.set_xlabel('时间')
        ax.set_ylabel(col.replace('_', ' ').title())
        ax.set_title(f'{col.replace("_", " ").title()} - 异常点分布')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('isolation_forest_results.png', dpi=300, bbox_inches='tight')
    print("\n✓ 可视化结果已保存到：isolation_forest_results.png")
    plt.show()


def analyze_feature_importance(model, X_scaled, feature_cols):
    """分析特征对异常检测的贡献"""
    print("=" * 60)
    print("特征重要性分析")
    print("=" * 60)
    
    # 计算每个特征的均值和标准差贡献
    feature_stats = []
    for i, col in enumerate(feature_cols):
        mean_val = np.abs(X_scaled[:, i]).mean()
        std_val = X_scaled[:, i].std()
        feature_stats.append({
            'Feature': col,
            'Mean Abs Value': mean_val,
            'Std Dev': std_val
        })
    
    stats_df = pd.DataFrame(feature_stats)
    stats_df = stats_df.sort_values('Mean Abs Value', ascending=False)
    
    print(stats_df.to_string(index=False))
    print("")


def generate_anomaly_details(df, predictions, timestamps):
    """生成异常详情报告"""
    anomaly_mask = predictions == -1
    anomaly_df = df[anomaly_mask].copy()
    
    print("=" * 60)
    print("异常详情报告（前 10 个异常点）")
    print("=" * 60)
    
    if len(anomaly_df) == 0:
        print("未检测到异常")
        return
    
    # 显示前 10 个异常点的详细信息
    display_cols = ['timestamp', 'cpu_usage_percent', 'memory_usage_percent', 
                    'disk_io_percent', 'network_traffic_mbps', 'response_time_ms']
    
    for idx, row in anomaly_df.head(10).iterrows():
        print(f"\n异常点 #{idx}:")
        print(f"  时间：{row['timestamp']}")
        print(f"  CPU: {row['cpu_usage_percent']:.2f}%")
        print(f"  内存：{row['memory_usage_percent']:.2f}%")
        print(f"  磁盘 IO: {row['disk_io_percent']:.2f}%")
        print(f"  网络流量：{row['network_traffic_mbps']:.2f} Mbps")
        print(f"  响应时间：{row['response_time_ms']:.2f} ms")


def main():
    """主函数"""
    print("=" * 60)
    print("Lab 2: Isolation Forest 检测多维指标异常")
    print("=" * 60)
    print("")
    
    # 设置 MLflow
    print("正在初始化 MLflow 实验追踪...")
    experiment_id = MLflowConfig.setup()
    print(f"✓ MLflow 实验已设置：{MLflowConfig.EXPERIMENT_NAME}")
    print(f"  跟踪 URI: {MLflowConfig.TRACKING_URI}")
    print("")
    
    # 启动 MLflow run
    with mlflow.start_run(run_name=f"isolation_forest_contamination_0.025") as run:
        # 记录超参数
        mlflow.log_params(MLflowConfig.DEFAULT_PARAMS)
        
        # 1. 加载数据
        df, X, timestamps, feature_cols = load_and_prepare_data()
        print(f"✓ 数据加载完成")
        print(f"  - 样本数量：{len(df)}")
        print(f"  - 特征维度：{len(feature_cols)}")
        print(f"  - 特征列表：{', '.join(feature_cols)}")
        print("")
        
        # 2. 训练模型
        model, scaler, X_scaled = train_isolation_forest(X, contamination=0.025)
        
        # 3. 检测异常
        predictions, scores = detect_anomalies(model, X_scaled, timestamps)
        
        # 4. 记录关键指标到 MLflow
        n_total = len(predictions)
        n_anomalies = np.sum(predictions == -1)
        anomaly_rate = n_anomalies / n_total * 100
        
        mlflow.log_metric("total_samples", n_total)
        mlflow.log_metric("detected_anomalies", n_anomalies)
        mlflow.log_metric("anomaly_rate", anomaly_rate)
        mlflow.log_metric("avg_anomaly_score", float(scores.mean()))
        mlflow.log_metric("min_anomaly_score", float(scores.min()))
        mlflow.log_metric("max_anomaly_score", float(scores.max()))
        
        # 5. 保存模型和 scaler
        # 创建一个 Pipeline 以便同时保存 scaler 和 model
        from sklearn.pipeline import Pipeline
        pipeline = Pipeline([
            ('scaler', scaler),
            ('model', model)
        ])
        mlflow.sklearn.log_model(pipeline, MLflowConfig.MODEL_PATH)
        
        # 6. 特征重要性分析
        analyze_feature_importance(model, X_scaled, feature_cols)
        
        # 7. 生成异常详情报告
        generate_anomaly_details(df, predictions, timestamps)
        
        # 8. 可视化
        visualize_results(df, X_scaled, predictions, scores, timestamps, feature_cols)
        
        # 9. 记录可视化结果为 artifact
        mlflow.log_artifact("isolation_forest_results.png", "visualizations")
        
        # 10. 记录特征统计信息
        feature_stats = []
        for i, col in enumerate(feature_cols):
            mean_val = np.abs(X_scaled[:, i]).mean()
            std_val = X_scaled[:, i].std()
            feature_stats.append({
                'Feature': col,
                'Mean Abs Value': float(mean_val),
                'Std Dev': float(std_val)
            })
        stats_df = pd.DataFrame(feature_stats)
        stats_df.to_csv("feature_statistics.csv", index=False)
        mlflow.log_artifact("feature_statistics.csv", "data")
        
        # 11. 记录运行信息
        mlflow.set_tag("mlflow.runName", f"isolation_forest_contamination_0.025")
        mlflow.set_tag("experiment.type", "anomaly_detection")
        mlflow.set_tag("algorithm", "IsolationForest")
        
        print("=" * 60)
        print("MLflow 实验追踪完成！")
        print("=" * 60)
        print(f"Run ID: {run.info.run_id}")
        print(f"Run Name: {run.info.run_name}")
        print(f"Experiment ID: {experiment_id}")
        print(f"Artifact 路径：{run.info.artifact_uri}")
        print("")
    
    print("=" * 60)
    print("实验完成！")
    print("=" * 60)
    print("")
    print("下一步:")
    print("  1. 查看可视化结果图表")
    print("  2. 调整 contamination 参数观察效果")
    print("  3. 尝试不同的特征组合")
    print("  4. 对比其他算法（如 One-Class SVM）")
    print("  5. 访问 MLflow UI 查看实验详情和对比结果")
    print("")


if __name__ == '__main__':
    main()
