#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频处理器桌面界面
基于用户提供的UI设计要素创建的小窗口桌面应用
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import pyaudio
import librosa
import csv
from tkinter import filedialog

class AudioProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("音频处理器 - Audio Processor")
        self.root.geometry("900x600")
        self.root.configure(bg='#000000')
        self.root.resizable(True, True)
        
        # 应用状态变量
        self.is_recording = False
        self.current_bpm = 170
        self.current_db = 25
        self.current_hz = 2500
        self.split_time = 2.0
        self.frequency_unit = "Hz"
        self.frequency_range = {"min": 1000, "max": 16000}
        self.debug_mode = False
        self.selected_mic_index = None  # 新增：当前选择的麦克风索引
        self.audio_data = None  # 存储音频数据
        self.sample_rate = 16000  # 采样率
        
        # 数据存储
        self.bpm_history = []
        self.db_history = []
        self.hz_history = []
        self.time_history = []  # 新增：采集时间戳
        self.waveform_data = []
        self.log_data = []
        self.noise_templates = []  # 支持多个噪声模板
        
        # 初始化日志
        self.add_log("info", "音频检测系统已启动")
        self.add_log("info", "BPM检测正常运行")
        self.add_log("debug", "频谱分析完成")
        
        self.mic_list = self.get_microphone_list()  # 获取麦克风列表
        self.setup_ui()
        self.start_data_simulation()
        
    def get_microphone_list(self):
        """获取可用麦克风设备列表"""
        p = pyaudio.PyAudio()
        mic_list = []
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info.get('maxInputChannels', 0) > 0:
                mic_list.append({'index': i, 'name': info['name']})
        p.terminate()
        return mic_list

    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = tk.Frame(self.root, bg='#000000')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建顶部导航栏
        self.create_navigation(main_frame)
        
        # 创建内容区域
        self.content_frame = tk.Frame(main_frame, bg='#000000')
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 麦克风设备初始化
        self.selected_mic_index = 0
        self.mic_devices = self.list_microphone_devices()
        
        # 默认显示测量页面
        self.show_measure_page()
        
    def list_microphone_devices(self):
        """枚举所有可用麦克风设备，返回[(index, name), ...]"""
        p = pyaudio.PyAudio()
        devices = []
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info.get('maxInputChannels', 0) > 0:
                devices.append((i, info.get('name', f"设备{i}")))
        p.terminate()
        if not devices:
            devices = [(0, '默认麦克风')]
        return devices

    def create_navigation(self, parent):
        """创建顶部导航栏"""
        nav_frame = tk.Frame(parent, bg='#1a1a1a', height=50)
        nav_frame.pack(fill=tk.X)
        nav_frame.pack_propagate(False)
        
        # 导航按钮样式
        button_style = {
            'bg': '#1a1a1a',
            'fg': '#87ceeb',
            'font': ('Arial', 10),
            'relief': 'flat',
            'borderwidth': 0,
            'padx': 20,
            'pady': 10
        }
        
        active_style = button_style.copy()
        active_style.update({'fg': '#ffffff', 'font': ('Arial', 10, 'bold')})
        
        # 创建导航按钮
        self.nav_buttons = {}
        buttons = [
            ("测量", self.show_measure_page),
            ("配置", self.show_config_page),
            ("高级校准", self.show_advanced_calib_page),
            ("日志", self.show_log_page)
        ]
        
        for text, command in buttons:
            btn = tk.Button(nav_frame, text=text, command=command, **button_style)
            btn.pack(side=tk.LEFT)
            self.nav_buttons[text] = btn
            
        # 设置默认激活按钮
        self.set_active_nav("测量")
        
    def set_active_nav(self, active_text):
        """设置激活的导航按钮"""
        for text, btn in self.nav_buttons.items():
            if text == active_text:
                btn.configure(fg='#ffffff', font=('Arial', 10, 'bold'))
            else:
                btn.configure(fg='#87ceeb', font=('Arial', 10))
                
    def clear_content(self):
        """清空内容区域"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_measure_page(self):
        """显示测量页面"""
        self.set_active_nav("测量")
        self.clear_content()
        
        # 创建三列布局
        left_frame = tk.Frame(self.content_frame, bg='#000000', width=200)
        center_frame = tk.Frame(self.content_frame, bg='#000000', width=400)
        right_frame = tk.Frame(self.content_frame, bg='#000000', width=300)
        
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        left_frame.pack_propagate(False)
        right_frame.pack_propagate(False)
        
        # 麦克风选择收纳窗
        self.create_mic_selector(left_frame)
        
        # 左侧：数字显示区
        self.create_digital_display(left_frame)
        
        # 中部：图形波形区
        self.create_waveform_area(center_frame)
        
        # 右侧：频率图 + 操作区
        self.create_frequency_area(right_frame)
        # 右侧操作按钮区（始终显示）
        btn_frame = tk.Frame(right_frame, bg='#000000')
        btn_frame.pack(fill=tk.X, pady=(0, 5), anchor='ne')
        export_btn = tk.Button(
            btn_frame,
            text="导出CSV",
            font=('Arial', 9, 'bold'),
            bg='#22c55e',  # 绿色
            fg='#fff',
            activebackground='#16a34a',
            activeforeground='#fff',
            relief='flat',
            padx=8,
            pady=3,
            height=1,
            bd=0,
            command=self.export_csv
        )
        export_btn.pack(side=tk.RIGHT, padx=2)
        reset_btn = tk.Button(
            btn_frame,
            text="重置测量数据",
            font=('Arial', 9, 'bold'),
            bg='#ef4444',  # 红色
            fg='#fff',
            activebackground='#b91c1c',
            activeforeground='#fff',
            relief='flat',
            padx=8,
            pady=3,
            height=1,
            bd=0,
            command=self.reset_measure_data
        )
        reset_btn.pack(side=tk.RIGHT, padx=2)

    def create_mic_selector(self, parent):
        """创建麦克风选择收纳窗"""
        frame = tk.LabelFrame(parent, text="麦克风选择", font=('Arial', 10, 'bold'), fg='#87ceeb', bg='#1a1a1a', bd=1, relief='solid')
        frame.pack(fill=tk.X, pady=(10, 5))
        self.mic_var = tk.StringVar()
        mic_names = [name for idx, name in self.mic_devices]
        if self.selected_mic_index >= len(mic_names):
            self.selected_mic_index = 0
        self.mic_var.set(mic_names[self.selected_mic_index])
        mic_menu = ttk.Combobox(frame, textvariable=self.mic_var, values=mic_names, state='readonly', font=('Arial', 10))
        mic_menu.pack(fill=tk.X, padx=5, pady=5)
        mic_menu.bind('<<ComboboxSelected>>', self.on_mic_selected)
        # 刷新按钮
        btn = tk.Button(frame, text="刷新设备", font=('Arial', 9), bg='#404040', fg='#fff', relief='flat', command=self.refresh_mic_devices)
        btn.pack(side=tk.RIGHT, padx=5, pady=2)

    def on_mic_selected(self, event=None):
        """切换麦克风设备"""
        name = self.mic_var.get()
        for idx, n in self.mic_devices:
            if n == name:
                self.selected_mic_index = idx
                self.add_log("info", f"切换麦克风: {n}")
                break

    def refresh_mic_devices(self):
        """刷新麦克风设备列表"""
        self.mic_devices = self.list_microphone_devices()
        mic_names = [name for idx, name in self.mic_devices]
        self.mic_var.set(mic_names[0] if mic_names else '默认麦克风')
        self.selected_mic_index = self.mic_devices[0][0] if self.mic_devices else 0
        self.show_measure_page()

    def create_digital_display(self, parent):
        """创建数字显示区域"""
        # BPM显示
        bpm_frame = tk.Frame(parent, bg='#000000')
        bpm_frame.pack(pady=(50, 30))
        
        self.bpm_label = tk.Label(
            bpm_frame, 
            text=f"{self.current_bpm}",
            font=('Courier New', 48, 'bold'),
            fg='#ffffff',
            bg='#000000'
        )
        self.bpm_label.pack()
        
        bpm_unit_label = tk.Label(
            bpm_frame,
            text="BPM",
            font=('Arial', 14),
            fg='#87ceeb',
            bg='#000000'
        )
        bpm_unit_label.pack()
        
        # dB和Hz显示
        db_hz_frame = tk.Frame(parent, bg='#000000')
        db_hz_frame.pack(pady=20)
        
        self.db_label = tk.Label(
            db_hz_frame,
            text=f"{self.current_db} dB",
            font=('Courier New', 16, 'bold'),
            fg='#ffffff',
            bg='#000000'
        )
        self.db_label.pack(pady=5)
        
        self.hz_label = tk.Label(
            db_hz_frame,
            text=f"{self.current_hz/1000:.1f} kHz",
            font=('Courier New', 16, 'bold'),
            fg='#ffffff',
            bg='#000000'
        )
        self.hz_label.pack(pady=5)
        
    def create_waveform_area(self, parent):
        """创建波形显示区域"""
        # 播放/暂停按钮
        control_frame = tk.Frame(parent, bg='#000000')
        control_frame.pack(pady=10)
        
        self.play_button = tk.Button(
            control_frame,
            text="▶" if not self.is_recording else "⏸",
            font=('Arial', 20),
            bg='#404040',
            fg='#ffffff',
            width=4,
            height=2,
            command=self.toggle_recording,
            relief='flat'
        )
        self.play_button.pack()
        
        # 波形图
        self.create_waveform_plot(parent)
        
        # Split Time控制
        split_frame = tk.Frame(parent, bg='#000000')
        split_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            split_frame,
            text="Split Time",
            font=('Arial', 10),
            fg='#888888',
            bg='#000000'
        ).pack(side=tk.LEFT)
        
        self.split_scale = tk.Scale(
            split_frame,
            from_=0.5,
            to=10.0,
            resolution=0.5,
            orient=tk.HORIZONTAL,
            bg='#000000',
            fg='#ffffff',
            highlightthickness=0,
            command=self.update_split_time
        )
        self.split_scale.set(self.split_time)
        self.split_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        tk.Label(
            split_frame,
            text=f"{self.split_time}s",
            font=('Arial', 10),
            fg='#888888',
            bg='#000000'
        ).pack(side=tk.RIGHT)
        
    def create_waveform_plot(self, parent):
        """创建傅里叶频谱图"""
        plot_frame = tk.Frame(parent, bg='#1a1a1a', relief='solid', bd=1)
        plot_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.fig = Figure(figsize=(6, 3), facecolor='#1a1a1a')
        self.ax = self.fig.add_subplot(111, facecolor='#1a1a1a')
        
        # 初始化空频谱图
        self.spectrum_line, = self.ax.plot([], [], color='#3b82f6', linewidth=2)
        
        self.ax.set_xlabel('频率 (Hz)', color='#888888')
        self.ax.set_ylabel('幅度', color='#888888')
        self.ax.set_title('傅里叶频谱', color='#ffffff', fontsize=12)
        self.ax.set_facecolor('#1a1a1a')
        self.ax.tick_params(colors='#888888')
        self.ax.grid(True, alpha=0.3, color='#404040')
        
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 添加点击事件处理
        self.canvas.mpl_connect('button_press_event', self.on_spectrum_click)
        
    def create_frequency_area(self, parent):
        """创建频率显示和控制区域"""
        # 单位切换按钮
        unit_frame = tk.Frame(parent, bg='#000000')
        unit_frame.pack(fill=tk.X, pady=5)
        hz_btn = tk.Button(
            unit_frame,
            text="Hz",
            font=('Arial', 9),
            bg='#404040' if self.frequency_unit == 'Hz' else '#1a1a1a',
            fg='#ffffff',
            command=lambda: self.set_frequency_unit('Hz'),
            relief='flat',
            padx=15
        )
        hz_btn.pack(side=tk.LEFT, padx=2)
        khz_btn = tk.Button(
            unit_frame,
            text="kHz",
            font=('Arial', 9),
            bg='#404040' if self.frequency_unit == 'kHz' else '#1a1a1a',
            fg='#ffffff',
            command=lambda: self.set_frequency_unit('kHz'),
            relief='flat',
            padx=15
        )
        khz_btn.pack(side=tk.LEFT, padx=2)
        # 频率范围显示
        range_label = tk.Label(
            parent,
            text=f"f = {self.frequency_range['min']} Hz ~ {self.frequency_range['max']} Hz",
            font=('Arial', 9),
            fg='#888888',
            bg='#000000'
        )
        range_label.pack(pady=5)
        # 频率图
        self.create_frequency_plot(parent)

    def create_frequency_plot(self, parent):
        """创建频率图：左bpm右hz"""
        freq_frame = tk.Frame(parent, bg='#1a1a1a', relief='solid', bd=1)
        freq_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.freq_fig = Figure(figsize=(3, 4), facecolor='#1a1a1a')
        self.freq_ax = self.freq_fig.add_subplot(111, facecolor='#1a1a1a')
        # 绘制bpm和hz
        t_points = np.arange(len(self.bpm_history)) * self.split_time if self.bpm_history else []
        hz_points = self.hz_history if self.hz_history else []
        bpm_points = self.bpm_history if self.bpm_history else []
        if len(t_points) and len(hz_points):
            self.freq_ax.plot(t_points, hz_points, color='#3b82f6', linewidth=2, label='Hz')
        if len(t_points) and len(bpm_points):
            self.freq_ax.plot(t_points, bpm_points, color='#ef4444', linewidth=2, label='BPM')
        self.freq_ax.set_xlabel('t (s)', color='#888888', fontsize=8)
        self.freq_ax.set_ylabel('Hz / BPM', color='#888888', fontsize=8)
        self.freq_ax.tick_params(colors='#888888', labelsize=7)
        self.freq_ax.grid(True, alpha=0.3, color='#404040')
        self.freq_ax.legend(facecolor='#1a1a1a', edgecolor='#404040', labelcolor='#ffffff')
        self.freq_canvas = FigureCanvasTkAgg(self.freq_fig, freq_frame)
        self.freq_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_stats_page(self):
        """显示统计页面"""
        self.set_active_nav("统计")
        self.clear_content()
        
        # 控制开关
        control_frame = tk.Frame(self.content_frame, bg='#000000')
        control_frame.pack(fill=tk.X, pady=10)
        
        self.show_bpm = tk.BooleanVar(value=True)
        self.show_db = tk.BooleanVar(value=True)
        self.show_hz = tk.BooleanVar(value=False)
        
        tk.Checkbutton(
            control_frame,
            text="BPM",
            variable=self.show_bpm,
            font=('Arial', 10),
            fg='#ffffff',
            bg='#000000',
            selectcolor='#404040',
            command=self.update_stats_plot
        ).pack(side=tk.LEFT, padx=20)
        
        tk.Checkbutton(
            control_frame,
            text="dB",
            variable=self.show_db,
            font=('Arial', 10),
            fg='#ffffff',
            bg='#000000',
            selectcolor='#404040',
            command=self.update_stats_plot
        ).pack(side=tk.LEFT, padx=20)
        
        tk.Checkbutton(
            control_frame,
            text="Hz",
            variable=self.show_hz,
            font=('Arial', 10),
            fg='#ffffff',
            bg='#000000',
            selectcolor='#404040',
            command=self.update_stats_plot
        ).pack(side=tk.LEFT, padx=20)
        
        # 统计图表
        self.create_stats_plot()
        
        # 新增导出和重置按钮
        btn_frame = tk.Frame(self.content_frame, bg='#000000')
        btn_frame.pack(fill=tk.X, pady=5)
        export_btn = tk.Button(btn_frame, text="导出CSV", font=('Arial', 9, 'bold'), bg='#3b82f6', fg='#fff', command=self.export_csv, relief='flat', padx=10, pady=6, height=1)
        export_btn.pack(side=tk.RIGHT, padx=2)
        reset_btn = tk.Button(btn_frame, text="重置测量数据", font=('Arial', 9, 'bold'), bg='#ef4444', fg='#fff', command=self.reset_measure_data, relief='flat', padx=10, pady=6, height=1)
        reset_btn.pack(side=tk.RIGHT, padx=2)

    def create_stats_plot(self):
        """创建统计图表"""
        plot_frame = tk.Frame(self.content_frame, bg='#1a1a1a', relief='solid', bd=1)
        plot_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.stats_fig = Figure(figsize=(8, 5), facecolor='#1a1a1a')
        self.stats_ax = self.stats_fig.add_subplot(111, facecolor='#1a1a1a')
        self.stats_ax2 = self.stats_fig.add_subplot(112, facecolor='#1a1a1a')  # 新增db条形图
        self.update_stats_plot()
        self.stats_canvas = FigureCanvasTkAgg(self.stats_fig, plot_frame)
        self.stats_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_stats_plot(self):
        """更新统计图表"""
        if hasattr(self, 'stats_ax'):
            self.stats_ax.clear()
            if self.bpm_history:
                time_points = self.time_history if self.time_history else np.arange(len(self.bpm_history)) * self.split_time
                if self.show_bpm.get():
                    self.stats_ax.plot(time_points, self.bpm_history, color='#ef4444', linewidth=2, label='BPM')
                if self.show_hz.get():
                    self.stats_ax.plot(time_points, self.hz_history, color='#3b82f6', linewidth=2, label='Hz')
                self.stats_ax.set_xlabel('时间 (s)', color='#888888')
                self.stats_ax.set_ylabel('BPM/Hz', color='#888888')
                self.stats_ax.legend(facecolor='#1a1a1a', edgecolor='#404040', labelcolor='#ffffff')
            self.stats_ax.tick_params(colors='#888888')
            self.stats_ax.grid(True, alpha=0.3, color='#404040')
            # db用条形图
            if hasattr(self, 'stats_ax2'):
                self.stats_ax2.clear()
                if self.show_db.get() and self.db_history:
                    time_points = self.time_history if self.time_history else np.arange(len(self.db_history)) * self.split_time
                    self.stats_ax2.bar(time_points, self.db_history, color='#22c55e', label='dB', alpha=0.7)
                    self.stats_ax2.set_ylabel('dB', color='#22c55e')
                    self.stats_ax2.legend(facecolor='#1a1a1a', edgecolor='#404040', labelcolor='#22c55e')
                self.stats_ax2.tick_params(colors='#888888')
                self.stats_ax2.grid(True, alpha=0.3, color='#404040')
            if hasattr(self, 'stats_canvas'):
                self.stats_canvas.draw()

    def show_config_page(self):
        """显示配置页面"""
        self.set_active_nav("配置")
        self.clear_content()
        
        config_frame = tk.Frame(self.content_frame, bg='#000000')
        config_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # 分段时间设置
        split_section = tk.LabelFrame(
            config_frame,
            text="分段时间设置",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#1a1a1a',
            bd=1,
            relief='solid'
        )
        split_section.pack(fill=tk.X, pady=10)
        
        split_inner = tk.Frame(split_section, bg='#1a1a1a')
        split_inner.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(
            split_inner,
            text="Split Time:",
            font=('Arial', 10),
            fg='#ffffff',
            bg='#1a1a1a'
        ).pack(side=tk.LEFT)
        
        self.config_split_scale = tk.Scale(
            split_inner,
            from_=0.5,
            to=10.0,
            resolution=0.5,
            orient=tk.HORIZONTAL,
            bg='#1a1a1a',
            fg='#ffffff',
            highlightthickness=0
        )
        self.config_split_scale.set(self.split_time)
        self.config_split_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        tk.Label(
            split_inner,
            text="秒",
            font=('Arial', 10),
            fg='#ffffff',
            bg='#1a1a1a'
        ).pack(side=tk.RIGHT)
        
        # 单位偏好设置
        unit_section = tk.LabelFrame(
            config_frame,
            text="单位偏好",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#1a1a1a',
            bd=1,
            relief='solid'
        )
        unit_section.pack(fill=tk.X, pady=10)
        
        unit_inner = tk.Frame(unit_section, bg='#1a1a1a')
        unit_inner.pack(fill=tk.X, padx=20, pady=15)
        
        self.unit_var = tk.StringVar(value=self.frequency_unit)
        
        tk.Radiobutton(
            unit_inner,
            text="Hz",
            variable=self.unit_var,
            value="Hz",
            font=('Arial', 10),
            fg='#ffffff',
            bg='#1a1a1a',
            selectcolor='#404040'
        ).pack(side=tk.LEFT, padx=20)
        
        tk.Radiobutton(
            unit_inner,
            text="kHz",
            variable=self.unit_var,
            value="kHz",
            font=('Arial', 10),
            fg='#ffffff',
            bg='#1a1a1a',
            selectcolor='#404040'
        ).pack(side=tk.LEFT, padx=20)
        
        # 频谱范围设置
        freq_section = tk.LabelFrame(
            config_frame,
            text="频谱范围设置",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#1a1a1a',
            bd=1,
            relief='solid'
        )
        freq_section.pack(fill=tk.X, pady=10)
        
        freq_inner = tk.Frame(freq_section, bg='#1a1a1a')
        freq_inner.pack(fill=tk.X, padx=20, pady=15)
        
        # 起始频率
        start_frame = tk.Frame(freq_inner, bg='#1a1a1a')
        start_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            start_frame,
            text="起始频率 (Hz):",
            font=('Arial', 10),
            fg='#ffffff',
            bg='#1a1a1a'
        ).pack(side=tk.LEFT)
        
        self.start_freq_entry = tk.Entry(
            start_frame,
            font=('Arial', 10),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat'
        )
        self.start_freq_entry.insert(0, str(self.frequency_range['min']))
        self.start_freq_entry.pack(side=tk.RIGHT, padx=10)
        
        # 结束频率
        end_frame = tk.Frame(freq_inner, bg='#1a1a1a')
        end_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            end_frame,
            text="结束频率 (Hz):",
            font=('Arial', 10),
            fg='#ffffff',
            bg='#1a1a1a'
        ).pack(side=tk.LEFT)
        
        self.end_freq_entry = tk.Entry(
            end_frame,
            font=('Arial', 10),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat'
        )
        self.end_freq_entry.insert(0, str(self.frequency_range['max']))
        self.end_freq_entry.pack(side=tk.RIGHT, padx=10)
        
        # 应用按钮
        apply_btn = tk.Button(
            config_frame,
            text="应用设置",
            font=('Arial', 12, 'bold'),
            bg='#3b82f6',
            fg='#ffffff',
            command=self.apply_config,
            relief='flat',
            padx=30,
            pady=10
        )
        apply_btn.pack(pady=20)
        
        # 移除dB校准按钮，新增噪声采集/刷新按钮
        self.noise_btn = tk.Button(
            config_frame,
            text="采集噪声模板",
            font=('Arial', 12, 'bold'),
            bg='#fbbf24',
            fg='#fff',
            command=self.collect_noise_template
        )
        self.noise_btn.pack(pady=10)
        # 展示噪声模板列表
        self.noise_list_frame = tk.Frame(config_frame, bg='#1a1a1a')
        self.noise_list_frame.pack(fill=tk.X, pady=5)
        self.refresh_noise_list()
        
    def show_log_page(self):
        """显示日志页面"""
        self.set_active_nav("日志")
        self.clear_content()
        
        # Debug开关
        debug_frame = tk.Frame(self.content_frame, bg='#000000')
        debug_frame.pack(fill=tk.X, pady=10)
        
        self.debug_var = tk.BooleanVar(value=self.debug_mode)
        
        tk.Checkbutton(
            debug_frame,
            text="显示调试日志",
            variable=self.debug_var,
            font=('Arial', 10),
            fg='#ffffff',
            bg='#000000',
            selectcolor='#404040',
            command=self.toggle_debug_mode
        ).pack(side=tk.LEFT)
        
        # 日志显示区域
        log_frame = tk.Frame(self.content_frame, bg='#1a1a1a', relief='solid', bd=1)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建滚动文本框
        self.log_text = tk.Text(
            log_frame,
            font=('Courier New', 9),
            bg='#1a1a1a',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            wrap=tk.WORD
        )
        
        scrollbar = tk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置日志颜色标签
        self.log_text.tag_configure("info", foreground="#22c55e")
        self.log_text.tag_configure("error", foreground="#ef4444")
        self.log_text.tag_configure("debug", foreground="#fbbf24")
        
        self.update_log_display()
        
    def update_log_display(self):
        """更新日志显示"""
        if hasattr(self, 'log_text'):
            self.log_text.delete(1.0, tk.END)
            
            for log_entry in self.log_data:
                if not self.debug_mode and log_entry['type'] == 'debug':
                    continue
                    
                timestamp = log_entry['time']
                log_type = log_entry['type'].upper()
                message = log_entry['message']
                
                line = f"{timestamp} [{log_type}] {message}\n"
                self.log_text.insert(tk.END, line, log_entry['type'])
            
            self.log_text.see(tk.END)
            
    # 事件处理方法
    def toggle_recording(self):
        """切换录音状态"""
        self.is_recording = not self.is_recording
        self.play_button.configure(text="⏸" if self.is_recording else "▶")
        
        if self.is_recording:
            self.add_log("info", "开始音频录制")
        else:
            self.add_log("info", "停止音频录制")
            
    def update_split_time(self, value):
        """更新分段时间"""
        self.split_time = float(value)
        
    def set_frequency_unit(self, unit):
        """设置频率单位"""
        self.frequency_unit = unit
        self.show_measure_page()  # 刷新显示
        
    def adjust_frequency_range(self, direction):
        """调整频率范围"""
        range_size = self.frequency_range['max'] - self.frequency_range['min']
        step = range_size * 0.1
        
        if direction == 'left':
            self.frequency_range['min'] = max(0, self.frequency_range['min'] - step)
            self.frequency_range['max'] = max(step, self.frequency_range['max'] - step)
        else:
            self.frequency_range['min'] += step
            self.frequency_range['max'] += step
            
        self.show_measure_page()  # 刷新显示
        
    def reset_frequency_zoom(self):
        """重置频率缩放"""
        self.frequency_range = {"min": 1000, "max": 16000}
        self.show_measure_page()  # 刷新显示
        
    def apply_config(self):
        """应用配置设置"""
        try:
            # 应用分段时间
            self.split_time = self.config_split_scale.get()
            
            # 应用单位偏好
            self.frequency_unit = self.unit_var.get()
            
            # 应用频率范围
            start_freq = int(self.start_freq_entry.get())
            end_freq = int(self.end_freq_entry.get())
            
            if start_freq < end_freq:
                self.frequency_range['min'] = start_freq
                self.frequency_range['max'] = end_freq
                
                messagebox.showinfo("成功", "配置已应用")
                self.add_log("info", "配置设置已更新")
            else:
                messagebox.showerror("错误", "起始频率必须小于结束频率")
                
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            
    def toggle_debug_mode(self):
        """切换调试模式"""
        self.debug_mode = self.debug_var.get()
        self.update_log_display()
        
    def add_log(self, log_type, message):
        """添加日志条目"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_data.append({
            'time': timestamp,
            'type': log_type,
            'message': message
        })
        
        # 限制日志数量
        if len(self.log_data) > 100:
            self.log_data = self.log_data[-100:]
            
        # 如果日志页面正在显示，更新显示
        # 使用after方法在主线程中安全地更新UI
        if hasattr(self, 'log_text') and self.log_text.winfo_exists():
            self.root.after(0, self.update_log_display)
            
    def collect_noise_template(self):
        """采集一段噪声作为噪声模板，支持多样本"""
        try:
            messagebox.showinfo("噪声采集", "请保持环境噪声稳定，点击确定后开始采集噪声模板...")
            p = pyaudio.PyAudio()
            duration = 2  # 采集时长2秒
            rate = 16000
            chunk = 1024
            device_index = getattr(self, 'selected_mic_index', 0)
            
            try:
                stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, 
                               frames_per_buffer=chunk, input_device_index=device_index)
                frames = []
                for _ in range(int(rate / chunk * duration)):
                    data = stream.read(chunk, exception_on_overflow=False)
                    frames.append(data)
                stream.stop_stream()
                stream.close()
                
                audio = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0
                self.noise_templates.append(audio)
                self.refresh_noise_list()
                
                # 成功录制后显示消息
                messagebox.showinfo("噪声采集", "噪声模板采集完成，已加入列表。后续测量将自动去噪。")
                self.add_log("info", f"噪声模板采集成功，当前模板数: {len(self.noise_templates)}")
            finally:
                # 确保PyAudio实例被正确终止
                p.terminate()
                
        except Exception as e:
            messagebox.showerror("采集失败", str(e))
            self.add_log("error", f"噪声模板采集失败: {e}")

    def refresh_noise_list(self):
        """刷新噪声模板列表UI"""
        for widget in self.noise_list_frame.winfo_children():
            widget.destroy()
        if not self.noise_templates:
            tk.Label(self.noise_list_frame, text="无噪声模板", font=('Arial', 10), fg='#888', bg='#1a1a1a').pack()
            return
        for idx, _ in enumerate(self.noise_templates):
            row = tk.Frame(self.noise_list_frame, bg='#1a1a1a')
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"模板{idx+1}", font=('Arial', 10), fg='#fff', bg='#1a1a1a').pack(side=tk.LEFT, padx=5)
            del_btn = tk.Button(row, text="×", font=('Arial', 10, 'bold'), bg='#ef4444', fg='#fff', relief='flat', width=2, command=lambda i=idx: self.delete_noise_template(i))
            del_btn.pack(side=tk.RIGHT, padx=5)

    def delete_noise_template(self, idx):
        """删除指定噪声模板"""
        if 0 <= idx < len(self.noise_templates):
            del self.noise_templates[idx]
            self.refresh_noise_list()
            self.add_log("info", f"已删除噪声模板{idx+1}")

    def record_calib_sample(self):
        """录制2s音频样本，按类型保存，支持目标输入与补偿"""
        import tkinter.simpledialog as sd
        try:
            t = self.calib_type_var.get()
            # 1. 目标值输入
            target = None
            while target is None:
                val = sd.askstring("输入目标值", f"请输入本次录制的目标{t.upper()}值：")
                if val is None:
                    self.add_log("warn", f"取消录制{t}校准样本")
                    return
                try:
                    target = float(val)
                except Exception:
                    tk.messagebox.showerror("输入错误", "请输入有效数字！")
                    target = None
            messagebox.showinfo("录制校准样本", f"请保持目标信号稳定，点击确定后录制2秒({t})...")
            p = pyaudio.PyAudio()
            duration = 2
            rate = 16000
            chunk = 1024
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=chunk)
            frames = []
            for _ in range(int(rate / chunk * duration)):
                data = stream.read(chunk)
                frames.append(data)
            stream.stop_stream()
            stream.close()
            p.terminate()
            audio = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0
            # 2. 分析实际值
            actual = self.analyze_calib_actual(audio, t)
            self.add_log("info", f"录制{t}校准样本，目标: {target}，实际: {actual:.2f}")
            # 3. 计算补偿并保存
            compensation = target - actual
            if not hasattr(self, 'calib_compensations'):
                self.calib_compensations = {'hz': 0, 'db': 0, 'bpm': 0}
            self.calib_compensations[t] = compensation
            self.add_log("info", f"{t}补偿值: {compensation:+.2f} 已保存，后续测量将自动修正")
            # 4. 保存样本
            if not hasattr(self, 'calib_samples'):
                self.calib_samples = {'hz': [], 'db': [], 'bpm': []}
            self.calib_samples[t].append(audio)
            self.refresh_calib_sample_list()
            messagebox.showinfo("录制完成", f"{t}样本已保存，可多次录制。\n补偿值: {compensation:+.2f}")
        except Exception as e:
            messagebox.showerror("录制失败", str(e))
            self.add_log("error", f"录制校准样本失败: {e}")

    def analyze_calib_actual(self, audio, t):
        """分析录音样本的实际bpm/hz/db"""
        rate = 16000
        if t == 'bpm':
            try:
                bpm = librosa.beat.tempo(y=audio, sr=rate)[0]
                return float(bpm)
            except:
                return 0.0
        elif t == 'hz':
            try:
                fft = np.fft.rfft(audio)
                freqs = np.fft.rfftfreq(len(audio), 1/rate)
                main_freq = freqs[np.argmax(np.abs(fft))]
                return float(main_freq)
            except:
                return 0.0
        elif t == 'db':
            try:
                rms = np.sqrt(np.mean(audio**2))
                db = 20 * np.log10(rms + 1e-6)
                return float(db)
            except:
                return 0.0
        return 0.0

    def apply_calib_compensation(self, t, value):
        """测量时自动应用补偿"""
        if hasattr(self, 'calib_compensations') and t in self.calib_compensations:
            return value + self.calib_compensations[t]
        return value

    def estimate_from_microphone(self, duration=None, rate=16000, chunk=1024):
        duration = duration or self.split_time
        p = pyaudio.PyAudio()
        device_index = getattr(self, 'selected_mic_index', 0)
        
        try:
            stream = p.open(format=pyaudio.paInt16, 
                           channels=1, 
                           rate=rate, 
                           input=True, 
                           frames_per_buffer=chunk, 
                           input_device_index=device_index)
            frames = []
            for _ in range(int(rate / chunk * duration)):
                data = stream.read(chunk, exception_on_overflow=False)
                frames.append(data)
            stream.stop_stream()
            stream.close()
            
            audio = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0
            # 存储音频数据供频谱图使用
            self.audio_data = audio
        finally:
            # 确保PyAudio实例被正确终止
            p.terminate()
        # 多模板谱减法去噪
        if self.noise_templates:
            min_len = min([len(audio)] + [len(n) for n in self.noise_templates])
            audio = audio[:min_len]
            noise_stack = np.stack([n[:min_len] for n in self.noise_templates], axis=0)
            noise_mean = np.mean(noise_stack, axis=0)
            audio_fft = np.fft.rfft(audio)
            noise_fft = np.fft.rfft(noise_mean)
            clean_fft = audio_fft - np.abs(noise_fft)
            audio = np.fft.irfft(clean_fft)
        # BPM估算
        bpm = librosa.beat.tempo(y=audio, sr=rate)[0]
        # 主频估算
        fft = np.fft.rfft(audio)
        freqs = np.fft.rfftfreq(len(audio), 1/rate)
        main_freq = freqs[np.argmax(np.abs(fft))]
        # 响度估算
        rms = np.sqrt(np.mean(audio**2))
        db_raw = 20 * np.log10(rms + 1e-6)
        # 应用补偿
        bpm = self.apply_calib_compensation('bpm', bpm)
        main_freq = self.apply_calib_compensation('hz', main_freq)
        db = self.apply_calib_compensation('db', db_raw)
        return int(round(bpm)), int(round(db)), int(round(main_freq))

    def start_data_simulation(self):
        """启动真实麦克风音频采集线程"""
        def collect_data():
            while True:
                if self.is_recording:
                    try:
                        bpm, db, hz = self.estimate_from_microphone(duration=self.split_time)
                        self.current_bpm = bpm
                        self.current_db = db
                        self.current_hz = hz
                        # 新增：采集波形数据和时间戳
                        self.waveform_data = self.waveform_data[-99:] + [random.uniform(-1, 1) for _ in range(100)]
                    
                        # 修正：使用split_time的倍数作为时间戳，确保与表格显示一致
                        if not self.time_history:
                            self.start_time = time.time()
                            self.time_counter = 0
                        else:
                            self.time_counter += 1
                    
                        # 使用理论时间（split_time的倍数）而不是实际时间
                        self.time_history.append(round(self.time_counter * self.split_time, 3))
                    except Exception as e:
                        self.add_log("error", f"音频采集/分析失败: {e}")
                    self.root.after(0, self.update_displays)
                    self.bpm_history.append(self.current_bpm)
                    self.db_history.append(self.current_db)
                    self.hz_history.append(self.current_hz)
                    if len(self.bpm_history) > 50:
                        self.bpm_history = self.bpm_history[-50:]
                        self.db_history = self.db_history[-50:]
                        self.hz_history = self.hz_history[-50:]
                        self.time_history = self.time_history[-50:]
                time.sleep(self.split_time)
        # 在后台线程中运行数据采集
        data_thread = threading.Thread(target=collect_data, daemon=True)
        data_thread.start()
        
    def on_spectrum_click(self, event):
        """处理频谱图点击事件，保存频谱图"""
        if event.inaxes == self.ax:
            # 创建保存对话框
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                title="保存频谱图"
            )
            
            if file_path:
                try:
                    self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                    messagebox.showinfo("保存成功", f"频谱图已保存至:\n{file_path}")
                    self.add_log("info", f"频谱图已保存至: {file_path}")
                except Exception as e:
                    messagebox.showerror("保存失败", f"保存频谱图时出错:\n{str(e)}")
                    self.add_log("error", f"保存频谱图失败: {str(e)}")
    
    def update_displays(self):
        """更新显示数据"""
        # 更新数字显示
        if hasattr(self, 'bpm_label'):
            self.bpm_label.configure(text=f"{self.current_bpm}")
        if hasattr(self, 'db_label'):
            self.db_label.configure(text=f"{self.current_db} dB")
        if hasattr(self, 'hz_label'):
            hz_display = f"{self.current_hz/1000:.1f} kHz" if self.frequency_unit == 'kHz' else f"{self.current_hz} Hz"
            self.hz_label.configure(text=hz_display)
            
        # 更新频谱图
        if hasattr(self, 'spectrum_line') and self.audio_data is not None and len(self.audio_data) > 1:
            # 计算FFT
            n = len(self.audio_data)
            fft_data = np.fft.rfft(self.audio_data * np.hamming(n))
            fft_freq = np.fft.rfftfreq(n, d=1.0/self.sample_rate)
            fft_magnitude = np.abs(fft_data)
            
            # 更新频谱图
            self.spectrum_line.set_data(fft_freq, fft_magnitude)
            self.ax.set_xlim(0, self.sample_rate/2)  # 设置x轴范围为0到采样率的一半
            self.ax.set_ylim(0, np.max(fft_magnitude) * 1.1 or 1)  # 动态调整y轴
            self.canvas.draw_idle()

    def reset_measure_data(self):
        """重置所有测量数据和显示"""
        self.bpm_history = []
        self.db_history = []
        self.hz_history = []
        self.time_history = []
        self.waveform_data = []
        self.current_bpm = 0
        self.current_db = 0
        self.current_hz = 0
        self.add_log("info", "测量数据已重置")
        self.update_displays()
        self.update_stats_plot()
        # 频率图归零
        if hasattr(self, 'freq_ax'):
            self.freq_ax.clear()
            self.freq_canvas.draw()

    def export_csv(self):
        """导出time-bpm-db-hz为CSV"""
        if not self.bpm_history:
            messagebox.showwarning("无数据", "没有可导出的测量数据！")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV文件', '*.csv')],
            title='导出CSV'
        )
        if not file_path:
            return
        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['time', 'bpm', 'db', 'hz'])
                for i in range(len(self.bpm_history)):
                    # 确保使用一致的时间戳，如果time_history不足，则使用理论时间
                    if i < len(self.time_history):
                        t = self.time_history[i]
                    else:
                        t = round(i * self.split_time, 3)
                    writer.writerow([t, self.bpm_history[i], self.db_history[i], self.hz_history[i]])
            messagebox.showinfo("导出成功", f"数据已导出到: {file_path}")
            self.add_log("info", f"测量数据导出CSV: {file_path}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))
            self.add_log("error", f"CSV导出失败: {e}")

    def show_advanced_calib_page(self):
        """显示高级校准页面，支持多样本录制/删除，类型选择"""
        self.set_active_nav("高级校准")
        self.clear_content()
        calib_frame = tk.Frame(self.content_frame, bg='#000000')
        calib_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        # 校准类型选择
        tk.Label(calib_frame, text="校准类型：", font=('Arial', 12, 'bold'), fg='#fff', bg='#000000').pack(anchor='w')
        self.calib_type_var = tk.StringVar(value='hz')
        type_frame = tk.Frame(calib_frame, bg='#000000')
        type_frame.pack(anchor='w', pady=5)
        for t, label in [('hz', '主频Hz'), ('db', '响度dB'), ('bpm', 'BPM')]:
            tk.Radiobutton(type_frame, text=label, variable=self.calib_type_var, value=t, font=('Arial', 10), fg='#fff', bg='#000000', selectcolor='#404040').pack(side=tk.LEFT, padx=10)
        # 录制按钮
        tk.Button(calib_frame, text="录制2s样本", font=('Arial', 12, 'bold'), bg='#3b82f6', fg='#fff', command=self.record_calib_sample).pack(pady=10)
        # 样本列表
        self.calib_sample_frame = tk.Frame(calib_frame, bg='#1a1a1a')
        self.calib_sample_frame.pack(fill=tk.X, pady=5)
        self.refresh_calib_sample_list()

    def record_calib_sample(self):
        """录制2s音频样本，按类型保存，支持目标输入与补偿"""
        import tkinter.simpledialog as sd
        try:
            # 确保calib_type_var存在
            if not hasattr(self, 'calib_type_var'):
                self.add_log("error", "校准类型变量不存在")
                return
                
            t = self.calib_type_var.get()
            # 1. 目标值输入
            target = None
            while target is None:
                val = sd.askstring("输入目标值", f"请输入本次录制的目标{t.upper()}值：")
                if val is None:
                    self.add_log("info", f"取消录制{t}校准样本")
                    return
                try:
                    target = float(val)
                except Exception:
                    tk.messagebox.showerror("输入错误", "请输入有效数字！")
                    target = None
                    
            messagebox.showinfo("录制校准样本", f"请保持目标信号稳定，点击确定后录制2秒({t})...")
            
            # 使用当前选择的麦克风
            device_index = getattr(self, 'selected_mic_index', 0)
            p = pyaudio.PyAudio()
            duration = 2
            rate = 16000
            chunk = 1024
            
            try:
                stream = p.open(format=pyaudio.paInt16, 
                               channels=1, 
                               rate=rate, 
                               input=True, 
                               frames_per_buffer=chunk,
                               input_device_index=device_index)
                               
                frames = []
                for _ in range(int(rate / chunk * duration)):
                    data = stream.read(chunk, exception_on_overflow=False)
                    frames.append(data)
                    
                stream.stop_stream()
                stream.close()
                
                audio = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0
                
                # 2. 分析实际值
                actual = self.analyze_calib_actual(audio, t)
                self.add_log("info", f"录制{t}校准样本，目标: {target}，实际: {actual:.2f}")
                
                # 3. 计算补偿并保存
                compensation = target - actual
                if not hasattr(self, 'calib_compensations'):
                    self.calib_compensations = {'hz': 0, 'db': 0, 'bpm': 0}
                self.calib_compensations[t] = compensation
                self.add_log("info", f"{t}补偿值: {compensation:+.2f} 已保存，后续测量将自动修正")
                
                # 4. 保存样本
                if not hasattr(self, 'calib_samples'):
                    self.calib_samples = {'hz': [], 'db': [], 'bpm': []}
                self.calib_samples[t].append(audio)
                
                # 使用after方法在主线程中安全地更新UI
                if hasattr(self, 'root') and self.root.winfo_exists():
                    self.root.after(0, self.refresh_calib_sample_list)
                else:
                    self.refresh_calib_sample_list()
                
                messagebox.showinfo("录制完成", f"{t}样本已保存，可多次录制。\n补偿值: {compensation:+.2f}")
            finally:
                # 确保PyAudio实例被正确终止
                p.terminate()
                
        except Exception as e:
            messagebox.showerror("录制失败", str(e))
            self.add_log("error", f"录制校准样本失败: {e}")

    def analyze_calib_actual(self, audio, t):
        """分析录音样本的实际bpm/hz/db"""
        rate = 16000
        if t == 'bpm':
            try:
                bpm = librosa.beat.tempo(y=audio, sr=rate)[0]
                return float(bpm)
            except:
                return 0.0
        elif t == 'hz':
            try:
                fft = np.fft.rfft(audio)
                freqs = np.fft.rfftfreq(len(audio), 1/rate)
                main_freq = freqs[np.argmax(np.abs(fft))]
                return float(main_freq)
            except:
                return 0.0
        elif t == 'db':
            try:
                rms = np.sqrt(np.mean(audio**2))
                db = 20 * np.log10(rms + 1e-6)
                return float(db)
            except:
                return 0.0
        return 0.0

    def refresh_calib_sample_list(self):
        """刷新校准样本列表UI"""
        # 检查UI组件是否仍然存在
        if not hasattr(self, 'calib_sample_frame') or not self.calib_sample_frame.winfo_exists():
            return
            
        try:
            for widget in self.calib_sample_frame.winfo_children():
                widget.destroy()
                
            if not hasattr(self, 'calib_samples'):
                self.calib_samples = {'hz': [], 'db': [], 'bpm': []}
                
            t = getattr(self, 'calib_type_var', None)
            t = t.get() if t and hasattr(t, 'get') else 'hz'
            samples = self.calib_samples.get(t, [])
            
            if not samples:
                tk.Label(self.calib_sample_frame, text="无样本", font=('Arial', 10), fg='#888', bg='#1a1a1a').pack()
                return
                
            for idx, _ in enumerate(samples):
                row = tk.Frame(self.calib_sample_frame, bg='#1a1a1a')
                row.pack(fill=tk.X, pady=2)
                tk.Label(row, text=f"{t.upper()}样本{idx+1}", font=('Arial', 10), fg='#fff', bg='#1a1a1a').pack(side=tk.LEFT, padx=5)
                del_btn = tk.Button(row, text="×", font=('Arial', 10, 'bold'), bg='#ef4444', fg='#fff', relief='flat', width=2, command=lambda i=idx, typ=t: self.delete_calib_sample(typ, i))
                del_btn.pack(side=tk.RIGHT, padx=5)
        except Exception as e:
            # 捕获可能的错误，避免UI更新失败导致程序崩溃
            self.add_log("error", f"刷新校准样本列表失败: {e}")

    def delete_calib_sample(self, typ, idx):
        """删除指定类型的校准样本"""
        if hasattr(self, 'calib_samples') and typ in self.calib_samples and 0 <= idx < len(self.calib_samples[typ]):
            del self.calib_samples[typ][idx]
            self.refresh_calib_sample_list()
            self.add_log("info", f"已删除{typ}校准样本{idx+1}")

    def record_calibration_sample(self, cal_type):
        """录制校准样本，弹窗输入目标值，分析实际值，保存补偿"""
        # 弹窗输入目标值
        target = self.ask_target_value(cal_type)
        if target is None:
            self.add_log("warn", f"取消录制{cal_type}校准样本")
            return
        self.add_log("info", f"录制{cal_type}校准样本，目标: {target}")
        # 录音
        audio = self.record_audio(duration=2)
        # 分析实际值
        actual = self.analyze_calibration_value(audio, cal_type)
        self.add_log("info", f"实际{cal_type}: {actual:.2f}")
        # 计算补偿
        compensation = target - actual
        self.save_calibration_compensation(cal_type, compensation)
        self.add_log("info", f"补偿值: {compensation:+.2f} 已保存")
        # 保存样本（如有需要）
        # ...existing code...

    def ask_target_value(self, cal_type):
        """弹窗让用户输入目标bpm/hz/db"""
        import tkinter.simpledialog as sd
        prompt = f"请输入本次录制的目标{cal_type.upper()}值："
        while True:
            val = sd.askstring("输入目标值", prompt)
            if val is None:
                return None
            try:
                v = float(val)
                return v
            except Exception:
                tk.messagebox.showerror("输入错误", "请输入有效数字！")

    def analyze_calibration_value(self, audio, cal_type):
        """分析录音样本的实际bpm/hz/db"""
        # 这里假设已有相关分析函数
        if cal_type == 'bpm':
            return self.estimate_bpm(audio)
        elif cal_type == 'hz':
            return self.estimate_hz(audio)
        elif cal_type == 'db':
            return self.estimate_db(audio)
        else:
            return 0

    def save_calibration_compensation(self, cal_type, compensation):
        """保存补偿参数到字典并持久化"""
        if not hasattr(self, 'calibration_compensations'):
            self.calibration_compensations = {'bpm': 0, 'hz': 0, 'db': 0}
        self.calibration_compensations[cal_type] = compensation
        # 可扩展为写入文件
        # with open('calibration_compensations.json', 'w') as f:
        #     json.dump(self.calibration_compensations, f)

    def apply_calibration_compensation(self, cal_type, value):
        """测量时自动应用补偿"""
        if hasattr(self, 'calibration_compensations') and cal_type in self.calibration_compensations:
            return value + self.calibration_compensations[cal_type]
        return value

    # 在测量/估算bpm/hz/db时调用apply_calibration_compensation
    def update_measurement_display(self, bpm, hz, db):
        bpm = self.apply_calibration_compensation('bpm', bpm)
        hz = self.apply_calibration_compensation('hz', hz)
        db = self.apply_calibration_compensation('db', db)
        # ...existing code...

def main():
    """主函数"""
    root = tk.Tk()
    app = AudioProcessorGUI(root)
    
    # 设置窗口图标（如果有的话）
    try:
        # root.iconbitmap('icon.ico')  # 如果有图标文件
        pass
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()