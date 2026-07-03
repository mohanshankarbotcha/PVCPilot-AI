'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { DynamicProductionChart } from '../production/DynamicProductionChart';
import { MACHINE_CHART_CONFIGS, CHART_TYPE_LABELS } from '../../lib/machineChartConfig';
import { api } from '../../lib/api';

type Period = '1D' | '7D' | '30D' | '90D';

export function ProductionOverview() {
  const [selectedMachine, setSelectedMachine] = useState('EXT-01');
  const [period, setPeriod] = useState<Period>('30D');

  const config = MACHINE_CHART_CONFIGS[selectedMachine];

  // Fetch production chart data from backend
  const { data, isLoading } = useQuery({
    queryKey: ['production-chart', selectedMachine, period],
    queryFn: () =>
      api.get(`/production/chart-data`, { params: { machine: selectedMachine, period } }).then(r => r.data),
    staleTime: 15_000,
  });

  const machineOptions = Object.values(MACHINE_CHART_CONFIGS);

  return (
    <div className="bg-card border border-border p-6 rounded-xl shadow-sm lg:col-span-2 space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-b border-border pb-4">
        <div>
          <h3 className="font-bold text-sm uppercase tracking-wider text-muted-foreground">Production Overview (Meters)</h3>
          {config && (
            <p className="text-[10px] text-muted-foreground mt-0.5 font-mono">
              {config.machineName} · {CHART_TYPE_LABELS[config.primaryChartType]}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {/* Machine Dropdown Selector */}
          <select 
            value={selectedMachine} 
            onChange={(e) => setSelectedMachine(e.target.value)}
            className="bg-background border border-border text-foreground px-3 py-1.5 rounded-lg text-xs font-medium focus:outline-none"
          >
            <optgroup label="Extruders">
              {machineOptions.filter(m => m.machineCode.startsWith('EXT')).map(m => (
                <option key={m.machineCode} value={m.machineCode}>
                  {m.machineCode} - Extruder
                </option>
              ))}
            </optgroup>
            <optgroup label="Cooling & Cutting">
              {machineOptions.filter(m => !m.machineCode.startsWith('EXT')).map(m => (
                <option key={m.machineCode} value={m.machineCode}>
                  {m.machineCode} - {m.machineName.split(' ')[0]}
                </option>
              ))}
            </optgroup>
          </select>

          {/* Period Button Group */}
          <div className="flex bg-muted/60 p-0.5 rounded-lg border border-border">
            {(['1D', '7D', '30D', '90D'] as Period[]).map(p => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`text-[10px] px-2.5 py-1 rounded-md font-semibold transition-all ${
                  period === p
                    ? 'bg-background text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="h-64 w-full flex items-center justify-center text-xs text-muted-foreground font-medium">
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary mr-2" />
          Loading machine metrics...
        </div>
      ) : (
        <div className="space-y-6">
          {/* Primary Chart */}
          {config && (
            <DynamicProductionChart
              machineCode={selectedMachine}
              data={data?.primaryData ?? []}
              chartType={config.primaryChartType}
              title={config.primaryTitle}
              primaryColor={config.primaryColor}
              secondaryColor={config.secondaryColor}
              unit={config.unit}
              yAxisLabel={config.yAxisLabel}
            />
          )}

          {/* Divider line */}
          <div className="border-t border-border/60" />

          {/* Secondary Chart */}
          {config && (
            <DynamicProductionChart
              machineCode={`${selectedMachine}-secondary`}
              data={data?.primaryData ?? []} // using same primaryData for other metrics or data?.secondaryData
              chartType={config.secondaryChartType}
              title={config.secondaryTitle}
              primaryColor={config.secondaryColor}
              secondaryColor={config.primaryColor}
              unit={config.unit}
              yAxisLabel={config.yAxisLabel}
            />
          )}
        </div>
      )}
    </div>
  );
}
