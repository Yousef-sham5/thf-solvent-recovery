DROP TABLE IF EXISTS azeotropes;

CREATE TABLE azeotropes (
  property_package TEXT NOT NULL,
  p_bar REAL NOT NULL,
  x_azeotrope REAL NOT NULL CHECK (x_azeotrope > 0 AND x_azeotrope < 1),
  T_azeotrope REAL NOT NULL,
  PRIMARY KEY (property_package, p_bar)
);