const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-Auth-Token'
};

export default {
  async scheduled(event, env, ctx) {
    console.log("Iniciando tarea programada");
  },

  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/$/, "");
    const method = request.method;

    if (method === 'OPTIONS') return new Response(null, { headers: CORS });

    // ── HANTA ──────────────────────────────────────────
    if (path === '/api/hanta' || path === '/api/hanta/cases') {
      try {
        const { results } = await env.DB.prepare('SELECT * FROM cases ORDER BY reported_date DESC').all();
        return Response.json({ cases: results, total: results.length }, { headers: CORS });
      } catch (e) {
        return Response.json({ error: e.message }, { status: 500, headers: CORS });
      }
    }

    // ── SISMOS ─────────────────────────────────────────
    if (path === '/api/sismos') {
      try {
        const limit = url.searchParams.get('limit') || 200;
        const minmag = url.searchParams.get('minmag') || 4.0;
        const days = parseInt(url.searchParams.get('days') || 1);
        const minlat = url.searchParams.get('minlat') || '';
        const maxlat = url.searchParams.get('maxlat') || '';
        const minlon = url.searchParams.get('minlon') || '';
        const maxlon = url.searchParams.get('maxlon') || '';
        const endtime = new Date().toISOString().split('T')[0];
        const starttime = new Date(Date.now() - days*86400000).toISOString().split('T')[0];
        let usgsUrl = `https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=${limit}&minmagnitude=${minmag}&orderby=time&starttime=${starttime}&endtime=${endtime}`;
        if (minlat) usgsUrl += `&minlatitude=${minlat}&maxlatitude=${maxlat}&minlongitude=${minlon}&maxlongitude=${maxlon}`;
        const res = await fetch(usgsUrl);
        const data = await res.json();
        const features = (data.features||[]).map(f => ({
          id: f.id, place: f.properties.place, mag: f.properties.mag,
          time: f.properties.time, lat: f.geometry.coordinates[1],
          lon: f.geometry.coordinates[0], depth: f.geometry.coordinates[2]
        }));
        return Response.json({ features, total: features.length, last_updated: new Date().toISOString() }, { headers: CORS });
      } catch (e) {
        return Response.json({ features: [], error: e.message }, { headers: CORS });
      }
    }

    // ── VUELOS ─────────────────────────────────────────
    if (path === '/api/vuelos') {
      try {
        const lat = url.searchParams.get('lat') || '23.63';
        const lon = url.searchParams.get('lon') || '-102.55';
        const dist = url.searchParams.get('dist') || '800';
        const res = await fetch(`https://api.adsb.lol/v2/lat/${lat}/lon/${lon}/dist/${dist}`);
        const data = await res.json();
        const flights = (data.ac||[]).filter(a=>a.lat&&a.lon).map(a=>({
          icao: a.hex||'', callsign: (a.flight||'').trim()||'N/A', country: a.r||'?',
          lat: a.lat, lon: a.lon, altitude: a.alt_baro||0,
          velocity: Math.round(a.gs||0), heading: a.track||0,
          on_ground: a.alt_baro==='ground'
        }));
        return Response.json({ flights, total: flights.length, last_updated: new Date().toISOString() }, { headers: CORS });
      } catch (e) {
        return Response.json({ flights: [], error: e.message }, { headers: CORS });
      }
    }

    // ── ASTEROIDES ─────────────────────────────────────
    if (path === '/api/asteroides') {
      try {
        const today = new Date().toISOString().split('T')[0];
        const res = await fetch(`https://api.nasa.gov/neo/rest/v1/feed?start_date=${today}&end_date=${today}&api_key=DEMO_KEY`);
        const data = await res.json();
        const raw = Object.values(data.near_earth_objects||{}).flat();
        const asteroids = raw.map(a => ({
          id: a.id, name: a.name,
          diameter_km: (a.estimated_diameter.kilometers.estimated_diameter_min + a.estimated_diameter.kilometers.estimated_diameter_max) / 2,
          hazardous: a.is_potentially_hazardous_asteroid,
          miss_distance_km: parseFloat(a.close_approach_data[0]?.miss_distance?.kilometers||0),
          velocity_kmh: parseFloat(a.close_approach_data[0]?.relative_velocity?.kilometers_per_hour||0)
        })).sort((a,b) => a.miss_distance_km - b.miss_distance_km);
        return Response.json({ asteroids, total: asteroids.length, last_updated: new Date().toISOString() }, { headers: CORS });
      } catch (e) {
        return Response.json({ asteroids: [], error: e.message }, { headers: CORS });
      }
    }

    return new Response('Not Found', { status: 404, headers: CORS });
  }
};