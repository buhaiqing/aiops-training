#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MLflow 配置模块
集中管理 MLflow 实验配置
"""

import os
from pathlib import Path


class MLflowConfig:
    """MLflow 配置类"""
    
    # 实验名称
    EXPERIMENT_NAME = "lab2_isolation_forest_anomaly_detection"
    
    # MLflow 跟踪服务器 URI
    # 本地开发环境使用 Docker 时设置为：http://localhost:5000
    # 默认使用本地文件存储
    TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
    
    # Artifact 存储路径
    ARTIFACT_PATH = os.getenv("MLFLOW_ARTIFACT_PATH", "./mlruns/artifacts")
    
    # 模型保存路径
    MODEL_PATH = "isolation_forest_model"
    
    # 默认超参数
    DEFAULT_PARAMS = {
        "n_estimators": 100,
        "max_samples": "auto",
        "contamination": 0.025,
        "random_state": 42,
        "n_jobs": -1
    }
    
    # 要追踪的指标列表
    METRICS_TO_TRACK = [
        "anomaly_rate",
        "avg_anomaly_score",
        "min_anomaly_score",
        "max_anomaly_score",
        "total_samples",
        "detected_anomalies"
    ]
    
    @classmethod
    def setup(cls):
        """设置 MLflow 环境"""
        import mlflow
        
        # 设置跟踪 URI
        mlflow.set_tracking_uri(cls.TRACKING_URI)
        
        # 设置或创建实验
        experiment = mlflow.get_experiment_by_name(cls.EXPERIMENT_NAME)
        if experiment is None:
            experiment_id = mlflow.create_experiment(
                cls.EXPERIMENT_NAME,
                artifact_location=f"file://{Path(cls.ARTIFACT_PATH).absolute()}"
            )
        else:
            experiment_id = experiment.experiment_id
        
        mlflow.set_experiment(experiment_id=experiment_id)
        
        return experiment_id
    
    @classmethod
    def get_tracking_info(cls):
        """获取 MLflow 跟踪信息"""
        return {
            "experiment_name": cls.EXPERIMENT_NAME,
            "tracking_uri": cls.TRACKING_URI,
            "artifact_path": cls.ARTIFACT_PATH,
            "model_path": cls.MODEL_PATH
        }
