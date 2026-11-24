-- Quality Control (QC) queries (failures, THF balance, recovery):

-- cases where columns didn't converge
SELECT run_id, p_bar, reflux, n_stages, error_msg FROM runs
WHERE converged = 0;


-- reflux ratio = 0.25
SELECT run_id, p_bar, n_stages, converged, (D_kmol_h * x_thf_top / 120) AS recovery, thf_err_rel
FROM runs
WHERE reflux = 0.25
ORDER BY p_bar, n_stages;


-- how many runs have a THF balance error above 1e-9, and the worst one
SELECT COUNT(*) AS thf_err_above_1e9, MAX(thf_err_rel) AS worst
FROM runs
WHERE converged = 1 AND thf_err_rel > 1e-9;


-- recovery range at each reflux ratio (converged runs only)
SELECT reflux, COUNT(*) AS n,
	MIN(D_kmol_h * x_thf_top / 120) AS min_recovery,
	MAX(D_kmol_h * x_thf_top / 120) AS max_recovery
FROM runs
WHERE converged = 1
GROUP BY reflux
ORDER BY reflux;


-- Results queries:

-- 1. good runs only
SELECT p_bar, reflux, n_stages FROM runs
WHERE converged = 1 AND thf_err_rel < 1e-3
ORDER BY p_bar, reflux, n_stages;


-- 2. best top THF per pressure, next to x_azeotrope
SELECT r.p_bar, MAX(r.x_thf_top) AS max_x_thf_top, a.x_azeotrope, (MAX(r.x_thf_top) / a.x_azeotrope) AS ratio
FROM runs AS r
INNER JOIN azeotropes AS a ON r.p_bar = a.p_bar
WHERE r.converged = 1 
	AND r.thf_err_rel < 1e-3 
	AND a.property_package = 'Wilson'
GROUP BY r.p_bar, a.x_azeotrope
ORDER BY r.p_bar;


-- 3. smallest grid RR per (P, N) reaching 99.9% of the plateau
WITH plateau AS (
    SELECT p_bar, x_thf_top AS x_plateau
    FROM runs
	WHERE n_stages = 25 
        AND reflux = 12 
        AND converged = 1
)
SELECT r.p_bar, r.n_stages, MIN(r.reflux) AS min_reflux, r.q_reb_kw
FROM runs AS r
JOIN plateau AS p ON r.p_bar = p.p_bar
WHERE r.x_thf_top >= 0.999 * p.x_plateau
	AND r.converged = 1
	AND r.thf_err_rel < 1e-3
GROUP BY r.p_bar, r.n_stages
ORDER BY r.n_stages, r.p_bar;


-- 4. lowest reboiler duty that meets the target, per pressure
WITH plateau AS (
    SELECT p_bar, x_thf_top AS x_plateau
    FROM runs
	WHERE n_stages = 25 
        AND reflux = 12 
        AND converged = 1
)
SELECT r.p_bar, MIN(r.q_reb_kw) AS min_q_reb_kw, r.n_stages, r.reflux
FROM runs AS r
JOIN plateau AS p ON r.p_bar = p.p_bar
WHERE r.x_thf_top >= 0.999 * p.x_plateau
	AND r.converged = 1
	AND r.thf_err_rel < 1e-3
GROUP BY r.p_bar
ORDER BY r.p_bar;



