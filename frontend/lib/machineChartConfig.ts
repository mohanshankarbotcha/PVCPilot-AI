import { AreaChart, BarChart, LineChart, ComposedChart, RadarChart } from 'recharts';

export type ChartType =
  | 'area_planned_vs_actual'
  | 'bar_output_by_shift'
  | 'line_speed_trend'
  | 'composed_throughput_efficiency'
  | 'bar_diameter_breakdown'
  | 'area_cumulative_output'
  | 'bar_shift_comparison'
  | 'line_cycle_time';

export interface MachineChartConfig {
  machineCode: string;
  machineName: string;
  primaryChartType: ChartType;
  secondaryChartType: ChartType;
  primaryTitle: string;
  secondaryTitle: string;
  primaryColor: string;
  secondaryColor: string;
  unit: string;
  yAxisLabel: string;
}

export const MACHINE_CHART_CONFIGS: Record<string, MachineChartConfig> = {
  'EXT-01': {
    machineCode: 'EXT-01',
    machineName: 'Twin Screw Extruder 01 (63mm)',
    primaryChartType: 'area_planned_vs_actual',
    secondaryChartType: 'bar_shift_comparison',
    primaryTitle: 'Planned vs Actual Output — 63mm Pipes',
    secondaryTitle: 'Output Comparison by Shift (Last 7 Days)',
    primaryColor: '#0EA5E9',
    secondaryColor: '#22C55E',
    unit: 'meters',
    yAxisLabel: 'Meters Produced',
  },
  'EXT-02': {
    machineCode: 'EXT-02',
    machineName: 'Twin Screw Extruder 02 (90mm)',
    primaryChartType: 'bar_output_by_shift',
    secondaryChartType: 'line_speed_trend',
    primaryTitle: 'Daily Output by Shift — 90mm Pipes',
    secondaryTitle: 'Extrusion Speed Trend (RPM over 30 Days)',
    primaryColor: '#F97316',
    secondaryColor: '#A855F7',
    unit: 'meters',
    yAxisLabel: 'Meters per Shift',
  },
  'EXT-03': {
    machineCode: 'EXT-03',
    machineName: 'Twin Screw Extruder 03 (110mm)',
    primaryChartType: 'composed_throughput_efficiency',
    secondaryChartType: 'area_cumulative_output',
    primaryTitle: 'Throughput & Efficiency — 110mm Production',
    secondaryTitle: 'Cumulative Output This Month',
    primaryColor: '#22C55E',
    secondaryColor: '#0EA5E9',
    unit: 'tons',
    yAxisLabel: 'Tons Produced',
  },
  'EXT-04': {
    machineCode: 'EXT-04',
    machineName: 'Twin Screw Extruder 04 (160mm)',
    primaryChartType: 'bar_diameter_breakdown',
    secondaryChartType: 'line_cycle_time',
    primaryTitle: 'Output by Diameter Class — EXT-04',
    secondaryTitle: 'Average Cycle Time per Batch (Minutes)',
    primaryColor: '#F59E0B',
    secondaryColor: '#EF4444',
    unit: 'meters',
    yAxisLabel: 'Output Volume',
  },
  'EXT-05': {
    machineCode: 'EXT-05',
    machineName: 'Twin Screw Extruder 05 (200mm)',
    primaryChartType: 'area_planned_vs_actual',
    secondaryChartType: 'composed_throughput_efficiency',
    primaryTitle: 'Planned vs Actual — 200mm Heavy Duty Pipes',
    secondaryTitle: 'Throughput Rate vs Target Efficiency',
    primaryColor: '#3B82F6',
    secondaryColor: '#10B981',
    unit: 'meters',
    yAxisLabel: 'Meters Produced',
  },
  'EXT-06': {
    machineCode: 'EXT-06',
    machineName: 'Twin Screw Extruder 06 (250mm)',
    primaryChartType: 'bar_shift_comparison',
    secondaryChartType: 'line_speed_trend',
    primaryTitle: 'Shift-wise Output — 250mm Large Bore Pipes',
    secondaryTitle: 'Production Speed vs Nominal (Last 14 Days)',
    primaryColor: '#8B5CF6',
    secondaryColor: '#F97316',
    unit: 'meters',
    yAxisLabel: 'Meters per Shift',
  },
  'COOL-01': {
    machineCode: 'COOL-01',
    machineName: 'Cooling Tank 01',
    primaryChartType: 'line_speed_trend',
    secondaryChartType: 'area_cumulative_output',
    primaryTitle: 'Water Temperature Profile (°C) — Tank 01',
    secondaryTitle: 'Pipes Cooled — Cumulative Count',
    primaryColor: '#06B6D4',
    secondaryColor: '#22C55E',
    unit: '°C',
    yAxisLabel: 'Temperature (°C)',
  },
  'COOL-02': {
    machineCode: 'COOL-02',
    machineName: 'Cooling Tank 02',
    primaryChartType: 'composed_throughput_efficiency',
    secondaryChartType: 'bar_shift_comparison',
    primaryTitle: 'Flow Rate vs Cooling Efficiency — Tank 02',
    secondaryTitle: 'Throughput per Shift (Meters)',
    primaryColor: '#0EA5E9',
    secondaryColor: '#6366F1',
    unit: 'L/min',
    yAxisLabel: 'Flow Rate',
  },
  'COOL-03': {
    machineCode: 'COOL-03',
    machineName: 'Cooling Tank 03',
    primaryChartType: 'line_cycle_time',
    secondaryChartType: 'area_planned_vs_actual',
    primaryTitle: 'Dwell Time Trend (Seconds per Meter)',
    secondaryTitle: 'Planned vs Actual Pipe Throughput',
    primaryColor: '#14B8A6',
    secondaryColor: '#F59E0B',
    unit: 'sec/m',
    yAxisLabel: 'Dwell Time',
  },
  'CUT-01': {
    machineCode: 'CUT-01',
    machineName: 'Pipe Cutter 01',
    primaryChartType: 'bar_output_by_shift',
    secondaryChartType: 'line_cycle_time',
    primaryTitle: 'Cuts per Shift — Cutter 01',
    secondaryTitle: 'Average Cut Time (ms) — Precision Trend',
    primaryColor: '#EF4444',
    secondaryColor: '#F97316',
    unit: 'cuts',
    yAxisLabel: 'Number of Cuts',
  },
  'CUT-02': {
    machineCode: 'CUT-02',
    machineName: 'Pipe Cutter 02',
    primaryChartType: 'bar_diameter_breakdown',
    secondaryChartType: 'bar_shift_comparison',
    primaryTitle: 'Cuts by Pipe Diameter — Cutter 02',
    secondaryTitle: 'Shift Performance Comparison (Last Week)',
    primaryColor: '#F59E0B',
    secondaryColor: '#22C55E',
    unit: 'cuts',
    yAxisLabel: 'Cut Count',
  },
  'CUT-03': {
    machineCode: 'CUT-03',
    machineName: 'Pipe Cutter 03',
    primaryChartType: 'composed_throughput_efficiency',
    secondaryChartType: 'area_cumulative_output',
    primaryTitle: 'Cut Rate vs Rejection Rate — Cutter 03',
    secondaryTitle: 'Cumulative Good Cuts This Week',
    primaryColor: '#8B5CF6',
    secondaryColor: '#10B981',
    unit: 'cuts',
    yAxisLabel: 'Cut Volume',
  },
  'CUT-04': {
    machineCode: 'CUT-04',
    machineName: 'Pipe Cutter 04',
    primaryChartType: 'line_speed_trend',
    secondaryChartType: 'bar_output_by_shift',
    primaryTitle: 'Blade Speed Trend — Cutter 04 (m/min)',
    secondaryTitle: 'Output Volume per Shift',
    primaryColor: '#06B6D4',
    secondaryColor: '#F97316',
    unit: 'm/min',
    yAxisLabel: 'Blade Speed',
  },
};

export const CHART_TYPE_LABELS: Record<ChartType, string> = {
  area_planned_vs_actual: 'Area Chart — Planned vs Actual',
  bar_output_by_shift: 'Bar Chart — Output by Shift',
  line_speed_trend: 'Line Chart — Speed Trend',
  composed_throughput_efficiency: 'Combo Chart — Throughput & Efficiency',
  bar_diameter_breakdown: 'Bar Chart — Diameter Breakdown',
  area_cumulative_output: 'Area Chart — Cumulative Output',
  bar_shift_comparison: 'Grouped Bar — Shift Comparison',
  line_cycle_time: 'Line Chart — Cycle Time',
};
