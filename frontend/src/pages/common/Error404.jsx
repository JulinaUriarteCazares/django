import { Link } from "react-router-dom";

export function Error404() {
  return (
    <div className="home">
      <h1>Error 404</h1>
      <p>La página que buscas no existe.</p>
      <Link to="/">Volver al inicio</Link>
    </div>
  );
}
