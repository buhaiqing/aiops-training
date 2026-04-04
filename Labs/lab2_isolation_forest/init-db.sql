-- 初始化 MLflow PostgreSQL 数据库
-- 该脚本会在 PostgreSQL 容器首次启动时自动执行

-- 创建扩展（如果需要）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 设置时区
SET timezone = 'UTC';

-- 创建 MLflow 所需的表结构
-- MLflow 会自动创建表，这里可以添加一些优化配置

-- 设置连接数限制（可选）
ALTER DATABASE mlflow_db SET max_connections = 100;

-- 授予权限（确保 mlflow 用户有完整权限）
GRANT ALL PRIVILEGES ON DATABASE mlflow_db TO mlflow;
