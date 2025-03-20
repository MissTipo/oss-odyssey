// router.tsx
import { createBrowserRouter } from "react-router-dom";
import HomePage from "./pages/home";
import AuthPage from "./pages/auth";
import DashboardPage from "./pages/dashboard";
import IssuesPage from "./pages/issues";
import WorkspacePage from "./pages/workspace";

const router = createBrowserRouter([
  { path: "/", element: <HomePage /> },
  { path: "/auth", element: <AuthPage /> },
  { path: "/dashboard", element: <DashboardPage /> },
  { path: "/issues", element: <IssuesPage /> },
  { path: "/workspace", element: <WorkspacePage /> },
]);

export default router;

