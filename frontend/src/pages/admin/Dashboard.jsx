import { Button } from "semantic-ui-react";
import { WeatherWidget } from "../../components";
import { useAuth } from "../../hooks/useAuth";

export function Dashboard() {
  const { logout, auth } = useAuth();
  const user = auth.me;

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <div>
          <h1>Dashboard</h1>
          <p>
            Bienvenido, <strong>{user.first_name || user.username}</strong>
          </p>
        </div>
        <Button content="Cerrar Sesión" onClick={logout} />
      </header>

      <div className="dashboard__grid">
        <section className="card">
          <h2>Mi cuenta</h2>
          <p className="card__source">Web service propio: /api/auth/me/</p>
          <dl className="user-data">
            <div>
              <dt>ID</dt>
              <dd>{user.id}</dd>
            </div>
            <div>
              <dt>Usuario</dt>
              <dd>{user.username}</dd>
            </div>
            <div>
              <dt>Correo</dt>
              <dd>{user.email}</dd>
            </div>
          </dl>
        </section>

        <WeatherWidget />
      </div>
    </div>
  );
}
