#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import fetch from "node-fetch";

const ENGLAND_LOCATIONS = [
  { name: "London", lat: 51.5074, lon: -0.1278 },
  { name: "Birmingham", lat: 52.4862, lon: -1.8904 },
  { name: "Manchester", lat: 53.4808, lon: -2.2426 },
  { name: "Leeds", lat: 53.8008, lon: -1.5491 },
  { name: "Sheffield", lat: 53.3811, lon: -1.4701 },
  { name: "Bristol", lat: 51.4545, lon: -2.5879 },
  { name: "Liverpool", lat: 53.4084, lon: -2.9916 },
  { name: "Newcastle", lat: 54.9783, lon: -1.6178 },
  { name: "Nottingham", lat: 52.9548, lon: -1.1581 },
  { name: "Southampton", lat: 50.9097, lon: -1.4044 },
  { name: "Brighton", lat: 50.8229, lon: -0.1363 },
  { name: "Cambridge", lat: 52.2053, lon: 0.1218 },
  { name: "Oxford", lat: 51.752, lon: -1.2577 },
  { name: "Exeter", lat: 50.7184, lon: -3.5339 },
  { name: "Norwich", lat: 52.6309, lon: 1.2974 },
  { name: "Penzance", lat: 50.1188, lon: -5.537 },
  { name: "York", lat: 53.9599, lon: -1.0873 },
  { name: "Carlisle", lat: 54.8951, lon: -2.9382 },
  { name: "Bournemouth", lat: 50.7192, lon: -1.8808 },
  { name: "Ipswich", lat: 52.0567, lon: 1.1482 },
];

async function fetchTemperatures() {
  const lats = ENGLAND_LOCATIONS.map((l) => l.lat).join(",");
  const lons = ENGLAND_LOCATIONS.map((l) => l.lon).join(",");

  const url =
    `https://api.open-meteo.com/v1/forecast?` +
    `latitude=${lats}&longitude=${lons}` +
    `&current=temperature_2m,apparent_temperature,weather_code` +
    `&wind_speed_unit=mph&temperature_unit=celsius`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Weather API error: ${response.status} ${response.statusText}`);
  }
  const data = await response.json();

  // API returns array when multiple locations requested
  const results = Array.isArray(data) ? data : [data];

  return ENGLAND_LOCATIONS.map((loc, i) => ({
    name: loc.name,
    temperature: results[i].current.temperature_2m,
    feelsLike: results[i].current.apparent_temperature,
    weatherCode: results[i].current.weather_code,
    unit: results[i].current_units.temperature_2m,
  }));
}

function weatherDescription(code) {
  if (code === 0) return "Clear sky";
  if (code === 1) return "Mainly clear";
  if (code === 2) return "Partly cloudy";
  if (code === 3) return "Overcast";
  if (code <= 49) return "Foggy";
  if (code <= 59) return "Drizzle";
  if (code <= 69) return "Rain";
  if (code <= 79) return "Snow";
  if (code <= 82) return "Rain showers";
  if (code <= 86) return "Snow showers";
  if (code <= 99) return "Thunderstorm";
  return "Unknown";
}

const server = new McpServer({
  name: "hottest-place-england",
  version: "1.0.0",
});

server.tool(
  "get_hottest_place",
  "Find the hottest place in England right now, with current temperatures for all monitored locations",
  {
    top_n: z
      .number()
      .int()
      .min(1)
      .max(20)
      .optional()
      .describe("Return the top N hottest places (default: 1)"),
  },
  async ({ top_n = 1 }) => {
    const locations = await fetchTemperatures();
    const sorted = [...locations].sort((a, b) => b.temperature - a.temperature);
    const topLocations = sorted.slice(0, top_n);

    const hottest = topLocations[0];
    let text =
      top_n === 1
        ? `The hottest place in England right now is **${hottest.name}** at **${hottest.temperature}${hottest.unit}** (feels like ${hottest.feelsLike}${hottest.unit}). Conditions: ${weatherDescription(hottest.weatherCode)}.\n`
        : `Top ${top_n} hottest places in England right now:\n`;

    if (top_n > 1) {
      topLocations.forEach((loc, i) => {
        text += `${i + 1}. ${loc.name}: ${loc.temperature}${loc.unit} (feels like ${loc.feelsLike}${loc.unit}) — ${weatherDescription(loc.weatherCode)}\n`;
      });
    }

    return { content: [{ type: "text", text }] };
  }
);

server.tool(
  "get_england_temperatures",
  "Get current temperatures for all monitored locations in England, sorted hottest to coldest",
  {},
  async () => {
    const locations = await fetchTemperatures();
    const sorted = [...locations].sort((a, b) => b.temperature - a.temperature);

    const unit = sorted[0].unit;
    let text = `Current temperatures across England (hottest to coldest):\n\n`;
    sorted.forEach((loc, i) => {
      text += `${String(i + 1).padStart(2)}. ${loc.name.padEnd(14)} ${String(loc.temperature).padStart(5)}${unit}  (feels like ${loc.feelsLike}${unit})  ${weatherDescription(loc.weatherCode)}\n`;
    });

    return { content: [{ type: "text", text }] };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
