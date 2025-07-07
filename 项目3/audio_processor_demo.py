#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频处理器命令行演示版本
展示主要功能和数据模拟
"""

import time
import random
import threading
from datetime import datetime

class AudioProcessorDemo:
    def __init__(self):
        self.is_recording = False
        self.current_bpm = 0
        self.current_db = 0
        self.current_hz = 0
        self.split_time = 2.0
        self.frequency_unit = "Hz"
        self.frequency_range = {"min": 1000, "max": 20000}
        self.debug_mode = False
        
        # 数据历史
        self.bpm_history = []
        self.db_history = []
        self.hz_history = []
        self.log_data = []
        
        # 初始化日志
        self.add_log("info", "音频检测系统已启动")
        self.add_log("info", "BPM检测正常运行")
        self.add_log("debug", "频谱分析完成")
        
    def add_log(self, log_type, message):
        """添加日志条目"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_data.append({
            'time': timestamp,
            'type': log_type,
            'message': message
        })
        
    def toggle_recording(self):
        """切换录音状态"""
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.add_log("info", "开始音频录制")
            print("🎵 开始录制...")
        else:
            self.add_log("info", "停止音频录制")
            print("⏹️  停止录制...")
            
    def simulate_data(self):
        """模拟数据更新"""
        while True:
            if self.is_recording:
                # 模拟BPM变化
                self.current_bpm = max(120, min(200, 
                    self.current_bpm + random.randint(-5, 5)))
                
                # 模拟dB变化
                self.current_db = max(10, min(50, 
                    self.current_db + random.randint(-3, 3)))
                
                # 模拟Hz变化
                self.current_hz = max(1000, min(5000, 
                    self.current_hz + random.randint(-200, 200)))
                
                # 添加到历史数据
                self.bpm_history.append(self.current_bpm)
                self.db_history.append(self.current_db)
                self.hz_history.append(self.current_hz)
                
                # 限制历史数据长度
                if len(self.bpm_history) > 20:
                    self.bpm_history = self.bpm_history[-20:]
                    self.db_history = self.db_history[-20:]
                    self.hz_history = self.hz_history[-20:]
                
                # 显示当前数据
                self.display_current_data()
                
            time.sleep(self.split_time)
            
    def display_current_data(self):
        """显示当前数据"""
        print(f"\r📊 BPM: {self.current_bpm:3d} | dB: {self.current_db:2d} | Hz: {self.current_hz:4d} | 历史数据点: {len(self.bpm_history)}", end="", flush=True)
        
    def show_stats(self):
        """显示统计信息"""
        if not self.bpm_history:
            print("📈 暂无统计数据")
            return
            
        print("\n" + "="*60)
        print("📈 统计信息")
        print("="*60)
        print(f"BPM - 平均: {sum(self.bpm_history)/len(self.bpm_history):.1f}, 最小: {min(self.bpm_history)}, 最大: {max(self.bpm_history)}")
        print(f"dB  - 平均: {sum(self.db_history)/len(self.db_history):.1f}, 最小: {min(self.db_history)}, 最大: {max(self.db_history)}")
        print(f"Hz  - 平均: {sum(self.hz_history)/len(self.hz_history):.1f}, 最小: {min(self.hz_history)}, 最大: {max(self.hz_history)}")
        print(f"数据点数量: {len(self.bpm_history)}")
        print(f"分段时间: {self.split_time}秒")
        print("="*60)
        
    def show_config(self):
        """显示配置信息"""
        print("\n" + "="*60)
        print("⚙️  配置信息")
        print("="*60)
        print(f"分段时间: {self.split_time}秒")
        print(f"频率单位: {self.frequency_unit}")
        print(f"频率范围: {self.frequency_range['min']} - {self.frequency_range['max']} Hz")
        print(f"调试模式: {'开启' if self.debug_mode else '关闭'}")
        print("="*60)
        
    def show_logs(self):
        """显示日志"""
        print("\n" + "="*60)
        print("📜 系统日志")
        print("="*60)
        for log_entry in self.log_data[-10:]:  # 显示最近10条日志
            if not self.debug_mode and log_entry['type'] == 'debug':
                continue
            color = {
                'info': '🟢',
                'error': '🔴',
                'debug': '🟡'
            }.get(log_entry['type'], '⚪')
            print(f"{color} {log_entry['time']} [{log_entry['type'].upper()}] {log_entry['message']}")
        print("="*60)
        
    def run_demo(self):
        """运行演示"""
        print("🎵 音频处理器桌面界面演示")
        print("="*60)
        print("这是一个模拟音频处理器的演示程序")
        print("实际的GUI界面包含以下功能页面：")
        print("1. 测量页面 - 实时显示BPM、dB、Hz和波形图")
        print("2. 统计页面 - 历史数据图表和趋势分析")
        print("3. 配置页面 - 参数设置和偏好配置")
        print("4. 日志页面 - 系统运行日志和调试信息")
        print("="*60)
        
        # 启动数据模拟线程
        data_thread = threading.Thread(target=self.simulate_data, daemon=True)
        data_thread.start()
        
        while True:
            print("\n📋 可用命令:")
            print("1. start/stop - 开始/停止录制")
            print("2. stats - 显示统计信息")
            print("3. config - 显示配置信息")
            print("4. logs - 显示系统日志")
            print("5. debug - 切换调试模式")
            print("6. quit - 退出程序")
            
            try:
                command = input("\n请输入命令: ").strip().lower()
                
                if command in ['start', 'stop']:
                    self.toggle_recording()
                elif command == 'stats':
                    self.show_stats()
                elif command == 'config':
                    self.show_config()
                elif command == 'logs':
                    self.show_logs()
                elif command == 'debug':
                    self.debug_mode = not self.debug_mode
                    print(f"🔧 调试模式已{'开启' if self.debug_mode else '关闭'}")
                elif command == 'quit':
                    print("👋 程序退出")
                    break
                else:
                    print("❌ 无效命令，请重新输入")
                    
            except KeyboardInterrupt:
                print("\n👋 程序退出")
                break

if __name__ == "__main__":
    demo = AudioProcessorDemo()
    demo.run_demo()

