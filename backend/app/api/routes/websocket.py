"""
---------------------------------------------------------------
File name:                  websocket.py
Author:                     Ignorant-lu
Date created:               2025/05/23
Description:                WebSocket API路由控制器，提供实时通信相关的API端点
----------------------------------------------------------------

Changed history:            
                            2025/05/23: 初始创建;
                            2025/05/23: 集成真实PING和扫描工具数据推送;
----
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import json
import uuid
import time
import asyncio
import logging

from ...schemas.common import SuccessResponse, ErrorResponse
from ...core.ping_tool import PingEngine
from ...core.port_scanner import PortScannerEngine

router = APIRouter()

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_info: Dict[str, Dict] = {}
        
        # 实时数据源
        self.ping_engine = PingEngine()
        self.port_scanner = PortScannerEngine()
        
        # 监控任务管理 - 添加停止信号
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.ping_stop_signals: Dict[str, asyncio.Event] = {}  # 添加PING停止信号

    async def connect(self, websocket: WebSocket, client_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if not client_id:
            client_id = str(uuid.uuid4())
        
        self.connection_info[client_id] = {
            "client_id": client_id,
            "websocket": websocket,
            "connected_at": time.time(),
            "last_activity": time.time()
        }
        
        return client_id

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # 从连接信息中移除并停止相关任务
        for client_id, info in list(self.connection_info.items()):
            if info["websocket"] == websocket:
                # 停止该客户端的所有PING任务
                self.stop_ping_for_client(client_id)
                del self.connection_info[client_id]
                break

    def stop_ping_for_client(self, client_id: str):
        """停止特定客户端的PING任务"""
        logging.info(f"尝试停止客户端 {client_id} 的PING")
        logging.info(f"当前停止信号字典键: {list(self.ping_stop_signals.keys())}")
        
        if client_id in self.ping_stop_signals:
            self.ping_stop_signals[client_id].set()
            logging.info(f"✅ 已为客户端 {client_id} 设置停止信号")
            del self.ping_stop_signals[client_id]
        else:
            logging.warning(f"❌ 客户端 {client_id} 没有找到对应的停止信号")
            logging.warning(f"可能的原因：1) 客户端ID不匹配 2) 停止信号已被删除 3) PING任务已结束")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_message_to_client(self, message: str, client_id: str):
        if client_id in self.connection_info:
            websocket = self.connection_info[client_id]["websocket"]
            await websocket.send_text(message)
            return True
        return False

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # 连接已断开，从列表中移除
                self.disconnect(connection)

    def get_connection_count(self):
        return len(self.active_connections)

    def get_all_connections(self):
        return [
            {
                "client_id": client_id,
                "connected_at": info["connected_at"],
                "last_activity": info["last_activity"]
            }
            for client_id, info in self.connection_info.items()
        ]

    async def start_ping_monitoring(self, websocket: WebSocket, target: str, 
                                  count: int = -1, interval: float = 1.0):
        """启动PING监控推送"""
        client_id_info = "[unknown]"
        for cid, info in self.connection_info.items():
            if info["websocket"] == websocket:
                client_id_info = cid
                break
        
        # 创建停止信号
        stop_signal = asyncio.Event()
        self.ping_stop_signals[client_id_info] = stop_signal
        
        logging.debug(f"[{client_id_info}] start_ping_monitoring: Called for target={target}, count={count}, interval={interval}")
        try:
            # 执行PING测试并实时推送结果
            duration = None if count == -1 else count * interval
            logging.debug(f"[{client_id_info}] start_ping_monitoring: Calculated duration={duration}")

            async for result in self.ping_engine.continuous_ping(
                host=target, 
                duration=duration,
                stop_signal=stop_signal
            ):
                # 检查停止信号
                if stop_signal.is_set():
                    logging.info(f"[{client_id_info}] start_ping_monitoring: Received stop signal for {target}")
                    break
                    
                # 检查WebSocket是否仍然连接
                if websocket not in self.active_connections:
                    logging.warning(f"[{client_id_info}] start_ping_monitoring: WebSocket no longer active, breaking ping loop for {target}.")
                    break
                    
                ping_data = {
                    "type": "ping_result",
                    "target": target,
                    "sequence": result.get("sequence", 0),
                    "success": result.get("success", False),
                    "status": self._get_ping_status(result),
                    "response_time": result.get("response_time"),
                    "ttl": result.get("ttl"),
                    "packet_size": result.get("packet_size", 32),
                    "timestamp": result.get("timestamp", time.time()),
                    "error": result.get("error_message"),
                    "error_message": result.get("error_message"),
                    "error_type": result.get("error_type")
                }
                
                try:
                    await websocket.send_text(json.dumps(ping_data))
                except WebSocketDisconnect:
                    # 连接已断开，停止发送
                    logging.info(f"[{client_id_info}] start_ping_monitoring: WebSocket disconnected while sending ping data to {target}.")
                    break
                except RuntimeError as e:
                    if "close message has been sent" in str(e):
                        # WebSocket已关闭，停止发送
                        logging.info(f"[{client_id_info}] start_ping_monitoring: WebSocket already closed while sending ping data to {target}.")
                        break
                    else:
                        logging.exception(f"[{client_id_info}] start_ping_monitoring: RuntimeError sending ping data to {target}: {e}")
                        raise
                    
                # 如果连接断开，停止监控
                if websocket not in self.active_connections:
                    logging.warning(f"[{client_id_info}] start_ping_monitoring: WebSocket no longer active after sending data, breaking ping loop for {target}.")
                    break
            logging.debug(f"[{client_id_info}] start_ping_monitoring: Ping loop finished for {target}.")
        except WebSocketDisconnect:
            # 连接已断开，正常退出
            logging.info(f"[{client_id_info}] start_ping_monitoring: WebSocket disconnected for {target}.")
            pass
        except Exception as e:
            logging.exception(f"[{client_id_info}] Unhandled exception in start_ping_monitoring for target {target}")
            # 只有在连接仍然活跃时才尝试发送错误信息
            if websocket in self.active_connections:
                try:
                    error_data = {
                        "type": "ping_error",
                        "target": target,
                        "error": str(e),
                        "timestamp": time.time()
                    }
                    await websocket.send_text(json.dumps(error_data))
                except (WebSocketDisconnect, RuntimeError):
                    # 忽略发送错误的尝试
                    pass

    async def start_scan_monitoring(self, websocket: WebSocket, targets: List[str], 
                                  ports: str = "1-1000", scan_type: str = "tcp", max_threads: int = 200):
        """启动扫描监控推送"""
        task_id = str(uuid.uuid4())
        client_id_info = "[unknown]"
        for cid, info in self.connection_info.items():
            if info["websocket"] == websocket:
                client_id_info = cid
                break
        logging.debug(f"[{client_id_info}] start_scan_monitoring: Called with task_id={task_id}, targets={targets}, ports={ports}, scan_type={scan_type}, max_threads={max_threads}")
        try:
            total_targets = len(targets)
            completed_targets = 0
            logging.debug(f"[{client_id_info}] start_scan_monitoring({task_id}): Starting scan for {total_targets} target(s).")

            for target_idx, target in enumerate(targets):
                logging.debug(f"[{client_id_info}] start_scan_monitoring({task_id}): Processing target {target_idx + 1}/{total_targets}: {target}")
                try:
                    # 检查WebSocket是否仍然连接
                    if websocket not in self.active_connections:
                        logging.warning(f"[{client_id_info}] start_scan_monitoring({task_id}): WebSocket no longer active, breaking scan for target {target}.")
                        break
                        
                    # 解析端口范围
                    logging.debug(f"[{client_id_info}] start_scan_monitoring({task_id}): Parsing ports '{ports}' for target {target}.")
                    port_list = self._parse_port_range(ports)
                    total_ports = len(port_list)
                    scanned_ports = 0
                    open_ports_found = 0
                    logging.debug(f"[{client_id_info}] start_scan_monitoring({task_id}): Parsed {total_ports} ports for target {target}.")

                    # 发送开始扫描通知
                    start_data = {
                        "type": "scan_started",
                        "task_id": task_id,
                        "target": target,
                        "total_ports": total_ports,
                        "scan_type": scan_type,
                        "timestamp": time.time()
                    }
                    
                    try:
                        await websocket.send_text(json.dumps(start_data))
                    except (WebSocketDisconnect, RuntimeError) as send_error:
                        logging.warning(f"[{client_id_info}] start_scan_monitoring({task_id}): Failed to send scan_started to {target}. Error: {send_error}")
                        break
                    
                    # 🚀 并发批量扫描端口（使用动态批量大小）
                    logging.debug(f"[{client_id_info}] start_scan_monitoring({task_id}): Starting concurrent port scan for {target} ({total_ports} ports) with max_threads={max_threads}.")
                    
                    # 设置批量大小，使用max_threads参数，确保不超过总端口数
                    batch_size = min(max_threads, total_ports)  # 使用max_threads作为批量大小
                    
                    for batch_start in range(0, total_ports, batch_size):
                        if websocket not in self.active_connections:
                            logging.warning(f"[{client_id_info}] start_scan_monitoring({task_id}): WebSocket no longer active, breaking batch scan for {target}.")
                            break
                        
                        batch_end = min(batch_start + batch_size, total_ports)
                        batch_ports = port_list[batch_start:batch_end]
                        
                        logging.debug(f"[{client_id_info}] start_scan_monitoring({task_id}): Scanning batch {batch_start+1}-{batch_end} of {total_ports} ports for {target} (batch_size={batch_size}).")
                        
                        # 创建并发扫描任务
                        scan_tasks = []
                        for port in batch_ports:
                            task = self.port_scanner.scan_port(
                                host=target,
                                port=port,
                                protocol=scan_type
                            )
                            scan_tasks.append(task)
                        
                        # 并发执行当前批次
                        try:
                            batch_results = await asyncio.gather(*scan_tasks, return_exceptions=True)
                        except Exception as e:
                            logging.error(f"[{client_id_info}] start_scan_monitoring({task_id}): Batch scan error for {target}: {e}")
                            continue
                        
                        # 处理批次结果
                        for i, result in enumerate(batch_results):
                            if isinstance(result, Exception):
                                logging.error(f"[{client_id_info}] start_scan_monitoring({task_id}): Port scan exception for {target}:{batch_ports[i]}: {result}")
                                continue
                            
                            if not isinstance(result, dict):
                                continue
                                
                            scanned_ports += 1
                            if result.get("status") == "open":
                                open_ports_found += 1
                                
                                # 发现开放端口时立即通知
                                open_port_data = {
                                    "type": "scan_port_found",
                                    "task_id": task_id,
                                    "target": target,
                                    "port": batch_ports[i],
                                    "result": result,
                                    "timestamp": time.time()
                                }
                                
                                try:
                                    await websocket.send_text(json.dumps(open_port_data))
                                except (WebSocketDisconnect, RuntimeError):
                                    logging.warning(f"[{client_id_info}] start_scan_monitoring({task_id}): Failed to send open port notification for {target}:{batch_ports[i]}.")
                                    break
                        
                        # 计算并发送进度更新
                        target_progress = (scanned_ports / total_ports) * 100
                        overall_progress = ((completed_targets + target_progress / 100) / total_targets) * 100
                        
                        progress_data = {
                            "type": "scan_progress",
                            "task_id": task_id,
                            "progress": round(overall_progress, 2),
                            "current_target": target,
                            "ports_scanned": scanned_ports,
                            "open_ports_found": open_ports_found,
                            "total_ports": total_ports,
                            "total_targets": total_targets,
                            "scan_type": scan_type,
                            "timestamp": time.time()
                        }
                        
                        try:
                            await websocket.send_text(json.dumps(progress_data))
                        except (WebSocketDisconnect, RuntimeError) as send_error:
                            logging.warning(f"[{client_id_info}] start_scan_monitoring({task_id}): Failed to send batch progress for {target}. Error: {send_error}")
                            break
                        
                        # 短暂延迟避免过于频繁的更新（减少延迟）
                        await asyncio.sleep(0.001)  # 1ms延迟，而不是10ms
                    
                    if websocket not in self.active_connections: # Check after batch loop
                        logging.warning(f"[{client_id_info}] start_scan_monitoring({task_id}): WebSocket disconnected after scanning ports for target {target}.")
                        break 
                    
                    completed_targets += 1
                    logging.debug(f"[{client_id_info}] start_scan_monitoring({task_id}): Finished scanning target {target}. Completed targets: {completed_targets}/{total_targets}")

                except Exception as target_error:
                    logging.exception(f"[{client_id_info}] start_scan_monitoring({task_id}): Error scanning target {target}: {target_error}")
                    # 单个目标扫描失败，继续下一个
                    if websocket in self.active_connections:
                        try:
                            error_data = {
                                "type": "scan_target_error",
                                "task_id": task_id,
                                "target": target,
                                "error": str(target_error),
                                "timestamp": time.time()
                            }
                            await websocket.send_text(json.dumps(error_data))
                        except (WebSocketDisconnect, RuntimeError):
                            break
                    completed_targets += 1
            
            logging.debug(f"[{client_id_info}] start_scan_monitoring({task_id}): Scan process finished for all targets.")
            # 扫描完成通知
            if websocket in self.active_connections:
                try:
                    completion_data = {
                        "type": "scan_completed",
                        "task_id": task_id,
                        "total_targets": total_targets,
                        "total_open_ports": sum([1 for target_data in [] for port_data in target_data if port_data.get("status") == "open"]),  # 这里需要实际统计
                        "scan_type": scan_type,
                        "timestamp": time.time()
                    }
                    await websocket.send_text(json.dumps(completion_data))
                except (WebSocketDisconnect, RuntimeError)  as send_error:
                    logging.warning(f"[{client_id_info}] start_scan_monitoring({task_id}): Failed to send scan_completed. Error: {send_error}")
                    pass
                    
        except WebSocketDisconnect:
            logging.info(f"[{client_id_info}] start_scan_monitoring({task_id}): WebSocket disconnected during scan task.")
            # 连接已断开，正常退出
            pass
        except Exception as e:
            logging.exception(f"[{client_id_info}] Unhandled exception in start_scan_monitoring for task_id {task_id}")
            # 只有在连接仍然活跃时才尝试发送错误信息
            if websocket in self.active_connections:
                try:
                    error_data = {
                        "type": "scan_error",
                        "task_id": task_id,
                        "error": str(e),
                        "timestamp": time.time()
                    }
                    await websocket.send_text(json.dumps(error_data))
                except (WebSocketDisconnect, RuntimeError):
                    pass

    def _parse_port_range(self, ports: str) -> List[int]:
        """解析端口范围字符串"""
        port_list = []
        
        for part in ports.split(","):
            part = part.strip()
            if "-" in part:
                # 端口范围
                start, end = map(int, part.split("-", 1))
                port_list.extend(range(start, end + 1))
            else:
                # 单个端口
                port_list.append(int(part))
        
        return sorted(list(set(port_list)))  # 去重并排序

    def _get_ping_status(self, result):
        """根据PING结果映射状态"""
        if result.get("success", False):
            return "success"
        
        error_type = result.get("error_type", "")
        if error_type in ["timeout", "unreachable"]:
            return "timeout"
        elif error_type in ["name_resolution", "permission_denied"]:
            return "error"
        else:
            return "timeout"  # 默认为超时


# 全局连接管理器
manager = ConnectionManager()


@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接端点
    
    Args:
        websocket: WebSocket连接
    """
    client_id = await manager.connect(websocket)
    
    try:
        # 发送连接成功消息
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "client_id": client_id,
            "message": "WebSocket连接已建立"
        }))
        
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type", "message")
                
                # 更新最后活动时间
                if client_id in manager.connection_info:
                    manager.connection_info[client_id]["last_activity"] = time.time()
                
                # 处理不同类型的消息
                if message_type == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": time.time()
                    }))
                elif message_type == "broadcast":
                    await manager.broadcast(json.dumps({
                        "type": "broadcast",
                        "from": client_id,
                        "message": message.get("content", ""),
                        "timestamp": time.time()
                    }))
                elif message_type == "private":
                    target_client = message.get("target")
                    if target_client:
                        success = await manager.send_message_to_client(
                            json.dumps({
                                "type": "private",
                                "from": client_id,
                                "message": message.get("content", ""),
                                "timestamp": time.time()
                            }),
                            target_client
                        )
                        if not success:
                            await websocket.send_text(json.dumps({
                                "type": "error",
                                "message": "目标客户端不存在或已断开连接"
                            }))
                else:
                    # 默认回显消息
                    await websocket.send_text(json.dumps({
                        "type": "echo",
                        "client_id": client_id,
                        "original_message": message,
                        "timestamp": time.time()
                    }))
                    
            except json.JSONDecodeError:
                # 处理非JSON消息
                await websocket.send_text(json.dumps({
                    "type": "echo",
                    "client_id": client_id,
                    "message": data,
                    "timestamp": time.time()
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/scan_monitor")
async def scan_monitor_websocket(websocket: WebSocket, 
                                targets: Optional[str] = "127.0.0.1",
                                ports: Optional[str] = "80,443,22,21,25,53,110,993,995",
                                scan_type: Optional[str] = "tcp"):
    """扫描监控WebSocket端点
    
    Args:
        websocket: WebSocket连接
        targets: 扫描目标，逗号分隔
        ports: 端口范围
        scan_type: 扫描类型
    """
    client_id = await manager.connect(websocket)
    
    try:
        await websocket.send_text(json.dumps({
            "type": "monitor_connected",
            "client_id": client_id,
            "message": "扫描监控连接已建立"
        }))
        
        # 解析目标列表
        target_list = [t.strip() for t in targets.split(",") if t.strip()]
        
        # 启动真实扫描监控
        await manager.start_scan_monitoring(
            websocket=websocket,
            targets=target_list,
            ports=ports,
            scan_type=scan_type
        )
        
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/ping_monitor")
async def ping_monitor_websocket(websocket: WebSocket,
                                target: Optional[str] = "8.8.8.8",
                                count: Optional[int] = -1,
                                interval: Optional[float] = 1.0):
    """PING监控WebSocket端点
    
    Args:
        websocket: WebSocket连接
        target: PING目标
        count: PING次数，-1为持续
        interval: PING间隔秒数
    """
    client_id = await manager.connect(websocket)
    
    try:
        await websocket.send_text(json.dumps({
            "type": "ping_monitor_connected",
            "client_id": client_id,
            "message": f"PING监控连接已建立，目标: {target}"
        }))
        logging.info(f"PING WebSocket ({client_id}) connected for target: {target}, count: {count}, interval: {interval}")

        # 启动真实PING监控
        await manager.start_ping_monitoring(
            websocket=websocket,
            target=target,
            count=count,
            interval=interval
        )
        logging.info(f"PING WebSocket ({client_id}) completed start_ping_monitoring call for target: {target}.")
        
    except WebSocketDisconnect:
        logging.info(f"PING WebSocket连接断开：client_id={client_id}, target={target}")
        manager.disconnect(websocket)
    except Exception as e:
        logging.exception(f"PING WebSocket ({client_id}) 异常 for target {target}: {e}")
        manager.disconnect(websocket)


@router.get("/connections", response_model=SuccessResponse)
async def get_websocket_connections():
    """获取WebSocket连接列表
    
    Returns:
        SuccessResponse: 连接列表
    """
    connections = manager.get_all_connections()
    
    return SuccessResponse(
        message="WebSocket连接列表获取成功",
        data={
            "total_connections": manager.get_connection_count(),
            "connections": connections
        }
    )


@router.post("/broadcast", response_model=SuccessResponse)
async def broadcast_message(message: Dict[str, Any]):
    """广播消息到所有WebSocket连接
    
    Args:
        message: 要广播的消息
        
    Returns:
        SuccessResponse: 广播结果
    """
    try:
        broadcast_data = {
            "type": "server_broadcast",
            "message": message.get("content", ""),
            "timestamp": time.time()
        }
        
        await manager.broadcast(json.dumps(broadcast_data))
        
        return SuccessResponse(
            message="消息广播成功",
            data={
                "recipients": manager.get_connection_count(),
                "message": message.get("content", "")
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"广播失败: {str(e)}"}
        )


@router.post("/send/{client_id}", response_model=SuccessResponse)
async def send_message_to_client(client_id: str, message: Dict[str, Any]):
    """发送消息到指定客户端
    
    Args:
        client_id: 目标客户端ID
        message: 要发送的消息
        
    Returns:
        SuccessResponse: 发送结果
    """
    try:
        message_data = {
            "type": "server_message",
            "message": message.get("content", ""),
            "timestamp": time.time()
        }
        
        success = await manager.send_message_to_client(
            json.dumps(message_data),
            client_id
        )
        
        if success:
            return SuccessResponse(
                message="消息发送成功",
                data={
                    "client_id": client_id,
                    "message": message.get("content", "")
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": "客户端不存在或已断开连接"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"消息发送失败: {str(e)}"}
        )


@router.get("/statistics", response_model=SuccessResponse)
async def get_websocket_statistics():
    """获取WebSocket统计信息
    
    Returns:
        SuccessResponse: 统计信息
    """
    stats = {
        "total_connections": manager.get_connection_count(),
        "active_connections": len(manager.active_connections),
        "uptime": time.time() - (min([info["connected_at"] for info in manager.connection_info.values()]) if manager.connection_info else time.time())
    }
    
    return SuccessResponse(
        message="WebSocket统计信息获取成功",
        data=stats
    )


@router.websocket("/ping")
async def ping_websocket(websocket: WebSocket,
                          target: Optional[str] = "8.8.8.8",
                          count: Optional[int] = -1,
                          interval: Optional[float] = 1.0):
    """PING WebSocket端点（与前端路径匹配）
    
    Args:
        websocket: WebSocket连接
        target: PING目标
        count: PING次数，-1为持续
        interval: PING间隔秒数
    """
    # 记录接收到的参数
    logging.info(f"PING WebSocket连接参数：target={target}, count={count}, interval={interval}")
    
    client_id = await manager.connect(websocket)
    
    try:
        await websocket.send_text(json.dumps({
            "type": "ping_monitor_connected",
            "client_id": client_id,
            "message": f"PING监控连接已建立，目标: {target}"
        }))
        
        # 创建PING监控任务
        ping_task = asyncio.create_task(manager.start_ping_monitoring(
            websocket=websocket,
            target=target,
            count=count,
            interval=interval
        ))
        
        # 创建消息监听任务
        async def message_listener():
            try:
                logging.info(f"[{client_id}] 开始消息监听任务")
                while True:
                    logging.debug(f"[{client_id}] 等待接收WebSocket消息...")
                    data = await websocket.receive_text()
                    logging.info(f"[{client_id}] 🔍 收到WebSocket消息: {data}")
                    
                    try:
                        message = json.loads(data)
                        logging.info(f"[{client_id}] 📋 解析后的消息: {message}")
                        
                        if message.get("type") == "stop_ping":
                            logging.info(f"[{client_id}] 🛑 收到停止PING信号！！！：client_id={client_id}")
                            # 发送停止信号
                            manager.stop_ping_for_client(client_id)
                            # 取消PING任务
                            ping_task.cancel()
                            logging.info(f"[{client_id}] ✅ 已取消PING任务并设置停止信号")
                            break
                        elif message.get("type") == "ping":
                            # 心跳响应
                            logging.debug(f"[{client_id}] 💓 处理心跳消息")
                            await websocket.send_text(json.dumps({"type": "pong", "timestamp": time.time()}))
                        else:
                            logging.info(f"[{client_id}] ❓ 未知消息类型: {message.get('type')}")
                            
                    except json.JSONDecodeError as e:
                        logging.warning(f"[{client_id}] ❌ JSON解析失败: {data}, 错误: {e}")
                    
            except WebSocketDisconnect:
                logging.info(f"[{client_id}] 🔌 PING WebSocket连接断开")
                ping_task.cancel()
            except Exception as e:
                logging.error(f"[{client_id}] ❌ 消息监听异常: {e}")
                ping_task.cancel()
        
        # 创建消息监听任务
        message_task = asyncio.create_task(message_listener())
        
        # 等待任一任务完成
        done, pending = await asyncio.wait(
            [ping_task, message_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # 取消所有未完成的任务
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        logging.info(f"PING WebSocket会话结束：client_id={client_id}")
        
    except WebSocketDisconnect:
        logging.info(f"PING WebSocket连接断开：client_id={client_id}")
        manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"PING WebSocket异常：{str(e)}")
        manager.disconnect(websocket)


@router.websocket("/scan")
async def scan_websocket(websocket: WebSocket, 
                        targets: Optional[str] = "127.0.0.1",
                        ports: Optional[str] = "80,443,22,21,25,53,110,993,995",
                        scan_type: Optional[str] = "tcp",
                        max_threads: Optional[int] = 200):
    """扫描WebSocket端点（与前端路径匹配）
    
    Args:
        websocket: WebSocket连接
        targets: 扫描目标，逗号分隔
        ports: 端口范围
        scan_type: 扫描类型
        max_threads: 最大并发线程数
    """
    # 记录接收到的参数
    logging.info(f"扫描WebSocket连接参数：targets={targets}, ports={ports}, scan_type={scan_type}, max_threads={max_threads}")
    
    client_id = await manager.connect(websocket)
    
    try:
        await websocket.send_text(json.dumps({
            "type": "monitor_connected",
            "client_id": client_id,
            "message": "扫描监控连接已建立"
        }))
        logging.info(f"扫描WebSocket ({client_id}) connected for targets: {targets}, ports: {ports}, scan_type: {scan_type}, max_threads: {max_threads}")
        
        # 解析目标列表
        target_list = [t.strip() for t in targets.split(",") if t.strip()]
        logging.info(f"扫描WebSocket ({client_id})目标列表：{target_list}")
        
        # 启动真实扫描监控，传递max_threads参数
        await manager.start_scan_monitoring(
            websocket=websocket,
            targets=target_list,
            ports=ports,
            scan_type=scan_type,
            max_threads=max_threads
        )
        logging.info(f"扫描WebSocket ({client_id}) completed start_scan_monitoring call for targets: {targets}.")

    except WebSocketDisconnect:
        logging.info(f"扫描WebSocket连接断开：client_id={client_id}, targets={targets}")
        manager.disconnect(websocket)
    except Exception as e:
        logging.exception(f"扫描WebSocket ({client_id}) 异常 for targets {targets}: {e}")
        manager.disconnect(websocket) 