import { useState, useEffect, createContext } from "react";
import { setToken, getToken, removeToken } from "../api/token";
import { useUser } from "../hooks/useUser";

// 1. Crear el contexto
export const AuthContext = createContext({
  auth: undefined,
  login: () => null,
  logout: () => null,
});

// 2. Crear el provider
export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(undefined);
  const { getMe } = useUser();

  const logout = () => {
    removeToken();
    setAuth(null);
  };

  const login = async (token) => {
    setToken(token);

    try {
      const me = await getMe(token);
      setAuth({ token, me });
    } catch (error) {
      // Token caducado o inválido: se limpia para no quedar en una sesión rota.
      logout();
      throw error;
    }
  };

  // Al recargar la página se recupera la sesión desde localStorage.
  useEffect(() => {
    const token = getToken();

    if (token) {
      login(token).catch(() => {});
    } else {
      setAuth(null);
    }
  }, []);

  const valueContext = { auth, login, logout };

  // Mientras se comprueba el token no se pinta nada: evita el flash del login.
  if (auth === undefined) return null;

  return (
    <AuthContext.Provider value={valueContext}>{children}</AuthContext.Provider>
  );
}
