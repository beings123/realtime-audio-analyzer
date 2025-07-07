from flask import Blueprint, jsonify
import random
import time
import threading
from datetime import datetime

audio_bp = Blueprint('audio', __name__)

# 全局数据存储
audio_data = {
    'bpm': 170,
    'db': 25,
    'hz': 2500,
    'timestamp': datetime.now().isoformat(),
    'is_recording': False,
    'split_time': 2.0,
    'frequency_range': {'min': 1000, 'max': 16000},
    'history': {
        'bpm': [],
        'db': [],
        'hz': [],
        'timestamps': []
    }
}

# 数据更新锁
data_lock = threading.Lock()

def simulate_audio_data():
    """模拟音频数据更新"""
    while True:
        with data_lock:
            if audio_data['is_recording']:
                # 模拟BPM变化 (120-200)
                audio_data['bpm'] = max(120, min(200, 
                    audio_data['bpm'] + random.randint(-5, 5)))
                
                # 模拟dB变化 (10-50)
                audio_data['db'] = max(10, min(50, 
                    audio_data['db'] + random.randint(-3, 3)))
                
                # 模拟Hz变化 (1000-5000)
                audio_data['hz'] = max(1000, min(5000, 
                    audio_data['hz'] + random.randint(-200, 200)))
                
                # 更新时间戳
                audio_data['timestamp'] = datetime.now().isoformat()
                
                # 添加到历史数据
                audio_data['history']['bpm'].append(audio_data['bpm'])
                audio_data['history']['db'].append(audio_data['db'])
                audio_data['history']['hz'].append(audio_data['hz'])
                audio_data['history']['timestamps'].append(audio_data['timestamp'])
                
                # 限制历史数据长度
                max_history = 100
                for key in audio_data['history']:
                    if len(audio_data['history'][key]) > max_history:
                        audio_data['history'][key] = audio_data['history'][key][-max_history:]
        
        time.sleep(audio_data['split_time'])

# 启动后台数据模拟线程
simulation_thread = threading.Thread(target=simulate_audio_data, daemon=True)
simulation_thread.start()

@audio_bp.route('/status', methods=['GET'])
def get_status():
    """获取API状态"""
    return jsonify({
        'status': 'running',
        'message': 'Audio API Server is running',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@audio_bp.route('/data', methods=['GET'])
def get_audio_data():
    """获取当前音频数据"""
    with data_lock:
        return jsonify({
            'bpm': audio_data['bpm'],
            'db': audio_data['db'],
            'hz': audio_data['hz'],
            'timestamp': audio_data['timestamp'],
            'is_recording': audio_data['is_recording'],
            'split_time': audio_data['split_time'],
            'frequency_range': audio_data['frequency_range']
        })

@audio_bp.route('/data/bpm', methods=['GET'])
def get_bpm():
    """获取当前BPM数据"""
    with data_lock:
        return jsonify({
            'bpm': audio_data['bpm'],
            'timestamp': audio_data['timestamp']
        })

@audio_bp.route('/data/db', methods=['GET'])
def get_db():
    """获取当前dB数据"""
    with data_lock:
        return jsonify({
            'db': audio_data['db'],
            'timestamp': audio_data['timestamp']
        })

@audio_bp.route('/data/hz', methods=['GET'])
def get_hz():
    """获取当前Hz数据"""
    with data_lock:
        return jsonify({
            'hz': audio_data['hz'],
            'timestamp': audio_data['timestamp']
        })

@audio_bp.route('/history', methods=['GET'])
def get_history():
    """获取历史数据"""
    with data_lock:
        return jsonify({
            'history': audio_data['history'],
            'count': len(audio_data['history']['bpm']),
            'timestamp': datetime.now().isoformat()
        })

@audio_bp.route('/recording/start', methods=['POST'])
def start_recording():
    """开始录制"""
    with data_lock:
        audio_data['is_recording'] = True
        return jsonify({
            'status': 'success',
            'message': 'Recording started',
            'is_recording': audio_data['is_recording'],
            'timestamp': datetime.now().isoformat()
        })

@audio_bp.route('/recording/stop', methods=['POST'])
def stop_recording():
    """停止录制"""
    with data_lock:
        audio_data['is_recording'] = False
        return jsonify({
            'status': 'success',
            'message': 'Recording stopped',
            'is_recording': audio_data['is_recording'],
            'timestamp': datetime.now().isoformat()
        })

@audio_bp.route('/recording/status', methods=['GET'])
def get_recording_status():
    """获取录制状态"""
    with data_lock:
        return jsonify({
            'is_recording': audio_data['is_recording'],
            'timestamp': audio_data['timestamp']
        })

@audio_bp.route('/config', methods=['GET'])
def get_config():
    """获取配置信息"""
    with data_lock:
        return jsonify({
            'split_time': audio_data['split_time'],
            'frequency_range': audio_data['frequency_range'],
            'timestamp': datetime.now().isoformat()
        })

@audio_bp.route('/config/split_time/<float:split_time>', methods=['POST'])
def set_split_time(split_time):
    """设置分段时间"""
    if 0.5 <= split_time <= 10.0:
        with data_lock:
            audio_data['split_time'] = split_time
            return jsonify({
                'status': 'success',
                'message': f'Split time set to {split_time}s',
                'split_time': audio_data['split_time'],
                'timestamp': datetime.now().isoformat()
            })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Split time must be between 0.5 and 10.0 seconds',
            'timestamp': datetime.now().isoformat()
        }), 400

@audio_bp.route('/esp32/data', methods=['GET'])
def get_esp32_data():
    """专为ESP32优化的数据接口"""
    with data_lock:
        return jsonify({
            'bpm': audio_data['bpm'],
            'db': audio_data['db'],
            'hz': audio_data['hz'],
            'recording': 1 if audio_data['is_recording'] else 0,
            'timestamp': int(time.time())  # Unix时间戳，ESP32更容易处理
        })

@audio_bp.route('/esp32/simple', methods=['GET'])
def get_esp32_simple():
    """ESP32简化数据接口（纯数值）"""
    with data_lock:
        # 返回简单的逗号分隔值，便于ESP32解析
        return f"{audio_data['bpm']},{audio_data['db']},{audio_data['hz']},{1 if audio_data['is_recording'] else 0}"

