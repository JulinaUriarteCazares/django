import { Login } from "../pages/common";
import { useAuth } from "../hooks/useAuth";

export function AdminLayout({ children }) {
  const { auth } = useAuth();

  if (!auth) return <Login />;

  return <div>{children}</div>;
}
