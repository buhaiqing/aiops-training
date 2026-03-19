#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 7: 数据加载层
实现通用的数据加载和缓存机制
"""

import json
import asyncio
import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar, Generic, Optional, Dict, Any, List
from datetime import datetime, timedelta
from functools import lru_cache

from logger import LoggerMixin, agent_logger
from types import AlertLoadError, RunbookLoadError
from constants import DEFAULT_ENCODING


T = TypeVar("T")


class DataLoader(ABC, Generic[T], LoggerMixin):
    """数据加载器抽象基类"""

    def __init__(self, cache_enabled: bool = True, cache_ttl: int = 300):
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, tuple[T, datetime]] = {}

    def _get_cache_key(self, filepath: Path) -> str:
        """生成缓存键"""
        mtime = filepath.stat().st_mtime if filepath.exists() else 0
        return hashlib.md5(f"{filepath}:{mtime}".encode()).hexdigest()

    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        if not self.cache_enabled or key not in self._cache:
            return False

        _, timestamp = self._cache[key]
        return datetime.now() - timestamp < timedelta(seconds=self.cache_ttl)

    def _get_from_cache(self, key: str) -> Optional[T]:
        """从缓存获取数据"""
        if self._is_cache_valid(key):
            data, _ = self._cache[key]
            return data
        return None

    def _set_cache(self, key: str, data: T):
        """设置缓存"""
        if self.cache_enabled:
            self._cache[key] = (data, datetime.now())

    @abstractmethod
    def _parse(self, raw_data: Any) -> T:
        """解析原始数据"""
        pass

    def load(self, filepath: Path) -> T:
        """加载数据（带缓存）"""
        self.log_operation("LOAD", file=str(filepath))

        if not filepath.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")

        cache_key = self._get_cache_key(filepath)
        cached = self._get_from_cache(cache_key)

        if cached is not None:
            self.logger.debug(f"缓存命中: {filepath}")
            return cached

        try:
            with open(filepath, "r", encoding=DEFAULT_ENCODING) as f:
                raw_data = json.load(f)

            parsed = self._parse(raw_data)
            self._set_cache(cache_key, parsed)

            self.log_operation(
                "LOAD_SUCCESS", file=str(filepath), size=len(json.dumps(raw_data))
            )
            return parsed

        except json.JSONDecodeError as e:
            self.log_error(e, f"JSON解析失败: {filepath}")
            raise AlertLoadError(f"JSON解析失败: {filepath}") from e
        except Exception as e:
            self.log_error(e, f"加载失败: {filepath}")
            raise AlertLoadError(f"加载失败: {filepath}") from e

    async def load_async(self, filepath: Path) -> T:
        """异步加载数据"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.load, filepath)

    def invalidate_cache(self, filepath: Optional[Path] = None):
        """清除缓存"""
        if filepath is None:
            self._cache.clear()
            self.logger.debug("清除所有缓存")
        else:
            cache_key = self._get_cache_key(filepath)
            self._cache.pop(cache_key, None)
            self.logger.debug(f"清除缓存: {filepath}")


class AlertLoader(DataLoader[List[dict]]):
    """告警数据加载器"""

    def _parse(self, raw_data: Any) -> List[dict]:
        if not isinstance(raw_data, list):
            raise ValueError("告警数据必须是列表格式")
        return raw_data


class ScenarioLoader(DataLoader[List[dict]]):
    """场景数据加载器"""

    def _parse(self, raw_data: Any) -> List[dict]:
        if not isinstance(raw_data, list):
            raise ValueError("场景数据必须是列表格式")
        return raw_data


class RunbookLoader(DataLoader[Dict[str, dict]]):
    """运维手册加载器"""

    def __init__(self, cache_enabled: bool = True, cache_ttl: int = 300):
        super().__init__(cache_enabled, cache_ttl)
        self.index_file = "index.json"

    def _parse(self, raw_data: Any) -> Dict[str, dict]:
        if not isinstance(raw_data, dict):
            raise ValueError("运维手册必须是字典格式")
        return raw_data

    def load_directory(self, directory: Path) -> Dict[str, dict]:
        """加载目录中的所有运维手册"""
        self.log_operation("LOAD_RUNBOOKS", dir=str(directory))

        if not directory.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")

        runbooks = {}

        for filepath in directory.glob("*.json"):
            if filepath.name == self.index_file:
                continue

            try:
                data = self.load(filepath)
                if "runbook_id" in data:
                    runbooks[data["runbook_id"]] = data
                    self.logger.debug(f"加载运维手册: {data['runbook_id']}")
            except Exception as e:
                self.logger.warning(f"跳过无效运维手册: {filepath} - {e}")

        self.log_operation("LOAD_RUNBOOKS_SUCCESS", count=len(runbooks))
        return runbooks

    async def load_directory_async(self, directory: Path) -> Dict[str, dict]:
        """异步加载目录"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.load_directory, directory)
