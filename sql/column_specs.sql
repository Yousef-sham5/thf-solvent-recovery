-- Calculating Distillate flow rate: D = recovery * F * z_THF / x_azeotrope
-- Calculating Bottom flow rate: B = F - D 

-- Constants: recovery = 0.9, F = 2000kmol/h, z_THF = 0.06

DROP VIEW IF EXISTS column_specs;
CREATE VIEW column_specs AS
  SELECT p_bar, x_azeotrope, 
      (ROUND((0.9 * 120 / x_azeotrope), 3)) AS D_kmol_h, 
      (ROUND(2000 - (0.9 * 120 / x_azeotrope), 3)) AS B_kmol_h
  FROM azeotropes
  WHERE property_package = 'Wilson'
  ORDER by p_bar;

