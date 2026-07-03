export type SensorKey = 'temperature' | 'vibration' | 'pressure' | 'speed' | 'power' | 'flow_rate' | 'cut_force' | 'dwell_time';

export interface SensorConfig {
  key: SensorKey;
  label: string;
  unit: string;
  chartType: 'line' | 'area' | 'bar' | 'composed';
  normalMin: number;
  normalMax: number;
  warningMax: number;
  criticalMax: number;
  color: string;
  thresholdColor: string;
}

export interface MachineOEEConfig {
  machineCode: string;
  machineType: 'extruder' | 'cooling' | 'cutter';
  sensors: SensorConfig[];
  availabilityTarget: number;   // %
  performanceTarget: number;    // %
  qualityTarget: number;        // %
  oeeTarget: number;            // %
}

export const MACHINE_TELEMETRY_CONFIGS: Record<string, MachineOEEConfig> = {
  // EXTRUDERS — 6 machines, each with different diameter = different operating ranges
  'EXT-01': {
    machineCode: 'EXT-01', machineType: 'extruder',
    availabilityTarget: 92, performanceTarget: 88, qualityTarget: 97, oeeTarget: 79,
    sensors: [
      { key: 'temperature', label: 'Melt Temperature', unit: '°C', chartType: 'area', normalMin: 175, normalMax: 215, warningMax: 235, criticalMax: 260, color: '#EF4444', thresholdColor: '#F97316' },
      { key: 'speed', label: 'Screw Speed', unit: 'RPM', chartType: 'line', normalMin: 22, normalMax: 38, warningMax: 45, criticalMax: 52, color: '#0EA5E9', thresholdColor: '#F59E0B' },
      { key: 'pressure', label: 'Die Pressure', unit: 'bar', chartType: 'composed', normalMin: 110, normalMax: 160, warningMax: 185, criticalMax: 210, color: '#8B5CF6', thresholdColor: '#EF4444' },
      { key: 'vibration', label: 'Drive Vibration', unit: 'mm/s', chartType: 'bar', normalMin: 0, normalMax: 3.5, warningMax: 5.5, criticalMax: 8.0, color: '#22C55E', thresholdColor: '#F97316' },
    ],
  },
  'EXT-02': {
    machineCode: 'EXT-02', machineType: 'extruder',
    availabilityTarget: 90, performanceTarget: 85, qualityTarget: 96, oeeTarget: 74,
    sensors: [
      { key: 'temperature', label: 'Zone 3 Temp', unit: '°C', chartType: 'line', normalMin: 170, normalMax: 210, warningMax: 230, criticalMax: 255, color: '#EF4444', thresholdColor: '#F97316' },
      { key: 'pressure', label: 'Barrel Pressure', unit: 'bar', chartType: 'area', normalMin: 120, normalMax: 170, warningMax: 200, criticalMax: 230, color: '#A855F7', thresholdColor: '#EF4444' },
      { key: 'speed', label: 'Line Speed', unit: 'm/min', chartType: 'composed', normalMin: 3.0, normalMax: 6.5, warningMax: 8.0, criticalMax: 10.0, color: '#0EA5E9', thresholdColor: '#F59E0B' },
      { key: 'power', label: 'Drive Power Draw', unit: 'kW', chartType: 'bar', normalMin: 55, normalMax: 95, warningMax: 110, criticalMax: 130, color: '#F97316', thresholdColor: '#EF4444' },
    ],
  },
  'EXT-03': {
    machineCode: 'EXT-03', machineType: 'extruder',
    availabilityTarget: 88, performanceTarget: 82, qualityTarget: 98, oeeTarget: 71,
    sensors: [
      { key: 'temperature', label: 'Compound Temp (Zone 4)', unit: '°C', chartType: 'composed', normalMin: 180, normalMax: 225, warningMax: 245, criticalMax: 270, color: '#EF4444', thresholdColor: '#F97316' },
      { key: 'vibration', label: 'Gearbox Vibration', unit: 'mm/s', chartType: 'area', normalMin: 0, normalMax: 4.0, warningMax: 6.5, criticalMax: 9.5, color: '#22C55E', thresholdColor: '#EF4444' },
      { key: 'power', label: 'Total Consumed Power', unit: 'kW', chartType: 'line', normalMin: 75, normalMax: 115, warningMax: 130, criticalMax: 155, color: '#F97316', thresholdColor: '#EF4444' },
      { key: 'speed', label: 'Output Rate', unit: 'kg/hr', chartType: 'bar', normalMin: 40, normalMax: 80, warningMax: 90, criticalMax: 100, color: '#0EA5E9', thresholdColor: '#F59E0B' },
    ],
  },
  'EXT-04': {
    machineCode: 'EXT-04', machineType: 'extruder',
    availabilityTarget: 94, performanceTarget: 90, qualityTarget: 97, oeeTarget: 82,
    sensors: [
      { key: 'pressure', label: 'Head Pressure', unit: 'bar', chartType: 'area', normalMin: 140, normalMax: 200, warningMax: 225, criticalMax: 250, color: '#8B5CF6', thresholdColor: '#EF4444' },
      { key: 'temperature', label: 'Melt Zone Temp', unit: '°C', chartType: 'composed', normalMin: 185, normalMax: 230, warningMax: 250, criticalMax: 275, color: '#EF4444', thresholdColor: '#F97316' },
      { key: 'vibration', label: 'Frame Vibration', unit: 'mm/s', chartType: 'line', normalMin: 0, normalMax: 5.0, warningMax: 8.0, criticalMax: 12.0, color: '#22C55E', thresholdColor: '#F97316' },
      { key: 'power', label: 'Drive Power', unit: 'kW', chartType: 'bar', normalMin: 90, normalMax: 140, warningMax: 160, criticalMax: 190, color: '#F97316', thresholdColor: '#EF4444' },
    ],
  },
  'EXT-05': {
    machineCode: 'EXT-05', machineType: 'extruder',
    availabilityTarget: 91, performanceTarget: 87, qualityTarget: 96, oeeTarget: 76,
    sensors: [
      { key: 'temperature', label: 'Die Head Temp', unit: '°C', chartType: 'line', normalMin: 190, normalMax: 235, warningMax: 255, criticalMax: 280, color: '#EF4444', thresholdColor: '#F97316' },
      { key: 'speed', label: 'Screw Speed', unit: 'RPM', chartType: 'area', normalMin: 18, normalMax: 32, warningMax: 40, criticalMax: 48, color: '#0EA5E9', thresholdColor: '#F59E0B' },
      { key: 'pressure', label: 'System Pressure', unit: 'bar', chartType: 'bar', normalMin: 155, normalMax: 210, warningMax: 240, criticalMax: 270, color: '#A855F7', thresholdColor: '#EF4444' },
      { key: 'power', label: 'Electricity (kWh)', unit: 'kWh', chartType: 'composed', normalMin: 100, normalMax: 160, warningMax: 185, criticalMax: 210, color: '#F97316', thresholdColor: '#EF4444' },
    ],
  },
  'EXT-06': {
    machineCode: 'EXT-06', machineType: 'extruder',
    availabilityTarget: 89, performanceTarget: 83, qualityTarget: 95, oeeTarget: 70,
    sensors: [
      { key: 'vibration', label: 'Critical Vibration (Drive)', unit: 'mm/s', chartType: 'area', normalMin: 0, normalMax: 4.5, warningMax: 7.0, criticalMax: 10.5, color: '#EF4444', thresholdColor: '#DC2626' },
      { key: 'temperature', label: 'Cylinder Temperature', unit: '°C', chartType: 'composed', normalMin: 195, normalMax: 240, warningMax: 260, criticalMax: 285, color: '#F97316', thresholdColor: '#EF4444' },
      { key: 'pressure', label: 'Melt Pressure', unit: 'bar', chartType: 'line', normalMin: 160, normalMax: 215, warningMax: 245, criticalMax: 275, color: '#8B5CF6', thresholdColor: '#EF4444' },
      { key: 'power', label: 'Total Power', unit: 'kW', chartType: 'bar', normalMin: 95, normalMax: 155, warningMax: 175, criticalMax: 200, color: '#F59E0B', thresholdColor: '#EF4444' },
    ],
  },
  // COOLING TANKS
  'COOL-01': {
    machineCode: 'COOL-01', machineType: 'cooling',
    availabilityTarget: 97, performanceTarget: 94, qualityTarget: 99, oeeTarget: 90,
    sensors: [
      { key: 'temperature', label: 'Water Temperature', unit: '°C', chartType: 'line', normalMin: 12, normalMax: 28, warningMax: 35, criticalMax: 45, color: '#06B6D4', thresholdColor: '#F59E0B' },
      { key: 'flow_rate', label: 'Water Flow Rate', unit: 'L/min', chartType: 'area', normalMin: 80, normalMax: 150, warningMax: 45, criticalMax: 30, color: '#0EA5E9', thresholdColor: '#EF4444' },
      { key: 'pressure', label: 'Tank Pressure', unit: 'bar', chartType: 'bar', normalMin: 0.5, normalMax: 2.5, warningMax: 3.5, criticalMax: 5.0, color: '#22C55E', thresholdColor: '#F97316' },
      { key: 'vibration', label: 'Pump Vibration', unit: 'mm/s', chartType: 'composed', normalMin: 0, normalMax: 2.0, warningMax: 3.5, criticalMax: 5.5, color: '#A855F7', thresholdColor: '#EF4444' },
    ],
  },
  'COOL-02': {
    machineCode: 'COOL-02', machineType: 'cooling',
    availabilityTarget: 96, performanceTarget: 93, qualityTarget: 99, oeeTarget: 89,
    sensors: [
      { key: 'flow_rate', label: 'Coolant Flow', unit: 'L/min', chartType: 'composed', normalMin: 90, normalMax: 160, warningMax: 50, criticalMax: 30, color: '#0EA5E9', thresholdColor: '#EF4444' },
      { key: 'temperature', label: 'Inlet / Outlet Temp', unit: '°C', chartType: 'area', normalMin: 10, normalMax: 30, warningMax: 38, criticalMax: 48, color: '#06B6D4', thresholdColor: '#F97316' },
      { key: 'power', label: 'Chiller Power', unit: 'kW', chartType: 'line', normalMin: 5, normalMax: 18, warningMax: 25, criticalMax: 32, color: '#F59E0B', thresholdColor: '#EF4444' },
      { key: 'vibration', label: 'Circulation Pump', unit: 'mm/s', chartType: 'bar', normalMin: 0, normalMax: 1.8, warningMax: 3.0, criticalMax: 4.5, color: '#22C55E', thresholdColor: '#F97316' },
    ],
  },
  'COOL-03': {
    machineCode: 'COOL-03', machineType: 'cooling',
    availabilityTarget: 98, performanceTarget: 95, qualityTarget: 99, oeeTarget: 92,
    sensors: [
      { key: 'temperature', label: 'Bath Temperature', unit: '°C', chartType: 'area', normalMin: 8, normalMax: 25, warningMax: 33, criticalMax: 42, color: '#06B6D4', thresholdColor: '#F59E0B' },
      { key: 'dwell_time', label: 'Pipe Dwell Time', unit: 'sec/m', chartType: 'line', normalMin: 30, normalMax: 60, warningMax: 75, criticalMax: 90, color: '#10B981', thresholdColor: '#F97316' },
      { key: 'flow_rate', label: 'Flow Rate', unit: 'L/min', chartType: 'bar', normalMin: 70, normalMax: 140, warningMax: 40, criticalMax: 20, color: '#0EA5E9', thresholdColor: '#EF4444' },
      { key: 'pressure', label: 'Water Pressure', unit: 'bar', chartType: 'composed', normalMin: 0.5, normalMax: 2.0, warningMax: 3.0, criticalMax: 4.5, color: '#8B5CF6', thresholdColor: '#EF4444' },
    ],
  },
  // CUTTERS
  'CUT-01': {
    machineCode: 'CUT-01', machineType: 'cutter',
    availabilityTarget: 95, performanceTarget: 91, qualityTarget: 99, oeeTarget: 86,
    sensors: [
      { key: 'cut_force', label: 'Blade Cut Force', unit: 'N', chartType: 'composed', normalMin: 200, normalMax: 600, warningMax: 800, criticalMax: 1000, color: '#EF4444', thresholdColor: '#DC2626' },
      { key: 'speed', label: 'Blade Speed', unit: 'm/min', chartType: 'area', normalMin: 40, normalMax: 80, warningMax: 95, criticalMax: 110, color: '#0EA5E9', thresholdColor: '#F59E0B' },
      { key: 'vibration', label: 'Chassis Vibration', unit: 'mm/s', chartType: 'line', normalMin: 0, normalMax: 3.0, warningMax: 5.0, criticalMax: 7.5, color: '#22C55E', thresholdColor: '#F97316' },
      { key: 'power', label: 'Motor Power', unit: 'kW', chartType: 'bar', normalMin: 3, normalMax: 12, warningMax: 16, criticalMax: 22, color: '#F97316', thresholdColor: '#EF4444' },
    ],
  },
  'CUT-02': {
    machineCode: 'CUT-02', machineType: 'cutter',
    availabilityTarget: 96, performanceTarget: 92, qualityTarget: 99, oeeTarget: 88,
    sensors: [
      { key: 'speed', label: 'Haul-Off Speed', unit: 'm/min', chartType: 'composed', normalMin: 3.0, normalMax: 7.0, warningMax: 9.0, criticalMax: 11.0, color: '#0EA5E9', thresholdColor: '#F59E0B' },
      { key: 'vibration', label: 'Frame Vibration', unit: 'mm/s', chartType: 'bar', normalMin: 0, normalMax: 2.5, warningMax: 4.5, criticalMax: 7.0, color: '#22C55E', thresholdColor: '#F97316' },
      { key: 'cut_force', label: 'Cutting Force', unit: 'N', chartType: 'line', normalMin: 180, normalMax: 550, warningMax: 750, criticalMax: 950, color: '#EF4444', thresholdColor: '#DC2626' },
      { key: 'power', label: 'Power Consumption', unit: 'kW', chartType: 'composed', normalMin: 2, normalMax: 10, warningMax: 14, criticalMax: 20, color: '#F59E0B', thresholdColor: '#EF4444' },
    ],
  },
  'CUT-03': {
    machineCode: 'CUT-03', machineType: 'cutter',
    availabilityTarget: 94, performanceTarget: 90, qualityTarget: 98, oeeTarget: 83,
    sensors: [
      { key: 'vibration', label: 'Vibration Level', unit: 'mm/s', chartType: 'line', normalMin: 0, normalMax: 3.2, warningMax: 5.5, criticalMax: 8.5, color: '#22C55E', thresholdColor: '#F97316' },
      { key: 'cut_force', label: 'Blade Pressure', unit: 'N', chartType: 'area', normalMin: 160, normalMax: 520, warningMax: 720, criticalMax: 920, color: '#EF4444', thresholdColor: '#DC2626' },
      { key: 'temperature', label: 'Blade Tip Temperature', unit: '°C', chartType: 'bar', normalMin: 30, normalMax: 70, warningMax: 90, criticalMax: 115, color: '#F97316', thresholdColor: '#EF4444' },
      { key: 'power', label: 'Drive Power', unit: 'kW', chartType: 'composed', normalMin: 2, normalMax: 11, warningMax: 15, criticalMax: 21, color: '#8B5CF6', thresholdColor: '#EF4444' },
    ],
  },
  'CUT-04': {
    machineCode: 'CUT-04', machineType: 'cutter',
    availabilityTarget: 97, performanceTarget: 93, qualityTarget: 99, oeeTarget: 89,
    sensors: [
      { key: 'speed', label: 'Cut Cycle Speed', unit: 'cuts/min', chartType: 'area', normalMin: 8, normalMax: 18, warningMax: 22, criticalMax: 28, color: '#0EA5E9', thresholdColor: '#F97316' },
      { key: 'cut_force', label: 'Saw Force', unit: 'N', chartType: 'area', normalMin: 150, normalMax: 500, warningMax: 700, criticalMax: 900, color: '#EF4444', thresholdColor: '#DC2626' },
      { key: 'vibration', label: 'Saw Vibration', unit: 'mm/s', chartType: 'bar', normalMin: 0, normalMax: 2.8, warningMax: 4.8, criticalMax: 7.2, color: '#22C55E', thresholdColor: '#EF4444' },
      { key: 'power', label: 'Total Power (kWh)', unit: 'kWh', chartType: 'line', normalMin: 1.5, normalMax: 8.0, warningMax: 11.0, criticalMax: 15.0, color: '#F59E0B', thresholdColor: '#EF4444' },
    ],
  },
};
