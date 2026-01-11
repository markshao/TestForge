import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TaskListPage } from "./pages/TaskListPage";
import { TaskDetailPage } from "./pages/TaskDetailPage";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/tasks" replace />} />
          <Route path="/tasks" element={<TaskListPage />} />
          <Route path="/tasks/:id" element={<TaskDetailPage />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App
