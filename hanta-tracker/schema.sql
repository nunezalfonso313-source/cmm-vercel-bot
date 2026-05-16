CREATE TABLE IF NOT EXISTS cases (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  country TEXT NOT NULL,
  region TEXT NOT NULL,
  lat REAL,
  lon REAL,
  cases_total INTEGER DEFAULT 0,
  deaths INTEGER DEFAULT 0,
  reported_date TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now'))
);

INSERT INTO cases (country, region, lat, lon, cases_total, deaths, reported_date) VALUES
('Argentina', 'Neuquén', -38.9516, -68.0591, 14, 3, '2026-05-01'),
('Chile', 'Aysén', -45.5752, -72.0662, 8, 1, '2026-05-03'),
('Brasil', 'São Paulo', -23.5505, -46.6333, 5, 0, '2026-05-05'),
('Panama', 'Panamá Oeste', 8.9936, -79.5197, 22, 7, '2026-04-28'),
('USA', 'New Mexico', 34.5199, -105.8701, 3, 0, '2026-05-07');
