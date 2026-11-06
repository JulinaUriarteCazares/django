const API_URL = import.meta.env.VITE_BASE_API_URL;

async function request(path, params) {
  try {
    return await fetch(`${API_URL}${path}`, params);
  } catch {
    throw new Error("No se pudo conectar con el servidor");
  }
}

export async function loginApi(formData) {
  const response = await request("/api/v1/auth/token/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData),
  });

  if (response.status !== 200) {
    throw new Error("Correo o contraseña incorrecta");
  }

  return response.json();
}

export async function registerApi(formData) {
  const response = await request("/api/v1/auth/register/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData),
  });

  if (response.status !== 201) {
    const errors = await response.json().catch(() => ({}));
    const message = Object.values(errors).flat().join(" ");
    throw new Error(message || "No se puede crear el usuario");
  }

  return response.json();
}

export async function getMeApi(token) {
  const response = await request("/api/v1/auth/me/", {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (response.status !== 200) {
    throw new Error("La sesión no es válida");
  }

  return response.json();
}
