'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, Play, CheckSquare, CheckCircle, AlertTriangle } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '../../lib/utils';

export interface WorkOrder {
  id: string;
  order_number: string;
  pipe_diameter_mm: number;
  pressure_class: string;
  quantity_meters: number;
  produced_meters: number;
  machine_id: string;
  shift: string;
  status: 'draft' | 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'delayed';
  priority: 'low' | 'medium' | 'high' | 'critical';
  planned_start: string;
  planned_end: string;
  quality_result?: string;
}

interface WorkOrderCardProps {
  order: WorkOrder;
  onAction?: () => void;
  actionText?: string;
  actionIcon?: React.ReactNode;
}

const PRIORITY_CONFIG = {
  critical: { label: 'CRITICAL', className: 'bg-red-500/20 text-red-400 border border-red-500/40', dot: 'bg-red-500 animate-pulse' },
  high:     { label: 'HIGH',     className: 'bg-orange-500/20 text-orange-400 border border-orange-500/40', dot: 'bg-orange-500' },
  medium:   { label: 'MED',      className: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/40', dot: 'bg-yellow-500' },
  low:      { label: 'LOW',      className: 'bg-slate-500/20 text-slate-400 border border-slate-500/40', dot: 'bg-slate-500' },
};

const STATUS_PROGRESS = { draft: 0, scheduled: 0, in_progress: null, quality_check: 95, completed: 100, cancelled: 0, delayed: 0 };

export function WorkOrderCard({ order, onAction, actionText, actionIcon }: WorkOrderCardProps) {
  const priority = PRIORITY_CONFIG[order.priority] || PRIORITY_CONFIG.medium;
  const progressPct = order.status === 'in_progress'
    ? Math.round((order.produced_meters / order.quantity_meters) * 100)
    : STATUS_PROGRESS[order.status] ?? 0;

  // Format dates safely
  const formatTime = (dateStr: string) => {
    try {
      return format(new Date(dateStr), 'dd MMM HH:mm');
    } catch (e) {
      return dateStr;
    }
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.97 }}
      transition={{ duration: 0.2 }}
      className="bg-card rounded-xl border border-border p-4 hover:border-primary/40 hover:shadow-lg transition-all duration-200 space-y-3"
    >
      {/* Header Row: WO Number + Priority */}
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] text-muted-foreground">{order.order_number}</span>
        <span className={cn('text-[9px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1.5', priority.className)}>
          <span className={cn('w-1.5 h-1.5 rounded-full', priority.dot)} />
          {priority.label}
        </span>
      </div>

      {/* Product Information */}
      <div>
        <p className="text-xs font-bold text-foreground leading-tight">
          uPVC Pipe {order.pipe_diameter_mm}mm {order.pressure_class || 'PN10'}
        </p>
        <p className="text-[10px] text-muted-foreground mt-0.5 font-mono">
          {order.quantity_meters.toLocaleString()}m · Machine: {String(order.machine_id).slice(-4).toUpperCase()} · {order.shift.toUpperCase()} Shift
        </p>
      </div>

      {/* Date Range Row */}
      <div className="flex items-center gap-1 text-[10px] text-muted-foreground bg-muted/30 px-2 py-1 rounded-md">
        <Calendar className="h-3 w-3 shrink-0" />
        <span>{formatTime(order.planned_start)}</span>
        <span className="text-border">→</span>
        <span>{formatTime(order.planned_end)}</span>
      </div>

      {/* Progress Bar (for in_progress & completed) */}
      {(order.status === 'in_progress' || order.status === 'completed') && (
        <div className="space-y-1 bg-muted/20 p-2 rounded-lg">
          <div className="flex justify-between text-[9px] text-muted-foreground">
            <span>Production Progress</span>
            <span className="font-mono font-bold text-foreground">{progressPct}%</span>
          </div>
          <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <motion.div
              className={cn(
                'h-full rounded-full',
                progressPct >= 90 ? 'bg-green-500' : progressPct >= 60 ? 'bg-blue-500' : 'bg-orange-500'
              )}
              initial={{ width: 0 }}
              animate={{ width: `${progressPct}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
          <div className="text-[9px] text-muted-foreground font-mono flex justify-between">
            <span>Produced: {order.produced_meters.toLocaleString()}m</span>
            <span>Target: {order.quantity_meters.toLocaleString()}m</span>
          </div>
        </div>
      )}

      {/* Action Trigger Button */}
      {onAction && actionText && (
        <button
          onClick={onAction}
          className="w-full bg-primary/10 hover:bg-primary/20 text-primary text-[10px] py-1.5 rounded-lg font-semibold transition-colors flex items-center justify-center gap-1 border border-primary/20"
        >
          {actionIcon}
          {actionText}
        </button>
      )}

      {/* Status Indicators for Completed or Other Statuses */}
      {order.status === 'completed' && (
        <div className="w-full bg-green-500/10 border border-green-500/20 text-green-500 text-[10px] py-1 px-2 rounded-lg font-semibold flex items-center justify-center gap-1">
          <CheckCircle className="h-3.5 w-3.5" />
          <span>Batch Passed Inspection</span>
        </div>
      )}
    </motion.div>
  );
}
