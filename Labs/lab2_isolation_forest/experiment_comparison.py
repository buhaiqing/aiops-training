#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验对比：不同 contamination 参数对 Isolation Forest 检测结果的影响

使用方法:
    python experiment_comparison.py
    
说明:
    该脚本会运行多次实验，每次使用不同的 contamination 值
    所有实验结果会自动记录到 MLflow，方便在 UI 中对比
"""

import numpy as np
import mlflow
from mlflow_config import MLflowConfig
from main import (
    load_and_prepare_data, 
    train_isolation_forest, 
    detect_anomalies,
    analyze_feature_importance
)


def run_parameter_comparison():
    """运行不同参数的对比实验"""
    
    print("=" * 80)
    print("Isolation Forest 参数对比实验")
    print("=" * 80)
    print("")
    
    # 设置 MLflow 实验
    print("正在初始化 MLflow...")
    experiment_id = MLflowConfig.setup()
    print(f"✓ MLflow 实验已设置：{MLflowConfig.EXPERIMENT_NAME}")
    print(f"  跟踪 URI: {MLflowConfig.TRACKING_URI}")
    print("")
    
    # 定义要测试的 contamination 值
    contamination_values = [0.01, 0.02, 0.025, 0.03, 0.05]
    
    # 加载数据（只加载一次）
    print("正在加载数据...")
    df, X, timestamps, feature_cols = load_and_prepare_data()
    print(f"✓ 数据加载完成：{len(df)} 个样本")
    print("")
    
    # 存储实验结果
    results = []
    
    # 遍历每个 contamination 值
    for cont in contamination_values:
        print(f"\n{'='*80}")
        print(f"运行实验：contamination = {cont}")
        print(f"{'='*80}")
        
        run_name = f"isolation_forest_contamination_{cont}"
        
        with mlflow.start_run(run_name=run_name):
            try:
                # 1. 记录超参数
                params = MLflowConfig.DEFAULT_PARAMS.copy()
                params['contamination'] = cont
                mlflow.log_params(params)
                
                # 2. 训练模型
                model, scaler, X_scaled = train_isolation_forest(X, contamination=cont)
                
                # 3. 检测异常
                predictions, scores = detect_anomalies(model, X_scaled, timestamps)
                
                # 4. 计算并记录指标
                n_total = len(predictions)
                n_anomalies = np.sum(predictions == -1)
                anomaly_rate = n_anomalies / n_total * 100
                
                # 记录核心指标
                mlflow.log_metric("contamination", cont)
                mlflow.log_metric("total_samples", n_total)
                mlflow.log_metric("detected_anomalies", n_anomalies)
                mlflow.log_metric("anomaly_rate", anomaly_rate)
                mlflow.log_metric("avg_anomaly_score", float(scores.mean()))
                mlflow.log_metric("min_anomaly_score", float(scores.min()))
                mlflow.log_metric("max_anomaly_score", float(scores.max()))
                
                # 记录额外指标
                mlflow.log_metric("score_std", float(scores.std()))
                mlflow.log_metric("score_median", float(np.median(scores)))
                
                # 5. 添加标签
                mlflow.set_tag("experiment.type", "parameter_comparison")
                mlflow.set_tag("algorithm", "IsolationForest")
                mlflow.set_tag("parameter.tested", "contamination")
                
                # 6. 保存结果
                result = {
                    'contamination': cont,
                    'detected_anomalies': int(n_anomalies),
                    'anomaly_rate': round(anomaly_rate, 2),
                    'avg_score': round(float(scores.mean()), 4),
                    'min_score': round(float(scores.min()), 4),
                    'max_score': round(float(scores.max()), 4)
                }
                results.append(result)
                
                print(f"\n✓ 实验完成:")
                print(f"  - 检测到的异常数：{n_anomalies}")
                print(f"  - 异常率：{anomaly_rate:.2f}%")
                print(f"  - 平均异常分数：{scores.mean():.4f}")
                
            except Exception as e:
                print(f"✗ 实验失败：{e}")
                mlflow.log_param("error", str(e))
                continue
    
    # 打印汇总结果
    print("\n" + "=" * 80)
    print("实验结果汇总")
    print("=" * 80)
    print("")
    
    # 创建结果表格
    print(f"{'Contamination':<15} {'异常数量':<12} {'异常率 (%)':<12} {'平均分数':<12} {'最小分数':<12} {'最大分数':<12}")
    print("-" * 85)
    for r in results:
        print(f"{r['contamination']:<15} {r['detected_anomalies']:<12} {r['anomaly_rate']:<12} "
              f"{r['avg_score']:<12} {r['min_score']:<12} {r['max_score']:<12}")
    
    print("")
    print("=" * 80)
    print("所有实验完成！")
    print("=" * 80)
    print("")
    print("下一步操作:")
    print("  1. 访问 MLflow UI 查看详细的实验对比")
    print("     - Docker 模式：http://localhost:5000")
    print("     - 本地模式：http://localhost:5000")
    print("")
    print("  2. 在 MLflow UI 中:")
    print("     - 勾选多个 Run 记录进行对比")
    print("     - 查看指标趋势图")
    print("     - 分析不同参数对检测结果的影响")
    print("")
    print("  3. 选择最佳的 contamination 参数:")
    print("     - 根据业务需求调整异常检测的敏感度")
    print("     - 平衡误报率和漏报率")
    print("")
    
    return results


if __name__ == '__main__':
    results = run_parameter_comparison()
