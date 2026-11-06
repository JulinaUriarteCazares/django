import { useEffect, useState } from "react";
import { Button, Message } from "semantic-ui-react";
import { CITY, getWeatherApi } from "../api/weather";

export function WeatherWidget() {
  const [weather, setWeather] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadWeather = async () => {
    setLoading(true);
    setError(null);

    try {
      setWeather(await getWeatherApi());
    } catch {
      setError("No se pudo obtener el clima. Intenta de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWeather();
  }, []);

  return (
    <section className="card weather">
      <h2>Clima en {CITY.name}</h2>
      <p className="card__source">API de terceros: Open-Meteo</p>

      {error && <Message negative content={error} />}

      {weather && !error && (
        <>
          <div className="weather__temperature">{weather.temperature} °C</div>
          <div className="weather__description">{weather.description}</div>
          <div className="weather__details">
            Humedad {weather.humidity}% · Viento {weather.wind} km/h
          </div>
        </>
      )}

      <Button
        content="Actualizar"
        size="small"
        loading={loading}
        disabled={loading}
        onClick={loadWeather}
      />
    </section>
  );
}
