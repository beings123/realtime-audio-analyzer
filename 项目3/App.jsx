import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Slider } from '@/components/ui/slider.jsx'
import { Switch } from '@/components/ui/switch.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Play, Pause, RotateCcw, ChevronLeft, ChevronRight } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import './App.css'

function App() {
  const [isRecording, setIsRecording] = useState(false)
  const [bpm, setBpm] = useState(0)
  const [db, setDb] = useState(0)
  const [hz, setHz] = useState(0)
  const [splitTime, setSplitTime] = useState([2])
  const [frequencyUnit, setFrequencyUnit] = useState('Hz')
  const [frequencyRange, setFrequencyRange] = useState({ min: 20, max: 20000 })
  const [showBpmChart, setShowBpmChart] = useState(true)
  const [showDbChart, setShowDbChart] = useState(true)
  const [showHzChart, setShowHzChart] = useState(false)
  const [debugMode, setDebugMode] = useState(false)
  
  // 模拟数据
  const [chartData, setChartData] = useState([])
  const [waveformData, setWaveformData] = useState([])
  const [logData, setLogData] = useState([
    { time: '10:30:15', type: 'info', message: '音频检测已启动' },
    { time: '10:30:16', type: 'info', message: 'BPM检测正常运行' },
    { time: '10:30:17', type: 'debug', message: '频谱分析完成' }
  ])

  // 生成模拟波形数据
  useEffect(() => {
    const generateWaveform = () => {
      const data = []
      for (let i = 0; i < 100; i++) {
        data.push({
          x: i,
          y: Math.sin(i * 0.1) * 50 + Math.random() * 20
        })
      }
      setWaveformData(data)
    }
    
    const generateChartData = () => {
      const data = []
      for (let i = 0; i < 20; i++) {
        data.push({
          time: i * splitTime[0],
          bpm: 160 + Math.random() * 20,
          db: 20 + Math.random() * 15,
          hz: 2000 + Math.random() * 1000
        })
      }
      setChartData(data)
    }

    generateWaveform()
    generateChartData()
  }, [splitTime])

  // 数字显示组件
  const PixelNumber = ({ value, unit, size = 'large' }) => {
    const textSize = size === 'large' ? 'text-6xl' : 'text-2xl'
    return (
      <div className={`font-mono ${textSize} font-bold text-white tracking-wider`}>
        <span className="pixel-text">{value}</span>
        <span className="text-lg ml-2 text-blue-300">{unit}</span>
      </div>
    )
  }

  const toggleRecording = () => {
    setIsRecording(!isRecording)
  }

  const resetZoom = () => {
    setFrequencyRange({ min: 20, max: 20000 })
  }

  const adjustFrequencyRange = (direction) => {
    const range = frequencyRange.max - frequencyRange.min
    const step = range * 0.1
    if (direction === 'left') {
      setFrequencyRange({
        min: Math.max(0, frequencyRange.min - step),
        max: Math.max(step, frequencyRange.max - step)
      })
    } else {
      setFrequencyRange({
        min: frequencyRange.min + step,
        max: frequencyRange.max + step
      })
    }
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <Tabs defaultValue="measure" className="w-full">
        {/* 顶部导航栏 */}
        <TabsList className="w-full bg-black border-b border-gray-800 rounded-none h-12">
          <TabsTrigger value="measure" className="text-blue-300 data-[state=active]:text-white data-[state=active]:border-b-2 data-[state=active]:border-blue-400">
            测量
          </TabsTrigger>
          <TabsTrigger value="stats" className="text-blue-300 data-[state=active]:text-white data-[state=active]:border-b-2 data-[state=active]:border-blue-400">
            统计
          </TabsTrigger>
          <TabsTrigger value="config" className="text-blue-300 data-[state=active]:text-white data-[state=active]:border-b-2 data-[state=active]:border-blue-400">
            配置
          </TabsTrigger>
          <TabsTrigger value="log" className="text-blue-300 data-[state=active]:text-white data-[state=active]:border-b-2 data-[state=active]:border-blue-400">
            日志
          </TabsTrigger>
        </TabsList>

        {/* 测量页面 */}
        <TabsContent value="measure" className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-120px)]">
            {/* 左侧：数字显示区 */}
            <div className="flex flex-col justify-center items-center space-y-8">
              <PixelNumber value={bpm} unit="BPM" />
              <div className="space-y-2">
                <PixelNumber value={db} unit="dB" size="small" />
                <PixelNumber value={hz/1000} unit="kHz" size="small" />
              </div>
            </div>

            {/* 中部：图形波形区 */}
            <div className="flex flex-col space-y-4">
              <div className="flex justify-center">
                <Button
                  onClick={toggleRecording}
                  className="w-16 h-16 rounded-full bg-gray-700 hover:bg-gray-600"
                >
                  {isRecording ? <Pause className="w-8 h-8" /> : <Play className="w-8 h-8" />}
                </Button>
              </div>
              
              <Card className="bg-gray-900 border-gray-700 flex-1">
                <CardContent className="p-4 h-full">
                  <div className="h-full flex items-center justify-center">
                    <svg width="100%" height="200" className="border border-gray-700">
                      <polyline
                        fill="none"
                        stroke="#3b82f6"
                        strokeWidth="2"
                        points={waveformData.map((point, index) => 
                          `${(index / waveformData.length) * 100}%,${50 + point.y}%`
                        ).join(' ')}
                      />
                    </svg>
                  </div>
                </CardContent>
              </Card>

              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-400">Split Time</span>
                <Slider
                  value={splitTime}
                  onValueChange={setSplitTime}
                  max={10}
                  min={1}
                  step={0.5}
                  className="flex-1"
                />
                <span className="text-sm text-gray-400">{splitTime[0]}s</span>
              </div>
            </div>

            {/* 右侧：频率图 + 操作区 */}
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Button
                  variant={frequencyUnit === 'Hz' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFrequencyUnit('Hz')}
                >
                  Hz
                </Button>
                <Button
                  variant={frequencyUnit === 'kHz' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFrequencyUnit('kHz')}
                >
                  kHz
                </Button>
              </div>

              <div className="text-sm text-gray-400">
                f = {frequencyRange.min} Hz ~ {frequencyRange.max} Hz
              </div>

              <Card className="bg-gray-900 border-gray-700 flex-1">
                <CardContent className="p-4 h-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={waveformData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis stroke="#9ca3af" />
                      <YAxis stroke="#9ca3af" />
                      <Line type="monotone" dataKey="y" stroke="#3b82f6" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <div className="flex items-center justify-between">
                <div className="flex space-x-2">
                  <Button size="sm" variant="outline" onClick={() => adjustFrequencyRange('left')}>
                    <ChevronLeft className="w-4 h-4" />
                    <ChevronLeft className="w-4 h-4 -ml-2" />
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => adjustFrequencyRange('right')}>
                    <ChevronRight className="w-4 h-4" />
                    <ChevronRight className="w-4 h-4 -ml-2" />
                  </Button>
                </div>
                <Button size="sm" variant="outline" onClick={resetZoom}>
                  <RotateCcw className="w-4 h-4 mr-2" />
                  重置缩放
                </Button>
              </div>
            </div>
          </div>
        </TabsContent>

        {/* 统计页面 */}
        <TabsContent value="stats" className="p-6">
          <div className="space-y-6">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <Switch checked={showBpmChart} onCheckedChange={setShowBpmChart} />
                <span className="text-sm">BPM</span>
              </div>
              <div className="flex items-center space-x-2">
                <Switch checked={showDbChart} onCheckedChange={setShowDbChart} />
                <span className="text-sm">dB</span>
              </div>
              <div className="flex items-center space-x-2">
                <Switch checked={showHzChart} onCheckedChange={setShowHzChart} />
                <span className="text-sm">Hz</span>
              </div>
            </div>

            <Card className="bg-gray-900 border-gray-700">
              <CardContent className="p-6">
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis 
                      dataKey="time" 
                      stroke="#9ca3af"
                      label={{ value: `n × ${splitTime[0]}s`, position: 'insideBottom', offset: -10 }}
                    />
                    <YAxis stroke="#9ca3af" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1f2937', 
                        border: '1px solid #374151',
                        borderRadius: '6px'
                      }}
                    />
                    {showBpmChart && <Line type="monotone" dataKey="bpm" stroke="#ef4444" strokeWidth={2} name="BPM" />}
                    {showDbChart && <Line type="monotone" dataKey="db" stroke="#22c55e" strokeWidth={2} name="dB" />}
                    {showHzChart && <Line type="monotone" dataKey="hz" stroke="#3b82f6" strokeWidth={2} name="Hz" />}
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 配置页面 */}
        <TabsContent value="config" className="p-6">
          <div className="max-w-2xl space-y-8">
            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle>分段时间设置</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-4">
                  <span className="text-sm w-24">Split Time</span>
                  <Slider
                    value={splitTime}
                    onValueChange={setSplitTime}
                    max={10}
                    min={0.5}
                    step={0.5}
                    className="flex-1"
                  />
                  <span className="text-sm w-12">{splitTime[0]}s</span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle>单位偏好</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex space-x-4">
                  <Button
                    variant={frequencyUnit === 'Hz' ? 'default' : 'outline'}
                    onClick={() => setFrequencyUnit('Hz')}
                  >
                    Hz
                  </Button>
                  <Button
                    variant={frequencyUnit === 'kHz' ? 'default' : 'outline'}
                    onClick={() => setFrequencyUnit('kHz')}
                  >
                    kHz
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle>频谱范围设置</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm text-gray-400">起始频率 (Hz)</label>
                    <input
                      type="number"
                      value={frequencyRange.min}
                      onChange={(e) => setFrequencyRange({...frequencyRange, min: parseInt(e.target.value)})}
                      className="w-full mt-1 px-3 py-2 bg-gray-800 border border-gray-600 rounded-md text-white"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-gray-400">结束频率 (Hz)</label>
                    <input
                      type="number"
                      value={frequencyRange.max}
                      onChange={(e) => setFrequencyRange({...frequencyRange, max: parseInt(e.target.value)})}
                      className="w-full mt-1 px-3 py-2 bg-gray-800 border border-gray-600 rounded-md text-white"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 日志页面 */}
        <TabsContent value="log" className="p-6">
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <Switch checked={debugMode} onCheckedChange={setDebugMode} />
              <span className="text-sm">显示调试日志</span>
            </div>

            <Card className="bg-gray-900 border-gray-700">
              <CardContent className="p-4">
                <div className="h-96 overflow-y-auto space-y-2 font-mono text-sm">
                  {logData
                    .filter(log => debugMode || log.type !== 'debug')
                    .map((log, index) => (
                    <div key={index} className="flex space-x-4">
                      <span className="text-gray-500">{log.time}</span>
                      <span className={`${
                        log.type === 'error' ? 'text-red-400' : 
                        log.type === 'debug' ? 'text-yellow-400' : 
                        'text-green-400'
                      }`}>
                        [{log.type.toUpperCase()}]
                      </span>
                      <span>{log.message}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default App

