// API de terceros gratuita y sin clave: https://open-meteo.com/
const WEATHER_URL = "https://api.open-meteo.com/v1/forecast";

export const CITY = {
  name: "Ciudad de México",
  latitude: 19.43,
  longitude: -99.13,
};

// Códigos WMO que usa Open-Meteo.
function describeWeather(code) {
  if (code === 0) return "Despejado";
  if (code === 1) return "Mayormente despejado";
  if (code === 2) return "Parcialmente nublado";
  if (code === 3) return "Nublado";
  if (code <= 48) return "Niebla";
  if (code <= 57) return "Llovizna";
  if (code <= 67) return "Lluvia";
  if (code <= 77) return "Nieve";
  if (code <= 82) return "Chubascos";
  if (code <= 86) return "Chubascos de nieve";
  return "Tormenta";
}

export async function getWeatherApi() {
  const params = new URLSearchParams({
    latitude: CITY.latitude,
    longitude: CITY.longitude,
    current: "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
    timezone: "auto",
  });

  const response = await fetch(`${WEATHER_URL}?${params}`);

  if (!response.ok) {
    throw new Error("La API del clima no respondió correctamente");
  }

  const { current } = await response.json();

  return {
    temperature: current.temperature_2m,
    humidity: current.relative_humidity_2m,
    wind: current.wind_speed_10m,
    description: describeWeather(current.weather_code),
    time: current.time,
  };
}
