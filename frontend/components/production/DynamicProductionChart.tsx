'use client';

import React from 'react';
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line,
  ComposedChart, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import { MACHINE_CHART_CONFIGS, ChartType } from '../../lib/machineChartConfig';
import type { MachineProductionData } from '../../types/production.types';

interface Props {
  machineCode: string;
  data: MachineProductionData[];
  chartType: ChartType;
  title: string;
  primaryColor: string;
  secondaryColor: string;
  unit: string;
  yAxisLabel: string;
}

const CustomTooltip = ({ active, payload, label, unit }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-zinc-900/95 border border-zinc-800 rounded-lg shadow-xl p-3 text-xs text-white">
        <p className="font-semibold mb-2">{label}</p>
        {payload.map((entry: any, i: number) => (
          <p key={i} style={{ color: entry.color }} className="flex justify-between gap-4">
            <span>{entry.name}:</span>
            <span className="font-mono font-bold">
              {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value} {unit}
            </span>
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export function DynamicProductionChart({
  machineCode, data, chartType, title, primaryColor, secondaryColor, unit, yAxisLabel,
}: Props) {
  const chartProps = {
    data,
    margin: { top: 10, right: 20, left: 10, bottom: 5 },
  };

  const axisProps = {
    xAxis: <XAxis dataKey="date" tick={{ fontSize: 10, fill: 'currentColor' }} className="text-muted-foreground" />,
    yAxis: <YAxis tick={{ fontSize: 10, fill: 'currentColor' }} className="text-muted-foreground" label={{ value: yAxisLabel, angle: -90, position: 'insideLeft', style: { fontSize: 9, fill: 'currentColor' } }} />,
    grid: <CartesianGrid strokeDasharray="3 3" className="stroke-zinc-800" opacity={0.3} />,
    tooltip: <Tooltip content={<CustomTooltip unit={unit} />} />,
    legend: <Legend wrapperStyle={{ fontSize: 10 }} />,
  };

  const renderChart = () => {
    switch (chartType) {
      case 'area_planned_vs_actual':
        return (
          <AreaChart {...chartProps}>
            {axisProps.grid}{axisProps.xAxis}{axisProps.yAxis}{axisProps.tooltip}{axisProps.legend}
            <defs>
              <linearGradient id={`grad-planned-${machineCode}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={secondaryColor} stopOpacity={0.2} />
                <stop offset="95%" stopColor={secondaryColor} stopOpacity={0.01} />
              </linearGradient>
              <linearGradient id={`grad-actual-${machineCode}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={primaryColor} stopOpacity={0.3} />
                <stop offset="95%" stopColor={primaryColor} stopOpacity={0.01} />
              </linearGradient>
            </defs>
            <Area type="monotone" dataKey="planned" name="Planned" stroke={secondaryColor} fill={`url(#grad-planned-${machineCode})`} strokeDasharray="4 2" strokeWidth={1.5} />
            <Area type="monotone" dataKey="actual" name="Actual" stroke={primaryColor} fill={`url(#grad-actual-${machineCode})`} strokeWidth={2} />
          </AreaChart>
        );

      case 'bar_output_by_shift':
        return (
          <BarChart {...chartProps}>
            {axisProps.grid}{axisProps.xAxis}{axisProps.yAxis}{axisProps.tooltip}{axisProps.legend}
            <Bar dataKey="morning" name="Morning Shift" fill={primaryColor} radius={[4, 4, 0, 0]} maxBarSize={30} />
            <Bar dataKey="afternoon" name="Afternoon Shift" fill={secondaryColor} radius={[4, 4, 0, 0]} maxBarSize={30} />
            <Bar dataKey="night" name="Night Shift" fill="#A855F7" radius={[4, 4, 0, 0]} maxBarSize={30} />
          </BarChart>
        );

      case 'line_speed_trend':
        return (
          <LineChart {...chartProps}>
            {axisProps.grid}{axisProps.xAxis}{axisProps.yAxis}{axisProps.tooltip}{axisProps.legend}
            <ReferenceLine y={data[0]?.nominal} stroke="#F59E0B" strokeDasharray="6 3" label={{ value: 'Nominal', position: 'right', fontSize: 8, fill: '#F59E0B' }} />
            <Line type="monotone" dataKey="actual" name="Actual Speed" stroke={primaryColor} strokeWidth={2} dot={{ r: 2, fill: primaryColor }} activeDot={{ r: 4 }} />
            <Line type="monotone" dataKey="target" name="Target" stroke={secondaryColor} strokeWidth={1.5} strokeDasharray="5 3" dot={false} />
          </LineChart>
        );

      case 'composed_throughput_efficiency':
        return (
          <ComposedChart {...chartProps}>
            {axisProps.grid}{axisProps.xAxis}{axisProps.yAxis}{axisProps.tooltip}{axisProps.legend}
            <Bar dataKey="throughput" name="Throughput" fill={primaryColor} radius={[4, 4, 0, 0]} maxBarSize={25} opacity={0.8} />
            <Line type="monotone" dataKey="efficiency" name="Efficiency %" stroke={secondaryColor} strokeWidth={2} yAxisId="right" dot={{ r: 2 }} />
            <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10, fill: 'currentColor' }} tickFormatter={(v) => `${v}%`} />
          </ComposedChart>
        );

      case 'bar_diameter_breakdown':
        return (
          <BarChart {...chartProps} layout="vertical">
            {axisProps.grid}
            <XAxis type="number" tick={{ fontSize: 10, fill: 'currentColor' }} />
            <YAxis type="category" dataKey="diameter" tick={{ fontSize: 10, fill: 'currentColor' }} width={55} />
            {axisProps.tooltip}{axisProps.legend}
            <Bar dataKey="quantity" name="Output (m)" fill={primaryColor} radius={[0, 4, 4, 0]} />
            <Bar dataKey="target" name="Target (m)" fill={secondaryColor} radius={[0, 4, 4, 0]} opacity={0.4} />
          </BarChart>
        );

      case 'area_cumulative_output':
        return (
          <AreaChart {...chartProps}>
            {axisProps.grid}{axisProps.xAxis}{axisProps.yAxis}{axisProps.tooltip}{axisProps.legend}
            <defs>
              <linearGradient id={`grad-cumulative-${machineCode}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={primaryColor} stopOpacity={0.4} />
                <stop offset="95%" stopColor={primaryColor} stopOpacity={0.01} />
              </linearGradient>
            </defs>
            <Area type="monotone" dataKey="cumulative" name="Cumulative Output" stroke={primaryColor} fill={`url(#grad-cumulative-${machineCode})`} strokeWidth={2} />
            <Line type="monotone" dataKey="target_cumulative" name="Target Cumulative" stroke={secondaryColor} strokeWidth={1.5} strokeDasharray="6 3" dot={false} />
          </AreaChart>
        );

      case 'bar_shift_comparison':
        return (
          <BarChart {...chartProps}>
            {axisProps.grid}{axisProps.xAxis}{axisProps.yAxis}{axisProps.tooltip}{axisProps.legend}
            <Bar dataKey="thisWeek" name="This Week" fill={primaryColor} radius={[4, 4, 0, 0]} maxBarSize={25} />
            <Bar dataKey="lastWeek" name="Last Week" fill={secondaryColor} radius={[4, 4, 0, 0]} maxBarSize={25} opacity={0.6} />
          </BarChart>
        );

      case 'line_cycle_time':
        return (
          <LineChart {...chartProps}>
            {axisProps.grid}{axisProps.xAxis}{axisProps.yAxis}{axisProps.tooltip}{axisProps.legend}
            <ReferenceLine y={data[0]?.standard} stroke="#EF4444" strokeDasharray="4 2" label={{ value: 'Standard', position: 'right', fontSize: 8, fill: '#EF4444' }} />
            <Line type="monotone" dataKey="cycleTime" name="Cycle Time" stroke={primaryColor} strokeWidth={2} dot={{ r: 2, fill: primaryColor }} activeDot={{ r: 4 }} />
            <Line type="monotone" dataKey="movingAvg" name="7-Day Avg" stroke={secondaryColor} strokeWidth={1.5} strokeDasharray="5 3" dot={false} />
          </LineChart>
        );

      default:
        return null;
    }
  };

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={`${machineCode}-${chartType}`}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.2, ease: 'easeOut' }}
        className="w-full"
      >
        <p className="text-[11px] font-semibold text-muted-foreground mb-3">{title}</p>
        <ResponsiveContainer width="100%" height={200}>
          {renderChart() as React.ReactElement}
        </ResponsiveContainer>
      </motion.div>
    </AnimatePresence>
  );
}
