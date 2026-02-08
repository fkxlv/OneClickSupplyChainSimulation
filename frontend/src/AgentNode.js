import React from 'react';
import { Handle, Position } from 'reactflow';
import { Settings, Activity } from 'lucide-react';

const AgentNode = ({ data }) => {
  return (
    <div className="window-node">
      {/* Шапка окошка */}
      <div className="window-header">
        <div className="window-dots">
          <span className="dot red"></span>
          <span className="dot yellow"></span>
          <span className="dot green"></span>
        </div>
        <span className="window-title">{data.role || 'Agent'}</span>
        <Settings size={10} className="window-icon" />
      </div>
      
      {/* Содержимое окошка */}
      <div className="window-content">
        <div className="agent-label">{data.label}</div>
        {data.status && (
          <div className="agent-status">
            <Activity size={12} className="spin-icon" />
            <span>{data.status}</span>
          </div>
        )}
      </div>

      {/* Точки подключения линий */}
      <Handle type="target" position={Position.Top} className="handle-style" />
      <Handle type="source" position={Position.Bottom} className="handle-style" />
    </div>
  );
};

export default AgentNode;