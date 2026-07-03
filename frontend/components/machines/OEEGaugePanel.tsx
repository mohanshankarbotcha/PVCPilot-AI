'use client';

import React from 'react';
import { RadialBarChart, RadialBar, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

interface OEEGaugePanelProps {
  availability: number;
  performance: number;
  quality: number;
  oee: number;
  targets: { availability: number; performance: number; quality: number; oee: number };
}

function GaugeCard({ label, value, target, color }: { label: string; value: number; target: number; color: string; }) {
  const isAboveTarget = value >= target;
  return (
    <div className="flex flex-col items-center gap-2 p-4 rounded-xl bg-muted/30 border border-border">
      <div className="relative w-24 h-24">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart cx="50%" cy="50%" innerRadius="65%" outerRadius="95%" startAngle={210} endAngle={-30} data={[{ value }]}>
            <RadialBar background dataKey="value" cornerRadius={6} fill={color} />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className="text-base font-bold font-mono text-foreground"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            {value.toFixed(1)}%
          </motion.span>
        </div>
      </div>
      <div className="text-center">
        <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{label}</p>
        <p className={cn('text-[9px] font-semibold mt-0.5', isAboveTarget ? 'text-green-500' : 'text-red-500')}>
          Target {target}% · {isAboveTarget ? '▲ On Track' : '▼ Below Target'}
        </p>
      </div>
    </div>
  );
}

export function OEEGaugePanel({ availability, performance, quality, oee, targets }: OEEGaugePanelProps) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      <GaugeCard label="Availability" value={availability} target={targets.availability} color="#22C55E" />
      <GaugeCard label="Performance" value={performance} target={targets.performance} color="#0EA5E9" />
      <GaugeCard label="Quality Rate" value={quality} target={targets.quality} color="#A855F7" />
      <GaugeCard label="Total OEE" value={oee} target={targets.oee} color="#F97316" />
    </div>
  );
}
