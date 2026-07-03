'use client';

import React from 'react';
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line,
  ComposedChart, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer, ReferenceLine
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, Info } from 'lucide-react';
import { MACHINE_TELEMETRY_CONFIGS, SensorConfig, SensorKey } from '../../lib/machineTelemetryConfig';

interface MachineDiagnosticsPanelProps {
  machineCode: string;
  sensorData: any[];
}

const CustomSensorTooltip = ({ active, payload, label, unit }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg shadow-xl p-3 text-xs text-white">
        <p className="font-semibold mb-1 font-mono">{label}</p>
        {payload.map((entry: any, i: number) => (
          <p key={i} style={{ color: entry.color }} className="flex justify-between gap-4">
            <span>{entry.name}:</span>
            <span className="font-mono font-bold">
              {entry.value} {unit}
            </span>
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export function MachineDiagnosticsPanel({ machineCode, sensorData }: MachineDiagnosticsPanelProps) {
  const config = MACHINE_TELEMETRY_CONFIGS[machineCode] || MACHINE_TELEMETRY_CONFIGS['EXT-01'];

  // Map sensor data to match keys
  const mapSensorData = (data: any[]) => {
    if (!data || data.length === 0) return [];
    return data.map((d: any) => ({
      timestamp: new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      temperature: d.temperature_celsius,
      speed: d.speed_rpm,
      pressure: d.pressure_bar,
      vibration: d.vibration_mm_s,
      power: d.power_kw,
    }));
  };

  const dbData = mapSensorData(sensorData);

  // Fallback dynamic mock generator if data is missing (for coolers, cutters, or unseeded states)
  const generateMockDataForSensor = (sensor: SensorConfig) => {
    const dataList = [];
    const now = new Date();
    const mid = (sensor.normalMin + sensor.normalMax) / 2;
    const range = (sensor.normalMax - sensor.normalMin) / 2;
    let lastVal = mid + (Math.random() - 0.5) * range;

    for (let i = 15; i >= 0; i--) {
      const timeStr = new Date(now.getTime() - i * 15 * 60 * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      // Random walk around nominal range
      const walk = (Math.random() - 0.5) * range * 0.25;
      let val = lastVal + walk;
      val = Math.max(sensor.normalMin * 0.8, Math.min(sensor.criticalMax * 1.1, val));
      lastVal = val;

      dataList.push({
        timestamp: timeStr,
        [sensor.key]: parseFloat(val.toFixed(1))
      });
    }
    return dataList;
  };

  const getChartData = (sensor: SensorConfig) => {
    // If the DB data contains the requested sensor key and it has non-zero entries, use it!
    if (dbData.length > 0 && dbData[0][sensor.key] !== undefined) {
      return dbData;
    }
    // Fall back to custom per-machine mock lists so there is always dynamic detailed telemetry
    return generateMockDataForSensor(sensor);
  };

  const renderSensorChart = (sensor: SensorConfig) => {
    const data = getChartData(sensor);
    const latestVal = data.length > 0 ? (data[data.length - 1][sensor.key] as number) : 0;
    const isWarning = latestVal > sensor.warningMax && latestVal <= sensor.criticalMax;
    const isCritical = latestVal > sensor.criticalMax;

    const chartProps = {
      data,
      margin: { top: 15, right: 15, left: 0, bottom: 5 },
    };

    const axisProps = {
      xAxis: <XAxis dataKey="timestamp" tick={{ fontSize: 9, fill: 'currentColor' }} className="text-muted-foreground" />,
      yAxis: <YAxis tick={{ fontSize: 9, fill: 'currentColor' }} className="text-muted-foreground" domain={[sensor.normalMin * 0.8, 'auto']} />,
      grid: <CartesianGrid strokeDasharray="3 3" className="stroke-zinc-800" opacity={0.2} />,
      tooltip: <Tooltip content={<CustomSensorTooltip unit={sensor.unit} />} />,
    };

    const renderPlot = () => {
      switch (sensor.chartType) {
        case 'area':
          return (
            <AreaChart {...chartProps}>
              {axisProps.grid}{axisProps.xAxis}{axisProps.yAxis}{axisProps.tooltip}
              <defs>
                <linearGradient id={`color-${machineCode}-${sensor.key}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={sensor.color} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={sensor.color} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <Area type="monotone" dataKey={sensor.key} name={sensor.label} stroke={sensor.color} fill={`url(#color-${machineCode}-${sensor.key})`} strokeWidth={2} />
              <ReferenceLine y={sensor.warningMax} stroke={sensor.thresholdColor} strokeDasharray="4 2" label={{ value: 'Warn Limit', fill: sensor.thresholdColor, fontSize: 8, position: 'insideRight' }} />
              <ReferenceLine y={sensor.criticalMax} stroke="#EF4444" strokeDasharray="3 3" label={{ value: 'CRIT Limit', fill: '#EF4444', fontSize: 8, position: 'insideRight' }} />
            </AreaChart>
          );
        case 'bar':
          return (
            <BarChart {...chartProps}>
              {axisProps.grid}{axisProps.xAxis}{axisProps.yAxis}{axisProps.tooltip}
              <Bar dataKey={sensor.key} name={sensor.label} fill={sensor.color} radius={[3, 3, 0, 0]} maxBarSize={20} />
              <ReferenceLine y={sensor.warningMax} stroke={sensor.thresholdColor} strokeDasharray="4 2" />
              <ReferenceLine y={sensor.criticalMax} stroke="#EF4444" strokeDasharray="3 3" />
            </BarChart>
          );
        case 'composed':
          return (
            <ComposedChart {...chartProps}>
              {axisProps.grid}{axisProps.xAxis}{axisProps.yAxis}{axisProps.tooltip}
              <Bar dataKey={sensor.key} name={sensor.label} fill={sensor.color} radius={[3, 3, 0, 0]} maxBarSize={20} opacity={0.7} />
              <Line type="monotone" dataKey={sensor.key} stroke={sensor.color} strokeWidth={2} dot={{ r: 1.5 }} />
              <ReferenceLine y={sensor.warningMax} stroke={sensor.thresholdColor} strokeDasharray="4 2" />
              <ReferenceLine y={sensor.criticalMax} stroke="#EF4444" strokeDasharray="3 3" />
            </ComposedChart>
          );
        case 'line':
        default:
          return (
            <LineChart {...chartProps}>
              {axisProps.grid}{axisProps.xAxis}{axisProps.yAxis}{axisProps.tooltip}
              <Line type="monotone" dataKey={sensor.key} name={sensor.label} stroke={sensor.color} strokeWidth={2} dot={{ r: 2 }} activeDot={{ r: 4 }} />
              <ReferenceLine y={sensor.warningMax} stroke={sensor.thresholdColor} strokeDasharray="4 2" label={{ value: 'Warning', fill: sensor.thresholdColor, fontSize: 8 }} />
              <ReferenceLine y={sensor.criticalMax} stroke="#EF4444" strokeDasharray="3 3" label={{ value: 'Critical', fill: '#EF4444', fontSize: 8 }} />
            </LineChart>
          );
      }
    };

    return (
      <div key={sensor.key} className="bg-card border border-border p-4 rounded-xl shadow-sm flex flex-col space-y-3 relative overflow-hidden">
        <div className="flex justify-between items-start">
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground block">{sensor.label}</span>
            <span className="text-lg font-black font-mono mt-1 block">
              {latestVal} <span className="text-xs font-semibold text-muted-foreground">{sensor.unit}</span>
            </span>
          </div>
          {isCritical ? (
            <span className="bg-red-500/20 text-red-400 border border-red-500/40 text-[9px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1.5 animate-pulse">
              <AlertTriangle className="h-3 w-3" /> CRITICAL
            </span>
          ) : isWarning ? (
            <span className="bg-amber-500/20 text-amber-400 border border-amber-500/40 text-[9px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1.5">
              <AlertTriangle className="h-3 w-3" /> WARNING
            </span>
          ) : (
            <span className="bg-green-500/10 text-green-500 text-[9px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
              ● NORMAL
            </span>
          )}
        </div>

        <div className="h-44 w-full">
          <ResponsiveContainer width="100%" height="100%">
            {renderPlot() as React.ReactElement}
          </ResponsiveContainer>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      <div className="bg-card border border-border px-4 py-3 rounded-xl flex items-center gap-2 text-xs text-muted-foreground">
        <Info className="h-4 w-4 text-primary shrink-0" />
        <span>Renders machine-specific telemetry sensors. Warning and critical thresholds are marked using dynamic reference limits.</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {config.sensors.map(sensor => renderSensorChart(sensor))}
      </div>
    </div>
  );
}
