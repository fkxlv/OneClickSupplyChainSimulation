import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, { 
  Background, Controls, useNodesState, useEdgesState 
} from 'reactflow';
import { Play, Activity, Box, MapPin, ClipboardList, Brain, CheckCircle, Terminal } from 'lucide-react';
import { io } from "socket.io-client";
import 'reactflow/dist/style.css';
import './App.css';
import AgentNode from './AgentNode';

// ✅ Определяем вне компонента, чтобы избежать ошибок рендеринга
const nodeTypes = { agent: AgentNode };
const socket = io('http://localhost:5001');

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [intent, setIntent] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [planData, setPlanData] = useState(null);
  const [logs, setLogs] = useState([]);

  const addLog = useCallback((message) => {
    setLogs((prev) => [`[${new Date().toLocaleTimeString()}] ${message}`, ...prev].slice(0, 5));
  }, []);

  useEffect(() => {
    socket.on('graph_update', (event) => {
      if (event.type === 'LOG') addLog(event.message);
    });
    return () => socket.off('graph_update');
  }, [addLog]);

  const fetchPlan = async (userIntent) => {
    try {
      const response = await fetch('http://127.0.0.1:5001/planner/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          intent: userIntent, 
          request_id: `req-${Math.random().toString(36).substr(2, 9)}` 
        })
      });
      return await response.json();
    } catch (error) {
      addLog("Backend connection failed");
      return null;
    }
  };

  const handleExecute = async () => {
    if (!intent) return;
    setIsProcessing(true);
    
    // Сброс графа
    setNodes([{ 
      id: 'orchestrator', 
      type: 'agent', 
      data: { label: '🤖 Orchestrator', role: 'Main Intelligence', status: 'Thinking...' }, 
      position: { x: 250, y: 200 } 
    }]);
    setEdges([]);

    const data = await fetchPlan(intent);
    if (!data) {
      setIsProcessing(false);
      return;
    }
    setPlanData(data);
    addLog(`Plan received: ${data.product}`);

    // Анимация появления узлов
    setTimeout(() => {
      setNodes((nds) => [...nds, {
        id: 'reg_1',
        type: 'agent',
        data: { label: 'Global Registry', role: 'Registry', status: 'Searching...' },
        position: { x: 250, y: 50 },
      }]);
      setEdges((eds) => [...eds, {
        id: 'e1', source: 'orchestrator', target: 'reg_1', animated: true, style: { stroke: '#EC4899' }
      }]);
    }, 1000);

    setTimeout(() => {
      setNodes((nds) => [...nds, {
        id: 'supp_1',
        type: 'agent',
        data: { label: `${data.product} Source`, role: 'Supplier', status: 'Ready' },
        position: { x: 500, y: 200 },
      }]);
      setEdges((eds) => [...eds, {
        id: 'e2', source: 'reg_1', target: 'supp_1', animated: true, style: { stroke: '#F59E0B' }
      }]);
      setIsProcessing(false);
    }, 2500);
  };

  return (
    <div className="app-viewport">
      <aside className="planner-side-panel">
        <div className="planner-header">
          <Brain size={20} color="#8B5CF6" />
          <h2>AI Planner</h2>
        </div>

        {planData ? (
          <div className="plan-content">
            <div className="data-card">
              <div className="card-item"><Box size={16} /> <span>{planData.product}</span></div>
              <div className="card-item"><Activity size={16} /> <span>{planData.quantity} units</span></div>
              <div className="card-item"><MapPin size={16} /> <span>{planData.constraints?.region || 'Berlin'}</span></div>
            </div>
            <div className="checklist-section">
              <h4>Strategy Steps:</h4>
              {planData.checklist?.map((step, i) => (
                <div key={i} className="step-row"><CheckCircle size={14} className="check-icon"/> <span>{step}</span></div>
              ))}
            </div>
          </div>
        ) : (
          <div className="empty-state"><p>Enter your intent to start simulation...</p></div>
        )}

        <div className="mini-logs">
          {logs.map((log, i) => (
            <div key={i} className="log-entry"><Terminal size={10} /> {log}</div>
          ))}
        </div>
      </aside>

      <main className="main-content">
        <header className="top-bar">
          <div className="input-wrapper">
            <input 
              value={intent} 
              onChange={(e) => setIntent(e.target.value)}
              placeholder="Ex: Source 500 units of steel for Berlin..." 
              disabled={isProcessing}
            />
            <button onClick={handleExecute} disabled={isProcessing || !intent}>
              {isProcessing ? <Activity className="spin" size={18} /> : <Play size={18} />}
              <span>{isProcessing ? 'Thinking...' : 'Execute'}</span>
            </button>
          </div>
        </header>

        <section className="graph-frame">
          <ReactFlow 
            nodes={nodes} 
            edges={edges} 
            nodeTypes={nodeTypes} 
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
          >
            <Background color="#1a1a2e" gap={20} />
            <Controls />
          </ReactFlow>
        </section>
      </main>
    </div>
  );
}