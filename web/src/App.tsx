import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { TaskListPage } from "./pages/TaskListPage";
import { TaskDetailPage } from "./pages/TaskDetailPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/tasks" replace />} />
        <Route path="/tasks" element={<TaskListPage />} />
        <Route path="/tasks/:id" element={<TaskDetailPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App
