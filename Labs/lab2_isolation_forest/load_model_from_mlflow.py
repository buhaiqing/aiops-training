#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 MLflow 加载已训练的 Isolation Forest 模型

使用方法:
    python load_model_from_mlflow.py
    
说明:
    该脚本演示如何从 MLflow 中加载之前训练并保存的模型
    可用于生产环境中的模型部署和复用
"""

import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from mlflow_config import MLflowConfig


def load_latest_model():
    """从 MLflow 加载最新的模型"""
    
    print("=" * 80)
    print("从 MLflow 加载 Isolation Forest 模型")
    print("=" * 80)
    print("")
    
    # 设置 MLflow
    print("正在初始化 MLflow...")
    MLflowConfig.setup()
    print(f"✓ MLflow 实验：{MLflowConfig.EXPERIMENT_NAME}")
    print("")
    
    # 获取最近的运行
    print("正在查找最近的实验运行...")
    client = mlflow.MlflowClient()
    experiment = client.get_experiment_by_name(MLflowConfig.EXPERIMENT_NAME)
    
    if experiment is None:
        print("✗ 未找到实验！请先运行 main.py 或 experiment_comparison.py")
        return None
    
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"],
        max_results=1
    )
    
    if not runs:
        print("✗ 未找到任何运行的实验！")
        return None
    
    run = runs[0]
    run_id = run.info.run_id
    run_name = run.info.run_name
    
    print(f"✓ 找到最近的运行:")
    print(f"  - Run ID: {run_id}")
    print(f"  - Run Name: {run_name}")
    print(f"  - 开始时间：{pd.Timestamp(run.info.start_time, unit='ms')}")
    print("")
    
    # 加载模型
    model_uri = f"runs:/{run_id}/{MLflowConfig.MODEL_PATH}"
    print(f"正在加载模型：{model_uri}")
    
    try:
        loaded_pipeline = mlflow.sklearn.load_model(model_uri)
        print(f"✓ 模型加载成功！")
        print("")
        
        # 显示模型信息
        print("模型信息:")
        print(f"  - 类型：{type(loaded_pipeline)}")
        print(f"  - 步骤：{loaded_pipeline.steps}")
        print("")
        
        # 提取 IsolationForest 模型
        isolation_forest_model = loaded_pipeline.named_steps['model']
        scaler = loaded_pipeline.named_steps['scaler']
        
        print("模型组件:")
        print(f"  - Scaler: {type(scaler).__name__}")
        print(f"  - Model: {type(isolation_forest_model).__name__}")
        print(f"  - n_estimators: {isolation_forest_model.n_estimators}")
        print(f"  - contamination: {isolation_forest_model.contamination}")
        print(f"  - random_state: {isolation_forest_model.random_state}")
        print("")
        
        return loaded_pipeline
        
    except Exception as e:
        print(f"✗ 模型加载失败：{e}")
        return None


def predict_with_loaded_model(pipeline, new_data_path=None):
    """使用加载的模型进行预测"""
    
    if pipeline is None:
        return
    
    print("=" * 80)
    print("使用加载的模型进行预测")
    print("=" * 80)
    print("")
    
    # 如果没有提供新数据，使用示例数据
    if new_data_path is None:
        print("使用示例数据进行预测...")
        # 生成一些示例数据
        np.random.seed(42)
        n_samples = 100
        
        # 模拟监控数据（与训练数据相同的特征）
        example_data = pd.DataFrame({
            'cpu_usage_percent': np.random.normal(60, 15, n_samples),
            'memory_usage_percent': np.random.normal(70, 10, n_samples),
            'disk_io_percent': np.random.normal(50, 12, n_samples),
            'network_traffic_mbps': np.random.normal(100, 25, n_samples),
            'response_time_ms': np.random.normal(200, 50, n_samples)
        })
        
        # 注入一些异常
        example_data.loc[10:14, 'cpu_usage_percent'] = 95  # CPU 异常高
        example_data.loc[20:24, 'memory_usage_percent'] = 92  # 内存异常高
        example_data.loc[30:34, 'response_time_ms'] = 500  # 响应时间异常
        
        print(f"✓ 生成了 {n_samples} 个示例数据点")
        print(f"  - 注入了 15 个异常点")
        print("")
        
    else:
        # 加载外部数据
        print(f"正在加载数据：{new_data_path}")
        example_data = pd.read_csv(new_data_path)
        print(f"✓ 加载了 {len(example_data)} 个数据点")
        print("")
    
    # 准备特征
    feature_cols = [
        'cpu_usage_percent',
        'memory_usage_percent',
        'disk_io_percent',
        'network_traffic_mbps',
        'response_time_ms'
    ]
    
    X_new = example_data[feature_cols].values
    
    # 预测
    print("正在进行预测...")
    predictions = pipeline.predict(X_new)
    scores = pipeline.decision_function(X_new)
    
    # 统计结果
    n_total = len(predictions)
    n_anomalies = np.sum(predictions == -1)
    anomaly_rate = n_anomalies / n_total * 100
    
    print(f"\n✓ 预测完成!")
    print(f"  - 总样本数：{n_total}")
    print(f"  - 检测到的异常数：{n_anomalies}")
    print(f"  - 异常率：{anomaly_rate:.2f}%")
    print(f"  - 平均异常分数：{scores.mean():.4f}")
    print("")
    
    # 显示异常详情
    if n_anomalies > 0:
        print("=" * 80)
        print("异常点详情（前 10 个）")
        print("=" * 80)
        
        anomaly_indices = np.where(predictions == -1)[0]
        
        for i, idx in enumerate(anomaly_indices[:10]):
            print(f"\n异常点 #{i+1} (索引：{idx}):")
            print(f"  异常分数：{scores[idx]:.4f}")
            for col in feature_cols:
                print(f"  {col}: {example_data.iloc[idx][col]:.2f}")
    
    print("")
    
    # 返回结果
    results = pd.DataFrame({
        'prediction': predictions,
        'anomaly_score': scores
    })
    
    return results


def list_all_runs():
    """列出所有实验运行记录"""
    
    print("=" * 80)
    print("查看所有实验运行记录")
    print("=" * 80)
    print("")
    
    # 设置 MLflow
    MLflowConfig.setup()
    client = mlflow.MlflowClient()
    experiment = client.get_experiment_by_name(MLflowConfig.EXPERIMENT_NAME)
    
    if experiment is None:
        print("✗ 未找到实验！")
        return
    
    # 获取所有运行
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"]
    )
    
    print(f"实验名称：{experiment.name}")
    print(f"运行总数：{len(runs)}")
    print("")
    
    print(f"{'Run Name':<40} {'Run ID':<35} {'Anomalies':<10} {'Rate (%)':<10} {'Timestamp':<20}")
    print("-" * 115)
    
    for run in runs:
        run_name = run.info.run_name or "N/A"
        run_id = run.info.run_id
        start_time = pd.Timestamp(run.info.start_time, unit='ms').strftime('%Y-%m-%d %H:%M')
        
        # 获取指标
        metrics = run.data.metrics
        detected_anomalies = metrics.get('detected_anomalies', 0)
        anomaly_rate = metrics.get('anomaly_rate', 0)
        
        print(f"{run_name:<40} {run_id:<35} {detected_anomalies:<10} {anomaly_rate:<10.2f} {start_time:<20}")
    
    print("")


if __name__ == '__main__':
    import sys
    
    print("=" * 80)
    print("MLflow 模型加载工具")
    print("=" * 80)
    print("")
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            # 列出所有运行
            list_all_runs()
            
        elif command == "load":
            # 加载最新模型并预测
            pipeline = load_latest_model()
            if pipeline:
                # 可以指定数据文件路径
                data_file = sys.argv[2] if len(sys.argv) > 2 else None
                predict_with_loaded_model(pipeline, data_file)
        
        else:
            print(f"未知命令：{command}")
            print("可用命令：list, load")
    else:
        # 默认行为：加载最新模型并预测
        pipeline = load_latest_model()
        if pipeline:
            predict_with_loaded_model(pipeline)
        
        print("\n提示:")
        print("  可用命令:")
        print("    python load_model_from_mlflow.py list   - 查看所有实验运行")
        print("    python load_model_from_mlflow.py load   - 加载最新模型并预测")
        print("    python load_model_from_mlflow.py load <data.csv> - 加载模型并对指定数据预测")
