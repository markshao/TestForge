import axios from 'axios';

export const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

export interface StepState {
  index: number;
  content: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  screenshot?: string;
}

export interface Task {
  id: string;
  name: string;
  description?: string;
  yaml_content: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'error';
  created_at: string;
  updated_at: string;
  steps?: StepState[];
}

export interface TaskSummary {
  id: string;
  name: string;
  status: Task['status'];
  created_at: string;
}

export interface TaskCreate {
  name: string;
  description?: string;
  yaml_content?: string;
  testcase_file?: string;
}

export interface ExecutionLog {
  timestamp: string;
  level: string;
  message: string;
}

export interface CellExecutionState {
  id: string;
  status: string;
  code: string;
  output?: string;
}

export interface ExecutionState {
  task_id: string;
  status: Task['status'];
  logs: ExecutionLog[];
  cells: CellExecutionState[];
}

export const tasksApi = {
  list: async () => {
    const { data } = await api.get<TaskSummary[]>('/tasks');
    return data;
  },
  
  create: async (task: TaskCreate) => {
    const { data } = await api.post<Task>('/tasks', task);
    return data;
  },
  
  get: async (id: string) => {
    const { data } = await api.get<Task>(`/tasks/${id}`);
    return data;
  },
  
  delete: async (id: string) => {
    await api.delete(`/tasks/${id}`);
  },
  
  start: async (id: string) => {
    await api.post(`/tasks/${id}/start`);
  },
  
  getExecution: async (id: string) => {
    const { data } = await api.get<ExecutionState>(`/tasks/${id}/execution`);
    return data;
  }
};
