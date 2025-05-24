"""
---------------------------------------------------------------
File name:                  scan.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                扫描API路由控制器，提供端口扫描相关的API端点
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建;
                            2025/05/23: 修复核心模块导入;
                            2025/05/24: 添加start和status路由;
----
"""

from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import asyncio
import uuid
import time

from ...schemas.scan import (
    ScanRequest, PortRangeRequest, BatchScanRequest, ScanResult,
    ScanStatistics, ScanTaskStatus, ScanConfigUpdate, ScanProfile
)
from ...schemas.common import SuccessResponse, ErrorResponse, Pagination
from ...core.port_scanner import PortScannerEngine
from ...config import settings

router = APIRouter()

# 全局任务存储（生产环境中应使用Redis或数据库）
_active_tasks: Dict[str, Dict] = {}
_scan_results: Dict[str, List[ScanResult]] = {}


@router.post("/single", response_model=SuccessResponse)
async def scan_single_port(request: ScanRequest):
    """扫描单个端口
    
    Args:
        request: 扫描请求参数
        
    Returns:
        SuccessResponse: 扫描结果
    """
    try:
        scanner = PortScannerEngine()
        result = await scanner.scan_port(
            host=request.target,
            port=request.port,
            protocol=request.protocol
        )
        
        return SuccessResponse(
            message="端口扫描完成",
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"扫描失败: {str(e)}"
        )


@router.post("/range", response_model=SuccessResponse)
async def scan_port_range(request: PortRangeRequest):
    """扫描端口范围
    
    Args:
        request: 端口范围扫描请求
        
    Returns:
        SuccessResponse: 扫描结果列表
    """
    try:
        scanner = PortScannerEngine()
        results = await scanner.scan_range(
            target=request.target,
            start_port=request.start_port,
            end_port=request.end_port,
            timeout=request.timeout,
            protocol=request.protocol,
            max_concurrent=request.max_concurrent
        )
        
        return SuccessResponse(
            message=f"端口范围扫描完成，共扫描 {len(results)} 个端口",
            data=results
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"范围扫描失败: {str(e)}"
        )


@router.post("/batch", response_model=SuccessResponse)
async def scan_batch(request: BatchScanRequest):
    """批量扫描
    
    Args:
        request: 批量扫描请求
        
    Returns:
        SuccessResponse: 扫描结果
    """
    try:
        scanner = PortScannerEngine()
        results = await scanner.scan_batch(
            targets=request.targets,
            ports=request.ports,
            timeout=request.timeout,
            protocol=request.protocol,
            max_concurrent=request.max_concurrent
        )
        
        return SuccessResponse(
            message=f"批量扫描完成，共扫描 {len(request.targets)} 个目标",
            data=results
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量扫描失败: {str(e)}"
        )


@router.post("/async", response_model=SuccessResponse)
async def start_async_scan(request: BatchScanRequest, background_tasks: BackgroundTasks):
    """启动异步扫描任务
    
    Args:
        request: 扫描请求
        background_tasks: 后台任务管理器
        
    Returns:
        SuccessResponse: 任务信息
    """
    task_id = str(uuid.uuid4())
    
    # 创建任务状态
    task_status = ScanTaskStatus(
        task_id=task_id,
        status="pending",
        progress=0.0,
        total_targets=len(request.targets),
        completed_targets=0,
        total_ports=len(request.ports),
        completed_ports=0
    )
    
    _active_tasks[task_id] = task_status.dict()
    
    # 添加后台任务
    background_tasks.add_task(
        _run_async_scan,
        task_id,
        request
    )
    
    return SuccessResponse(
        message="异步扫描任务已启动",
        data={"task_id": task_id, "status": "pending"}
    )


async def _run_async_scan(task_id: str, request: BatchScanRequest):
    """运行异步扫描任务
    
    Args:
        task_id: 任务ID
        request: 扫描请求
    """
    try:
        # 更新任务状态
        _active_tasks[task_id]["status"] = "running"
        _active_tasks[task_id]["started_at"] = time.time()
        
        scanner = PortScannerEngine()
        results = []
        
        total_scans = len(request.targets) * len(request.ports)
        completed_scans = 0
        
        for target in request.targets:
            for port in request.ports:
                try:
                    result = await scanner.scan_port(
                        host=target,
                        port=port,
                        protocol=request.protocol
                    )
                    results.append(result)
                    
                    completed_scans += 1
                    progress = (completed_scans / total_scans) * 100
                    
                    # 更新进度
                    _active_tasks[task_id]["progress"] = progress
                    _active_tasks[task_id]["completed_ports"] = completed_scans
                    
                except Exception as e:
                    # 记录错误但继续扫描
                    pass
        
        # 保存结果
        _scan_results[task_id] = results
        
        # 完成任务
        _active_tasks[task_id]["status"] = "completed"
        _active_tasks[task_id]["progress"] = 100.0
        _active_tasks[task_id]["completed_at"] = time.time()
        
    except Exception as e:
        _active_tasks[task_id]["status"] = "failed"
        _active_tasks[task_id]["error"] = str(e)


@router.get("/task/{task_id}", response_model=SuccessResponse)
async def get_task_status(task_id: str):
    """获取扫描任务状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        SuccessResponse: 任务状态
    """
    if task_id not in _active_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    return SuccessResponse(
        message="任务状态获取成功",
        data=_active_tasks[task_id]
    )


@router.get("/task/{task_id}/results", response_model=SuccessResponse)
async def get_task_results(task_id: str):
    """获取扫描任务结果
    
    Args:
        task_id: 任务ID
        
    Returns:
        SuccessResponse: 扫描结果
    """
    if task_id not in _active_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if _active_tasks[task_id]["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任务尚未完成"
        )
    
    results = _scan_results.get(task_id, [])
    
    return SuccessResponse(
        message="结果获取成功",
        data=results
    )


@router.delete("/task/{task_id}", response_model=SuccessResponse)
async def cancel_task(task_id: str):
    """取消扫描任务
    
    Args:
        task_id: 任务ID
        
    Returns:
        SuccessResponse: 取消结果
    """
    if task_id not in _active_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if _active_tasks[task_id]["status"] in ["completed", "failed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任务已结束，无法取消"
        )
    
    _active_tasks[task_id]["status"] = "cancelled"
    
    return SuccessResponse(
        message="任务已取消"
    )


@router.get("/tasks", response_model=SuccessResponse)
async def list_tasks(page: int = 1, page_size: int = 20):
    """获取扫描任务列表
    
    Args:
        page: 页码
        page_size: 每页大小
        
    Returns:
        SuccessResponse: 任务列表
    """
    tasks = list(_active_tasks.values())
    total_items = len(tasks)
    
    # 分页
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_tasks = tasks[start_idx:end_idx]
    
    pagination = Pagination(
        page=page,
        page_size=page_size,
        total_items=total_items
    )
    
    return SuccessResponse(
        message="任务列表获取成功",
        data={
            "tasks": page_tasks,
            "pagination": pagination.dict()
        }
    )


@router.get("/statistics/{task_id}", response_model=SuccessResponse)
async def get_scan_statistics(task_id: str):
    """获取扫描统计信息
    
    Args:
        task_id: 任务ID
        
    Returns:
        SuccessResponse: 统计信息
    """
    if task_id not in _scan_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="扫描结果不存在"
        )
    
    results = _scan_results[task_id]
    
    # 计算统计信息
    total_scans = len(results)
    open_ports = len([r for r in results if r.get("status") == "open"])
    closed_ports = len([r for r in results if r.get("status") == "closed"])
    filtered_ports = len([r for r in results if r.get("status") == "filtered"])
    timeout_ports = len([r for r in results if r.get("status") == "timeout"])
    error_ports = len([r for r in results if r.get("status") == "error"])
    
    statistics = ScanStatistics(
        total_scans=total_scans,
        open_ports=open_ports,
        closed_ports=closed_ports,
        filtered_ports=filtered_ports,
        timeout_ports=timeout_ports,
        error_ports=error_ports
    )
    
    return SuccessResponse(
        message="统计信息获取成功",
        data=statistics.dict()
    )


@router.post("/config", response_model=SuccessResponse)
async def update_scan_config(config: ScanConfigUpdate):
    """更新扫描配置
    
    Args:
        config: 配置更新请求
        
    Returns:
        SuccessResponse: 更新结果
    """
    # 这里应该实际更新配置
    # 暂时返回成功响应
    
    return SuccessResponse(
        message="扫描配置已更新",
        data=config.dict()
    )


@router.get("/config", response_model=SuccessResponse)
async def get_scan_config():
    """获取当前扫描配置
    
    Returns:
        SuccessResponse: 配置信息
    """
    network_settings = settings.get_network_tool_settings()
    
    return SuccessResponse(
        message="扫描配置获取成功",
        data=network_settings
    )


@router.post("/profiles", response_model=SuccessResponse)
async def create_scan_profile(profile: ScanProfile):
    """创建扫描配置模板
    
    Args:
        profile: 扫描配置模板
        
    Returns:
        SuccessResponse: 创建结果
    """
    # 这里应该保存到数据库
    # 暂时返回成功响应
    
    return SuccessResponse(
        message="扫描配置模板已创建",
        data=profile.dict()
    )


@router.get("/profiles", response_model=SuccessResponse)
async def list_scan_profiles():
    """获取扫描配置模板列表
    
    Returns:
        SuccessResponse: 模板列表
    """
    # 这里应该从数据库获取
    # 暂时返回空列表
    
    return SuccessResponse(
        message="配置模板列表获取成功",
        data=[]
    ) 


@router.post("/start", response_model=SuccessResponse)
async def start_scan(request: dict, background_tasks: BackgroundTasks):
    """启动端口扫描
    
    Args:
        request: 扫描配置
        background_tasks: 后台任务
        
    Returns:
        SuccessResponse: 扫描任务信息
    """
    try:
        scan_id = str(uuid.uuid4())
        
        # 解析端口
        ports = []
        if "ports" in request:
            port_spec = request["ports"]
            if isinstance(port_spec, str):
                # 处理端口范围表示法(如"1-1000,3389,8080-8090")
                parts = port_spec.split(',')
                for part in parts:
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        ports.extend(range(start, end + 1))
                    else:
                        try:
                            ports.append(int(part))
                        except ValueError:
                            pass
        
        # 创建扫描任务状态
        scan_status = {
            "scan_id": scan_id,
            "status": "running",
            "progress": 0,
            "total_ports": len(ports),
            "scanned_ports": 0,
            "found_ports": 0,
            "start_time": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_time": None
        }
        
        # 存储任务
        _active_tasks[scan_id] = scan_status
        _scan_results[scan_id] = []
        
        # 后台执行扫描
        background_tasks.add_task(
            _run_port_scan,
            scan_id=scan_id,
            target=request.get("target", ""),
            ports=ports,
            scan_type=request.get("scan_type", "tcp"),
            timeout=request.get("timeout", 3),
            max_threads=request.get("max_threads", 500)
        )
        
        return SuccessResponse(
            message="端口扫描已启动",
            data=scan_status
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动扫描失败: {str(e)}"
        )


@router.get("/status/{scan_id}", response_model=SuccessResponse)
async def get_scan_status(scan_id: str):
    """获取扫描状态
    
    Args:
        scan_id: 扫描任务ID
        
    Returns:
        SuccessResponse: 扫描状态
    """
    if scan_id not in _active_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="扫描任务不存在"
        )
    
    return SuccessResponse(
        message="扫描状态获取成功",
        data=_active_tasks[scan_id]
    )


@router.get("/results/{scan_id}", response_model=SuccessResponse)
async def get_scan_results(scan_id: str):
    """获取扫描结果
    
    Args:
        scan_id: 扫描任务ID
        
    Returns:
        SuccessResponse: 扫描结果
    """
    if scan_id not in _scan_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="扫描结果不存在"
        )
    
    return SuccessResponse(
        message="扫描结果获取成功",
        data=_scan_results[scan_id]
    )


@router.post("/stop/{scan_id}", response_model=SuccessResponse)
async def stop_scan(scan_id: str):
    """停止扫描
    
    Args:
        scan_id: 扫描任务ID
        
    Returns:
        SuccessResponse: 操作结果
    """
    if scan_id not in _active_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="扫描任务不存在"
        )
    
    # 更新任务状态
    _active_tasks[scan_id]["status"] = "cancelled"
    _active_tasks[scan_id]["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    return SuccessResponse(
        message="扫描已停止",
        data=_active_tasks[scan_id]
    )


async def _run_port_scan(scan_id: str, target: str, ports: List[int], scan_type: str, timeout: float, max_threads: int):
    """后台执行端口扫描
    
    Args:
        scan_id: 扫描任务ID
        target: 目标主机
        ports: 端口列表
        scan_type: 扫描类型
        timeout: 超时时间
        max_threads: 最大线程数
    """
    try:
        scanner = PortScannerEngine()
        
        total_ports = len(ports)
        completed_ports = 0
        found_ports = 0
        
        for port in ports:
            if _active_tasks[scan_id]["status"] == "cancelled":
                break
                
            try:
                result = await scanner.scan_port(
                    host=target,
                    port=port,
                    protocol=scan_type
                )
                
                # 保存结果
                if result:
                    scan_result = {
                        "scan_id": scan_id,
                        "target": target,
                        "port": port,
                        "status": result.get("status", "closed"),
                        "service": result.get("service", ""),
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    }
                    
                    _scan_results[scan_id].append(scan_result)
                    
                    if scan_result["status"] == "open":
                        found_ports += 1
            except Exception as e:
                # 记录扫描错误但继续扫描其他端口
                print(f"Error scanning port {port}: {str(e)}")
            
            completed_ports += 1
            progress = (completed_ports / total_ports) * 100 if total_ports > 0 else 100
            
            # 更新任务状态
            _active_tasks[scan_id]["scanned_ports"] = completed_ports
            _active_tasks[scan_id]["found_ports"] = found_ports
            _active_tasks[scan_id]["progress"] = progress
        
        # 扫描完成
        _active_tasks[scan_id]["status"] = "completed"
        _active_tasks[scan_id]["progress"] = 100
        _active_tasks[scan_id]["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
    except Exception as e:
        # 扫描失败
        _active_tasks[scan_id]["status"] = "failed"
        _active_tasks[scan_id]["error"] = str(e)
        _active_tasks[scan_id]["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")