import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { Terminal, Cpu, HardDrive, Activity } from 'lucide-react';
import './AgentNode.css';

export default memo(({ data }) => {
  return (
    <div className="agent-window">
      {/* Шапка окна (Title Bar) */}
      <div className="window-header">
        <div className="window-controls">
          <span className="control close"></span>
          <span className="control minimize"></span>
          <span className="control maximize"></span>
        </div>
        <div className="window-title">
          <Terminal size={12} />
          <span>{data.role || 'Agent'}</span>
        </div>
      </div>

      {/* Содержимое окна */}
      <div className="window-body">
        <div className="agent-info">
          <div className="agent-name">{data.label}</div>
          <div className="agent-status-line">
            <Activity size={12} className="pulse-icon" />
            <span>{data.status || 'Initializing...'}</span>
          </div>
        </div>

        <div className="agent-terminal-output">
          <p className="typing-text">{'>'} Checking protocols...</p>
          <p className="typing-text">{'>'} {data.role} active</p>
        </div>
      </div>

      {/* Точки подключения (Handles) */}
      <Handle type="target" position={Position.Top} className="custom-handle" />
      <Handle type="source" position={Position.Bottom} className="custom-handle" />
    </div>
  );
});