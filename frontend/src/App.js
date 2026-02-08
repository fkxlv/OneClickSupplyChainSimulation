import React, { useState, useCallback } from 'react';
import ReactFlow, { Background, Controls, useNodesState, useEdgesState } from 'reactflow';
import { Play, Activity, Terminal, Box } from 'lucide-react';
// УДАЛЕНО: import { io } from "socket.io-client"; 
import 'reactflow/dist/style.css';
import './App.css';
import AgentNode from './AgentNode';

const nodeTypes = { agent: AgentNode };

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [intent, setIntent] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [logs, setLogs] = useState([]);

  const addLog = (msg) => {
    setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev].slice(0, 5));
  };

  // Функция для имитации задержки (чтобы граф рос постепенно)
  const delay = (ms) => new Promise(res => setTimeout(res, ms));

  const handleExecute = async () => {
    // ===== PLANNER =====
    updateAgentState("Planner", prev => ({
      ...prev,
      status: "running",
      steps: [],
      output: null
    }));

    const planner = runPlanner(inputData);
    let plannerResult = null;

    while (true) {
      const { value, done } = await planner.next();

      if (done) {
        plannerResult = value;
        break;
      }

      updateAgentState("Planner", prev => ({
        ...prev,
        steps: [
          ...prev.steps,
          {
            timestamp: new Date().toISOString(),
            action: value.action,
            details: value.details
          }
        ]
      }));
    }

    updateAgentState("Planner", prev => ({
      ...prev,
      status: "completed",
      output: plannerResult
    }));

    // ===== SOURCING =====
    updateAgentState("Sourcing", prev => ({
      ...prev,
      status: "running",
      steps: [],
      output: null
    }));

    const sourcing = runSourcing(plannerResult);
    let sourcingResult = null;

    while (true) {
      const { value, done } = await sourcing.next();

      if (done) {
        sourcingResult = value;
        break;
      }

      updateAgentState("Sourcing", prev => ({
        ...prev,
        steps: [
          ...prev.steps,
          {
            timestamp: new Date().toISOString(),
            action: value.action,
            details: value.details
          }
        ]
      }));
    }

    updateAgentState("Sourcing", prev => ({
      ...prev,
      status: "completed",
      output: sourcingResult
    }));

    // ===== EXECUTOR =====
    updateAgentState("Executor", prev => ({
      ...prev,
      status: "running",
      steps: [],
      output: null
    }));

    const executor = runExecutor(sourcingResult);
    let executorResult = null;

    while (true) {
      const { value, done } = await executor.next();

      if (done) {
        executorResult = value;
        break;
      }

      updateAgentState("Executor", prev => ({
        ...prev,
        steps: [
          ...prev.steps,
          {
            timestamp: new Date().toISOString(),
            action: value.action,
            details: value.details
          }
        ]
      }));
    }

    updateAgentState("Executor", prev => ({
      ...prev,
      status: "completed",
      output: executorResult
    }));
  };



  return (
    <div className="app-viewport">
      <aside className="planner-side-panel">
        <h2 className="planner-header"><Box size={24} /> AI Planner</h2>
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
              placeholder="Input a prompt"
              disabled={isProcessing}
            />
            <button onClick={handleExecute} disabled={isProcessing}>
              {isProcessing ? <Activity className="spin" size={18} /> : <Play size={18} />}
              <span>Go</span>
            </button>
          </div>
        </header>

        <section className="graph-frame">
          <ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} fitView>
            <Background color="#1a1a2e" gap={20} />
            <Controls />
          </ReactFlow>
        </section>
      </main>
    </div>
  );
}