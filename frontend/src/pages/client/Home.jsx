import { Link } from "react-router-dom";
import { Button } from "semantic-ui-react";

export function Home() {
  return (
    <div className="home">
      <h1>Tienda Online</h1>
      <p>Frontend en React conectado a la API de Django.</p>
      <div>
        <Button as={Link} to="/login" primary content="Iniciar Sesión" />
        <Button as={Link} to="/register" content="Registrarme" />
      </div>
    </div>
  );
}
